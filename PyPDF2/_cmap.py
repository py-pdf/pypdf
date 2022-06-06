import warnings
from binascii import unhexlify
from typing import Any, Dict, List, Tuple, Union, cast

from ._adobe_glyphs import adobe_glyphs
from .errors import PdfReadWarning
from .generic import DecodedStreamObject, DictionaryObject, charset_encoding


# code freely inspired from @twiggy ; see #711
def build_char_map(
    font_name: str, space_width: float, obj: DictionaryObject
) -> Tuple[str, float, Dict[int, str], Dict]:
    ft: DictionaryObject = obj["/Resources"]["/Font"][font_name]  # type: ignore
    font_type: str = cast(str, ft["/Subtype"])

    space_code = 32
    encoding, space_code = parse_encoding(ft, space_code)
    map_dict, space_code = parse_to_unicode(ft, space_code)
    sp_width = compute_space_width(ft, space_code, space_width)

    return (
        font_type,
        float(sp_width / 2),
        dict(zip(range(256), encoding)),
        # https://github.com/python/mypy/issues/4374
        "".maketrans(map_dict),  # type: ignore
    )


def parse_encoding(ft: DictionaryObject, space_code: int) -> Tuple[List[str], int]:
    encoding: List[str] = []
    if "/Encoding" not in ft:
        return encoding, space_code
    enc: Union(str, DictionaryObject) = ft["/Encoding"].get_object()  # type: ignore
    if isinstance(enc, str):
        try:
            if enc in ("/Identity-H", "/Identity-V"):
                encoding = []
            else:
                encoding = charset_encoding[enc].copy()
        except Exception:
            warnings.warn(
                f"Advanced encoding {encoding} not implemented yet",
                PdfReadWarning,
            )
            encoding = charset_encoding["/StandardCoding"].copy()
    elif isinstance(enc, DictionaryObject) and "/BaseEncoding" in enc:
        try:
            encoding = charset_encoding[cast(str, enc["/BaseEncoding"])].copy()
        except Exception:
            warnings.warn(
                f"Advanced encoding {encoding} not implemented yet",
                PdfReadWarning,
            )
            encoding = charset_encoding["/StandardCoding"].copy()
    else:
        encoding = charset_encoding["/StandardCoding"].copy()
    if "/Differences" in enc:
        x = 0
        for o in cast(DictionaryObject, cast(DictionaryObject, enc)["/Differences"]):
            if isinstance(o, int):
                x = o
            else:
                try:
                    encoding[x] = adobe_glyphs[o]
                except Exception:
                    encoding[x] = o
                    if o == " ":
                        space_code = x
                x += 1
    return encoding, space_code


def parse_to_unicode(ft: DictionaryObject, space_code: int) -> Tuple[Dict, int]:
    map_dict: Dict[Any, Any] = {}
    if "/ToUnicode" not in ft:
        return map_dict, space_code
    process_rg: bool = False
    process_char: bool = False
    cm: str = cast(DecodedStreamObject, ft["/ToUnicode"]).get_data().decode("utf-8")
    for l in (
        cm.strip()
        .replace("<", " ")
        .replace(">", "")
        .replace("[", " [ ")
        .replace("]", " ] ")
        .split("\n")
    ):
        if l == "":
            continue
        if "beginbfrange" in l:
            process_rg = True
        elif "endbfrange" in l:
            process_rg = False
        elif "beginbfchar" in l:
            process_char = True
        elif "endbfchar" in l:
            process_char = False
        elif process_rg:
            lst = [x for x in l.split(" ") if x]
            a = int(lst[0], 16)
            b = int(lst[1], 16)
            if lst[2] == "[":
                for sq in lst[3:]:
                    if "]":
                        break
                    map_dict[a] = unhexlify(sq).decode("utf-16-be")
                    a += 1
                    assert a > b
            else:
                c = int(lst[2], 16)
                fmt = b"%%0%dX" % len(lst[2])
                while a <= b:
                    map_dict[a] = unhexlify(fmt % c).decode("utf-16-be")
                    a += 1
                    c += 1
        elif process_char:
            lst = [x for x in l.split(" ") if x]
            a = int(lst[0], 16)
            map_dict[a] = unhexlify("".join(lst[1:])).decode(
                "utf-16-be"
            )  # join is here as some cases where the code was split

    # get
    for a in map_dict:
        if map_dict[a] == " ":
            space_code = a
    return map_dict, space_code


def compute_space_width(
    ft: DictionaryObject, space_code: int, space_width: float
) -> float:
    sp_width: float = space_width * 2  # default value
    w = []
    st: int = 0
    if "/W" in ft:
        if "/DW" in ft:
            sp_width = cast(float, ft["/DW"])
        w = list(ft["/W"])  # type: ignore
        while len(w) > 0:
            st = w[0]
            second = w[1]
            if isinstance(int, second):
                if st <= space_code and space_code <= second:
                    sp_width = w[2]
                    break
                w = w[3:]
            if isinstance(list, second):
                if st <= space_code and space_code <= st + len(second) - 1:
                    sp_width = second[space_code - st]
                w = w[2:]
            else:
                warnings.warn(
                    "unknown widths : \n" + (ft["/W"]).__repr__(),
                    PdfReadWarning,
                )
                break
    if "/Widths" in ft:
        w = list(ft["/Widths"])  # type: ignore
        try:
            st = cast(int, ft["/FirstChar"])
            en: int = cast(int, ft["/LastChar"])
            if st > space_code or en < space_code:
                raise Exception("Not in range")
            if w[space_code - st] == 0:
                raise Exception("null width")
            sp_width = w[space_code - st]
        except Exception:
            if "/FontDescriptor" in ft and "/MissingWidth" in cast(
                DictionaryObject, ft["/FontDescriptor"]
            ):
                sp_width = ft["/FontDescriptor"]["/MissingWidth"]  # type: ignore
            else:
                # will consider width of char as avg(width)/2
                m = 0
                cpt = 0
                for x in w:
                    if x > 0:
                        m += x
                        cpt += 1
                sp_width = m / max(1, cpt) / 2
    return sp_width
