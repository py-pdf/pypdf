"""Extract PDF text preserving the layout of the source PDF"""

import sys
from itertools import groupby
from math import ceil
from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple, Union

from ..._utils import logger_warning
from .. import LAYOUT_NEW_BT_GROUP_SPACE_WIDTHS
from ._font import Font
from ._text_state_manager import TextStateManager
from ._text_state_params import TextStateParams

if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict
else:
    from typing_extensions import Literal, TypedDict


class BTGroup(TypedDict):
    """
    Dict describing a line of text rendered within a BT/ET operator pair.
    If multiple text show operations render text on the same line, the text
    will be combined into a single BTGroup dict.

    Keys:
        tx: x coordinate of first character in BTGroup
        ty: y coordinate of first character in BTGroup
        font_size: nominal font size
        font_height: effective font height
        text: rendered text
        displaced_tx: x coordinate of last character in BTGroup
        flip_sort: -1 if page is upside down, else 1
    """

    tx: float
    ty: float
    font_size: float
    font_height: float
    text: str
    displaced_tx: float
    flip_sort: Literal[-1, 1]


def bt_group(tj_op: TextStateParams, rendered_text: str, dispaced_tx: float) -> BTGroup:
    """
    BTGroup constructed from a TextStateParams instance, rendered text, and
    displaced tx value.

    Args:
        tj_op (TextStateParams): TextStateParams instance
        rendered_text (str): rendered text
        dispaced_tx (float): x coordinate of last character in BTGroup
    """
    return BTGroup(
        tx=tj_op.tx,
        ty=tj_op.ty,
        font_size=tj_op.font_size,
        font_height=tj_op.font_height,
        text=rendered_text,
        displaced_tx=dispaced_tx,
        flip_sort=-1 if tj_op.flip_vertical else 1,
    )


def decode_tj(_b: bytes, text_state_mgr: TextStateManager) -> TextStateParams:
    """
    Decode a Tj/TJ operator.

    Args:
        _b: text bytes
        text_state_mgr: stack of cm/tm transformations to be applied

    Raises:
        ValueError: if font not set (no Tf operator in incoming pdf content stream)

    Returns:
        TextStateParams: dataclass containing rendered text and state parameters
    """
    if not text_state_mgr.font:
        raise ValueError("font not set: is PDF missing a Tf operator?")
    try:
        if isinstance(text_state_mgr.font.encoding, str):
            _text = _b.decode(text_state_mgr.font.encoding, "surrogatepass")
        else:
            _text = "".join(
                text_state_mgr.font.encoding[x]
                if x in text_state_mgr.font.encoding
                else bytes((x,)).decode()
                for x in _b
            )
    except (UnicodeEncodeError, UnicodeDecodeError):
        _text = _b.decode("utf-8", "replace")
    _text = "".join(
        text_state_mgr.font.char_map[x] if x in text_state_mgr.font.char_map else x for x in _text
    )
    return text_state_mgr.text_state_params(_text)


