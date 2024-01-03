"""Extract pdf text preserving the structural layout of the source PDF
"""

import json
from itertools import groupby
from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple, Union
try:
    # Python 3.8+: https://peps.python.org/pep-0586
    from typing import Literal, TypedDict
except ImportError:
    from typing_extensions import Literal, TypedDict

from ._fonts import Font, TextStateParams
from ._xform_stack import XformStack


class BTGroup(TypedDict):
    """dict describing a line of text rendered within a BT/ET operator pair.
    If multiple text show operations render text on the same line, the text
    will be combined into a single BTGroup dict.

    Keys:
        tx: x coordinate of first character in BTGroup
        ty: y coordinate of first character in BTGroup
        font_height: effective font height
        text: rendered text
        displaced_tx: x coordinate of last character in BTGroup
        flip_sort: -1 if page is upside down, else 1
    """

    tx: float
    ty: float
    font_height: float
    text: str
    displaced_tx: float
    flip_sort: Literal[-1, 1]


def bt_group(tj_op: TextStateParams, rendered_text: str, dispaced_tx: float) -> BTGroup:
    """BTGroup constructed from a TextStateParams instance, rendered text, and
    displaced tx value.

    Args:
        tj_op (TextStateParams): TextStateParams instance
        rendered_text (str): rendered text
        dispaced_tx (float): x coordinate of last character in BTGroup
    """
    return BTGroup(
        tx=tj_op.render_xform[4],
        ty=tj_op.render_xform[5],
        font_height=tj_op.font_height,
        text=rendered_text,
        displaced_tx=dispaced_tx,
        flip_sort=-1 if tj_op.flip_vertical else 1,
    )


def decode_tj(_b: bytes, xform_stack: XformStack) -> TextStateParams:
    """decode a Tj/TJ operator

    Args:
        _b: text bytes
        xform_stack: stack of cm/tm transformations to be applied

    Raises:
        ValueError: if font not set (no Tf operator in incoming pdf content stream)

    Returns:
        TextStateParams: dataclass containing rendered text and state parameters
    """
    if not xform_stack.font:
        raise ValueError("font not set: is PDF missing a Tf operator?")
    try:
        if isinstance(xform_stack.font.encoding, str):
            _text = _b.decode(xform_stack.font.encoding, "surrogatepass")
        else:
            _text = "".join(
                xform_stack.font.encoding[x]
                if x in xform_stack.font.encoding
                else bytes((x,)).decode()
                for x in _b
            )
    except (UnicodeEncodeError, UnicodeDecodeError):
        _text = _b.decode("utf-8", "replace")
    _text = "".join(
        xform_stack.font.char_map[x] if x in xform_stack.font.char_map else x for x in _text
    )
    return xform_stack.text_state_params(_text)