def recurs_to_target_op(
    ops: Iterator[Tuple[List[Any], bytes]],
    text_state_mgr: TextStateManager,
    end_target: Literal[b"Q", b"ET"],
    fonts: Dict[str, Font],
    strip_rotated: bool = True,
) -> Tuple[List[BTGroup], List[TextStateParams]]:
    """
    Recurse operators between BT/ET and/or q/Q operators managing the transform
    stack and capturing text positioning and rendering data.

    Args:
        ops: iterator of operators in content stream
        text_state_mgr: a TextStateManager instance
        end_target: Either b"Q" (ends b"q" op) or b"ET" (ends b"BT" op)
        fonts: font dictionary as returned by PageObject._layout_mode_fonts()

    Returns:
        tuple: list of BTGroup dicts + list of TextStateParams dataclass instances.
    """
    # 1 entry per line of text rendered within each BT/ET operation.
    bt_groups: List[BTGroup] = []

    # 1 entry per text show operator (Tj/TJ/'/")
    tj_ops: List[TextStateParams] = []

    if end_target == b"Q":
        # add new q level. cm's added at this level will be popped at next b'Q'
        text_state_mgr.add_q()

    while True:
        try:
            operands, op = next(ops)
        except StopIteration:
            return bt_groups, tj_ops
        if op == end_target:
            if op == b"Q":
                text_state_mgr.remove_q()
            if op == b"ET":
                if not tj_ops:
                    return bt_groups, tj_ops
                _text = ""
                bt_idx = 0  # idx of first tj in this bt group
                last_displaced_tx = tj_ops[bt_idx].displaced_tx
                last_ty = tj_ops[bt_idx].ty
                for _idx, _tj in enumerate(tj_ops):  # ... build text from new Tj operators
                    if strip_rotated and _tj.rotated:
                        continue
                    # if the y position of the text is greater than the font height, assume
                    # the text is on a new line and start a new group
                    if abs(_tj.ty - last_ty) > _tj.font_height:
                        if _text.strip():
                            bt_groups.append(bt_group(tj_ops[bt_idx], _text, last_displaced_tx))
                        bt_idx = _idx
                        _text = ""

                    # if the x position of the text is less than the last x position by
                    # more than 5 spaces widths, assume the text order should be flipped
                    # and start a new group
                    if (
                        last_displaced_tx - _tj.tx
                        > _tj.space_tx * LAYOUT_NEW_BT_GROUP_SPACE_WIDTHS
                    ):
                        if _text.strip():
                            bt_groups.append(bt_group(tj_ops[bt_idx], _text, last_displaced_tx))
                        bt_idx = _idx
                        last_displaced_tx = _tj.displaced_tx
                        _text = ""

                    # calculate excess x translation based on ending tx of previous Tj
                    excess_tx = round(_tj.tx - last_displaced_tx, 3)

                    # pdfs sometimes have "placeholder" spaces for variable length date, time,
                    # and page number fields. Continue below prevents these spaces from being
                    # rendered in the output text avoiding extra spaces in datetime and
                    # header/footer page number strings. Might be knockout (Tk) related??
                    if _tj.txt == " " and _text.endswith(" ") and excess_tx <= _tj.space_tx:
                        continue

                    if _tj.space_tx > 0.0:
                        new_text = f'{" " * int(excess_tx // _tj.space_tx)}{_tj.txt}'
                    else:
                        new_text = _tj.txt

                    last_ty = _tj.ty
                    _text = f"{_text}{new_text}"
                    last_displaced_tx = _tj.displaced_tx
                if _text:
                    bt_groups.append(bt_group(tj_ops[bt_idx], _text, last_displaced_tx))
                text_state_mgr.reset_tm()
            return bt_groups, tj_ops
        if op == b"q":
            bts, tjs = recurs_to_target_op(ops, text_state_mgr, b"Q", fonts, strip_rotated)
            bt_groups.extend(bts)
            tj_ops.extend(tjs)
        elif op == b"cm":
            text_state_mgr.add_cm(*operands)
        elif op == b"BT":
            bts, tjs = recurs_to_target_op(ops, text_state_mgr, b"ET", fonts, strip_rotated)
            bt_groups.extend(bts)
            tj_ops.extend(tjs)
        elif op == b"Tj":
            tj_ops.append(decode_tj(operands[0], text_state_mgr))
        elif op == b"TJ":
            _tj = text_state_mgr.text_state_params()
            for tj_op in operands[0]:
                if isinstance(tj_op, bytes):
                    _tj = decode_tj(tj_op, text_state_mgr)
                    tj_ops.append(_tj)
                else:
                    text_state_mgr.add_trm(_tj.displacement_matrix(TD_offset=tj_op))
        elif op == b"'":
            text_state_mgr.reset_trm()
            text_state_mgr.add_tm([0, text_state_mgr.TL])
            tj_ops.append(decode_tj(operands[0], text_state_mgr))
        elif op == b'"':
            text_state_mgr.reset_trm()
            _set_state_param(b"Tw", [operands[0]], text_state_mgr)
            _set_state_param(b"Tc", [operands[1]], text_state_mgr)
            text_state_mgr.add_tm([0, text_state_mgr.TL])
            tj_ops.append(decode_tj(operands[2], text_state_mgr))
        elif op in (b"Td", b"Tm", b"TD", b"T*"):
            text_state_mgr.reset_trm()
            if op == b"Tm":
                text_state_mgr.reset_tm()
            elif op == b"TD":
                _set_state_param(b"TL", [-operands[1]], text_state_mgr)
            elif op == b"T*":
                operands = [0, -text_state_mgr.TL]
            text_state_mgr.add_tm(operands)
        elif op == b"Tf":
            text_state_mgr.font_size = operands[1]
            text_state_mgr.font = fonts[operands[0]]
        else:  # handle Tc, Tw, Tz, TL, and Ts operators
            _set_state_param(op, operands, text_state_mgr)


def _set_state_param(op: bytes, operands: List[Any], text_state_mgr: TextStateManager) -> None:
    """
    Set a text state parameter.

    Args:
        op: operator defined in PDF standard 1.7 as bytes
        operands: List of operands for the op as bytes, int or float
        text_state_mgr: stack of cm/tm transformations currently applied
    """
    if op == b"Tc":
        text_state_mgr.Tc = operands[0]
    if op == b"Tw":
        text_state_mgr.Tw = operands[0]
    if op == b"Tz":
        text_state_mgr.Tz = operands[0]
    if op == b"TL":
        text_state_mgr.TL = operands[0]
    if op == b"Ts":
        text_state_mgr.Ts = operands[0]


def y_coordinate_groups(
    bt_groups: List[BTGroup], debug_path: Union[Path, None] = None
) -> Dict[int, List[BTGroup]]:
    """
    Group text operations by rendered y coordinate, i.e. the line number.

    Args:
        bt_groups: list of dicts as returned by text_show_operations()
        debug_file: full path + filename prefix for debug output. Defaults to None.

    Returns:
        Dict[int, List[BTGroup]]: dict of lists of text rendered by each BT operator
            keyed by y coordinate
    """
    ty_groups = {
        ty: sorted(grp, key=lambda x: x["tx"])
        for ty, grp in groupby(
            bt_groups, key=lambda bt_grp: int(bt_grp["ty"] * bt_grp["flip_sort"])
        )
    }
    # combine groups whose y coordinates differ by less than the effective font height
    # (accounts for mixed fonts and other minor oddities)
    last_ty = next(iter(ty_groups))
    last_txs = {int(_t["tx"]) for _t in ty_groups[last_ty] if _t["text"].strip()}
    for ty in list(ty_groups)[1:]:
        fsz = min(ty_groups[_y][0]["font_height"] for _y in (ty, last_ty))
        txs = {int(_t["tx"]) for _t in ty_groups[ty] if _t["text"].strip()}
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
    if debug_path:  # pragma: no cover
        import json
        debug_path.joinpath("bt_groups.json").write_text(
            json.dumps(ty_groups, indent=2, default=str), "utf-8"
        )
    return ty_groups


def text_show_operations(
    ops: Iterator[Tuple[List[Any], bytes]],
    fonts: Dict[str, Font],
    strip_rotated: bool = True,
    debug_path: Union[Path, None] = None,
) -> List[BTGroup]:
    """
    Extract text from BT/ET operator pairs.

    Args:
        ops (Iterator[Tuple[List, bytes]]): iterator of operators in content stream
        fonts (Dict[str, Font]): font dictionary
        debug_file (str, optional): full path + filename prefix for debug output.
            Defaults to None.

    Returns:
        List[BTGroup]: list of dicts of text rendered by each BT operator
    """
    state_mgr = TextStateManager()  # transformation stack manager
    debug = bool(debug_path)
    bt_groups: List[BTGroup] = []  # BT operator dict
    tj_debug: List[TextStateParams] = []  # Tj/TJ operator data (debug only)
    try:
        warned_rotation = False
        while True:
            operands, op = next(ops)
            if op in (b"BT", b"q"):
                bts, tjs = recurs_to_target_op(
                    ops, state_mgr, b"ET" if op == b"BT" else b"Q", fonts, strip_rotated
                )
                if not warned_rotation and any(tj.rotated for tj in tjs):
                    warned_rotation = True
                    if strip_rotated:
                        logger_warning(
                            "Rotated text discovered. Output will be incomplete.", __name__
                        )
                    else:
                        logger_warning(
                            "Rotated text discovered. Layout will be degraded.", __name__
                        )
                bt_groups.extend(bts)
                if debug:
                    tj_debug.extend(tjs)
            else:  # handle Tc, Tw, Tz, TL, and Ts operators
                _set_state_param(op, operands, state_mgr)
    except StopIteration:
        pass

    # left align the data, i.e. decrement all tx values by min(tx)
    min_x = min((x["tx"] for x in bt_groups), default=0.0)
    bt_groups = [
        dict(ogrp, tx=ogrp["tx"] - min_x, displaced_tx=ogrp["displaced_tx"] - min_x)  # type: ignore[misc]
        for ogrp in sorted(
            bt_groups, key=lambda x: (x["ty"] * x["flip_sort"], -x["tx"]), reverse=True
        )
    ]

    if debug_path:  # pragma: no cover
        import json
        debug_path.joinpath("bts.json").write_text(
            json.dumps(bt_groups, indent=2, default=str), "utf-8"
        )
        debug_path.joinpath("tjs.json").write_text(
            json.dumps(tj_debug, indent=2, default=lambda x: getattr(x, "to_dict", str)(x)),
            "utf-8",
        )
    return bt_groups


def fixed_char_width(bt_groups: List[BTGroup], scale_weight: float = 1.25) -> float:
    """
    Calculate average character width weighted by the length of the rendered
    text in each sample for conversion to fixed-width layout.

    Args:
        bt_groups (List[BTGroup]): List of dicts of text rendered by each
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
    """
    Generate page text from text operations grouped by rendered y coordinate.

    Args:
        ty_groups: dict of text show ops as returned by y_coordinate_groups()
        char_width: fixed character width
        space_vertically: include blank lines inferred from y distance + font height.

    Returns:
        str: page text in a fixed width format that closely adheres to the rendered
            layout in the source pdf.
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
            spaces = (offset - len(line)) * (ceil(last_disp) < int(bt_op["tx"]))
            line = f"{line}{' ' * spaces}{bt_op['text']}"
            last_disp = bt_op["displaced_tx"]
        if line.strip() or lines:
            lines.append("".join(c if ord(c) < 14 or ord(c) > 31 else " " for c in line))
        last_y_coord = y_coord
    return "\n".join(ln.rstrip() for ln in lines if space_vertically or ln.strip())