def recurs_to_target_op(
    ops: Iterator[Tuple[List, bytes]],
    xform_stack: XformStack,
    end_target: Literal[b"Q", b"ET"],
    fonts: Dict[str, Font],
    debug=False,
) -> Tuple[List[BTGroup], List[TextStateParams]]:
    """recurse operators between BT/ET and/or q/Q operators managing the xform
    stack and capturing text positioning and rendering data.

    Args:
        ops: iterator of operators in content stream
        xform_stack: stack of cm/tm transformations to be applied
        end_target: Either b"Q" (ends b"q" op) or b"ET" (ends b"BT" op)
        fonts: font dictionary as returned by pdf_fonts.page_fonts()
        debug: Captures all text operator data. Defaults to False.

    Returns:
        tuple: list of BTGroup dicts + list of TextStateParams dataclass instances.
    """
    # 1 entry per line of text rendered within each BT/ET operation.
    bt_groups: List[BTGroup] = []

    # 1 entry per text show operator (Tj/TJ/'/")
    tj_ops: List[TextStateParams] = []

    if end_target == b"Q":
        # add new q level. cm's added at this level will be popped at next b'Q'
        xform_stack.add_q()

    while True:
        try:
            opands, op = next(ops)
        except StopIteration:
            return bt_groups, tj_ops
        if op == end_target:
            if op == b"Q":
                xform_stack.remove_q()
            if op == b"ET":
                if not tj_ops:
                    return bt_groups, tj_ops
                _text = ""
                displaced_tx = tj_ops[0].displaced_tx
                last_ty = tj_ops[0].render_xform[5]
                for _tj in tj_ops:  # ... build text from new Tj operators
                    # if the y position of the text is greater than the font height, assume
                    # the text is on a new line and start a new group
                    if abs(_tj.render_xform[5] - last_ty) > _tj.font_height:
                        if _text.strip():
                            bt_groups.append(bt_group(tj_ops[0], _text, displaced_tx))
                        tj_ops[0] = _tj
                        _text = ""

                    # if the x position of the text is less than the last x position by
                    # more than 5 spaces widths, assume the text order should be flipped
                    # and start a new group
                    if abs(_tj.render_xform[4] - displaced_tx) > _tj.space_tx * 5:
                        if _text.strip():
                            bt_groups.append(bt_group(tj_ops[0], _text, displaced_tx))
                        tj_ops[0] = _tj
                        displaced_tx = _tj.render_xform[4]
                        _text = ""

                    # calculate excess x translation based on ending tx of previous Tj
                    excess_tx = round(_tj.render_xform[4] - displaced_tx, 3)

                    # pdfs sometimes have "placeholder" spaces for variable length date, time,
                    # and page number fields. Continue below prevents these spaces from being
                    # rendered in the output text avoiding extra spaces in datetime and
                    # header/footer page number strings.
                    if _tj.txt == " " and _text.endswith(" ") and excess_tx <= _tj.space_tx:
                        continue

                    if _tj.space_tx > 0.0:
                        new_text = f'{" " * int(excess_tx // (_tj.space_tx))}{_tj.txt}'
                    else:
                        new_text = _tj.txt

                    last_ty = _tj.render_xform[5]
                    _text = f"{_text}{new_text}"
                    displaced_tx = _tj.displaced_tx
                if _text:
                    bt_groups.append(bt_group(tj_ops[0], _text, displaced_tx))
                xform_stack.reset_tm()
            return bt_groups, tj_ops
        if op == b"q":
            bts, tjs = recurs_to_target_op(ops, xform_stack, b"Q", fonts, debug)
            bt_groups.extend(bts)
            tj_ops.extend(tjs)
        elif op == b"cm":
            xform_stack.add_cm(*opands)
        elif op == b"BT":
            bts, tjs = recurs_to_target_op(ops, xform_stack, b"ET", fonts, debug)
            bt_groups.extend(bts)
            tj_ops.extend(tjs)
        elif op == b"Tj":
            tj_ops.append(decode_tj(opands[0], xform_stack))
        elif op == b"TJ":
            _tj = xform_stack.text_state_params()
            for tj_op in opands[0]:
                if isinstance(tj_op, bytes):
                    _tj = decode_tj(tj_op, xform_stack)
                    tj_ops.append(_tj)
                else:
                    xform_stack.add_trm(_tj.displacement_matrix(TD_offset=tj_op))
        elif op == b"'":
            xform_stack.reset_trm()
            xform_stack.add_tm([0, xform_stack.TL])
            tj_ops.append(decode_tj(opands[0], xform_stack))
        elif op == b'"':
            xform_stack.reset_trm()
            _set_state_param(b"Tw", [opands[0]], xform_stack)
            _set_state_param(b"Tc", [opands[1]], xform_stack)
            xform_stack.add_tm([0, xform_stack.TL])
            tj_ops.append(decode_tj(opands[2], xform_stack))
        elif op in (b"Td", b"Tm", b"TD", b"T*"):
            xform_stack.reset_trm()
            if op == b"Tm":
                xform_stack.reset_tm()
            elif op == b"TD":
                _set_state_param(b"TL", [-opands[1]], xform_stack)
            elif op == b"T*":
                opands = [0, -xform_stack.TL]
            xform_stack.add_tm(opands)
        elif op == b"Tf":
            xform_stack.font_size = opands[1]
            xform_stack.font = fonts[opands[0]]
        else:
            _set_state_param(op, opands, xform_stack)


def y_coordinate_groups(
    bt_groups: List[BTGroup], debug_path: Union[Path, None] = None
) -> Dict[int, List[BTGroup]]:
    """group text operations by rendered y coordinate, i.e. the line number

    Args:
        bt_groups: list of dicts as returned by text_show_operations()
        debug_file: full path + filename prefix for debug output. Defaults to None.

    Returns:
        Dict[int, List[BTGroup]]: dict of lists of text rendered by each BT operator
         keyed by y coordinate"""
    ty_groups = {
        ty: sorted(grp, key=lambda x: x["tx"])
        for ty, grp in groupby(
            bt_groups, key=lambda bt_grp: int(bt_grp["ty"] * bt_grp["flip_sort"])
        )
    }
    # combine groups whose y coordinates differ by less than the effective font height
    # (accounts for mixed fonts and other minor oddities)
    last_ty = list(ty_groups)[0]
    last_txs = set(int(_t["tx"]) for _t in ty_groups[last_ty] if _t["text"].strip())
    for ty in list(ty_groups)[1:]:
        fsz = min(ty_groups[_y][0]["font_height"] for _y in (ty, last_ty))
        txs = set(int(_t["tx"]) for _t in ty_groups[ty] if _t["text"].strip())
        # prevent merge if both groups are rendering in the same x position.
        no_text_overlap = not (txs & last_txs)
        offset_less_than_font_height = abs(ty - last_ty) < fsz
        if no_text_overlap and offset_less_than_font_height:
            ty_groups[last_ty] = sorted(
                ty_groups.pop(ty) + ty_groups[last_ty], key=lambda x: x["tx"]
            )
            last_txs |= txs
        else:
            last_ty = ty
            last_txs = txs
    if debug_path:
        debug_path.with_name("bt_groups.json").write_text(
            json.dumps(ty_groups, indent=2, default=str), "utf-8"
        )
    return ty_groups


def _set_state_param(op: bytes, opands: List, xform_stack: XformStack):
    """set text state parameter

    Args:
        op: operator defined in PDF standard 1.7 as bytes
        opands: List of operands for the op as bytes, int or float
        xform_stack: stack of cm/tm transformations currently applied
    """
    if op == b"Tc":
        xform_stack.Tc = opands[0]
    if op == b"Tw":
        xform_stack.Tw = opands[0]
    if op == b"Tz":
        xform_stack.Tz = opands[0]
    if op == b"TL":
        xform_stack.TL = opands[0]
    if op == b"Ts":
        xform_stack.Ts = opands[0]


def text_show_operations(
    ops: Iterator[Tuple[List, bytes]], fonts: Dict[str, Font], debug_path=Union[Path, None]
) -> List[BTGroup]:
    """extract text from BT/ET operator pairs

    Args:
        ops (Iterator[Tuple[List, bytes]]): iterator of operators in content stream
        fonts (Dict[str, Font]): font dictionary
        debug_file (str, optional): full path + filename prefix for debug output.
            Defaults to None.

    Returns:
        List[BTGroup]: list of dicts of text rendered by each BT operator
    """
    x_stack = XformStack()  # transformation stack manager
    debug = bool(debug_path)
    bt_groups: List[BTGroup] = []  # BT operator dict
    tj_debug: List[TextStateParams] = []  # Tj/TJ operator data (debug only)
    try:
        while True:
            opands, op = next(ops)
            if op in (b"BT", b"q"):
                bts, tjs = recurs_to_target_op(
                    ops, x_stack, b"ET" if op == b"BT" else b"Q", fonts, debug
                )
                bt_groups.extend(bts)
                if debug:
                    tj_debug.extend(tjs)
            else:
                _set_state_param(op, opands, x_stack)
    except StopIteration:
        pass

    # left align the data, i.e. decrement all tx values by min(tx)
    min_x = min((x["tx"] for x in bt_groups), default=0.0)
    bt_groups = [
        dict(ogrp, tx=ogrp["tx"] - min_x, displaced_tx=ogrp["displaced_tx"] - min_x)
        for ogrp in sorted(
            bt_groups, key=lambda x: (x["ty"] * x["flip_sort"], -x["tx"]), reverse=True
        )
    ]

    if debug_path:
        debug_path.with_name("bts.json").write_text(
            json.dumps(bt_groups, indent=2, default=str), "utf-8"
        )
        debug_path.with_name("tjs.json").write_text(
            json.dumps(tj_debug, indent=2, default=lambda x: getattr(x, "to_dict", str)(x)),
            "utf-8",
        )
    return bt_groups


def fixed_char_width(bt_groups: List[Dict[str, Any]], scale_weight: float = 1.25) -> float:
    """calculate average character width weighted by the length of the rendered
    text in each sample for conversion to fixed-width layout.

    Args:
        bt_groups (List[Dict[str, Any]]): List of dicts of text rendered by each
            BT operator

    Returns:
        float: fixed character width
    """
    char_widths = []
    for _bt in bt_groups:
        _len = len(_bt["text"]) * scale_weight
        char_widths.append(((_bt["displaced_tx"] - _bt["tx"]) / _len, _len))
    return sum(_w * _l for _w, _l in char_widths) / sum(_l for _, _l in char_widths)


def fixed_width_page(
    ty_groups: Dict[int, List[BTGroup]], char_width: float, space_vertically: bool
) -> str:
    """generate page text from text operations grouped by y coordinate

    Args:
        ty_groups: dict of text show ops as returned by y_coordinate_groups()
        char_width: fixed character width
        space_vertically: include blank lines inferred from y distance + font height.

    Returns:
        str: page text structured as it was rendered in the source PDF.
    """
    lines: List[str] = []
    last_y_coord = 0
    for y_coord, line_data in ty_groups.items():
        if space_vertically and lines:
            blank_lines = int(abs(y_coord - last_y_coord) / line_data[0]["font_height"]) - 1
            lines.extend([""] * blank_lines)
        line = ""
        last_disp = 0.0
        for bt_op in line_data:
            offset = int(bt_op["tx"] // char_width)
            spaces = (offset - len(line)) * (
                round(last_disp + (char_width / 2.0)) < round(bt_op["tx"])
            )
            line = f"{line}{' ' * spaces}{bt_op['text']}"
            last_disp = bt_op["displaced_tx"]
        if line.strip() or lines:
            lines.append("".join(c if ord(c) < 14 or ord(c) > 31 else " " for c in line))
        last_y_coord = y_coord
    return "\n".join(ln.rstrip() for ln in lines if space_vertically or ln.strip())
