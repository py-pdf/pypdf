import warnings
from binascii import unhexlify
from typing import Any, Dict, List, Tuple, Union, cast

from ._codecs import adobe_glyphs, charset_encoding
from .errors import PdfReadWarning
from .generic import DecodedStreamObject, DictionaryObject


# code freely inspired from @twiggy ; see #711
def build_char_map(
    font_name: str, space_width: float, obj: DictionaryObject
) -> Tuple[
    str, float, Union[str, Dict[int, str]], Dict
]:  # font_type,space_width /2, encoding, cmap
    ft: DictionaryObject = obj["/Resources"]["/Font"][font_name]  # type: ignore
    font_type: str = cast(str, ft["/Subtype"])

    space_code = 32
    encoding, space_code = parse_encoding(ft, space_code)
    map_dict, space_code, int_entry = parse_to_unicode(ft, space_code)

    # encoding can be either a string for decode (on 1,2 or a variable number of bytes) of a char table (for 1 byte only for me)
    # if empty string, it means it is than encoding field is not present and we have to select the good encoding from cmap input data
    if encoding == "":
        if -1 not in map_dict or map_dict[-1] == 1:
            # I have not been able to find any rule for no /Encoding nor /ToUnicode
            # One example shows /Symbol,bold I consider 8 bits encoding default
            encoding = "charmap"
        else:
            encoding = "utf-16-be"
    # apply rule from PDF ref 1.7 §5.9.1, 1st bullet : if cmap not empty encoding should be discarded (here transformed into identity for those characters)
    # if encoding is an str it is expected to be a identity translation
    elif isinstance(encoding, dict):
        for x in int_entry:
            if x <= 255:
                encoding[x] = chr(x)
    if font_name in _default_fonts_space_width:
        # override space_width with new params
        space_width = _default_fonts_space_width[font_name]
    sp_width = compute_space_width(ft, space_code, space_width)

    return (
        font_type,
        float(sp_width / 2),
        encoding,
        # https://github.com/python/mypy/issues/4374
        map_dict,  # type: ignore
    )  # type: ignore


# used when missing data, e.g. font def missing
unknown_char_map: Tuple[str, float, Union[str, Dict[int, str]], Dict] = (
    "Unknown",
    9999,
    dict(zip(range(256), ["�"] * 256)),
    {},
)


_predefined_cmap: Dict[str, str] = {
    "/Identity-H": "utf-16-be",
    "/Identity-V": "utf-16-be",
    "/GB-EUC-H": "gbk",  # TBC
    "/GB-EUC-V": "gbk",  # TBC
    "/GBpc-EUC-H": "gb2312",  # TBC
    "/GBpc-EUC-V": "gb2312",  # TBC
}


# manually extracted from http://mirrors.ctan.org/fonts/adobe/afm/Adobe-Core35_AFMs-229.tar.gz
_default_fonts_space_width: Dict[str, int] = {
    "/Courrier": 600,
    "/Courier-Bold": 600,
    "/Courier-BoldOblique": 600,
    "/Courier-Oblique": 600,
    "/Helvetica": 278,
    "/Helvetica-Bold": 278,
    "/Helvetica-BoldOblique": 278,
    "/Helvetica-Oblique": 278,
    "/Helvetica-Narrow": 228,
    "/Helvetica-NarrowBold": 228,
    "/Helvetica-NarrowBoldOblique": 228,
    "/Helvetica-NarrowOblique": 228,
    "/Times-Roman": 250,
    "/Times-Bold": 250,
    "/Times-BoldItalic": 250,
    "/Times-Italic": 250,
    "/Symbol": 250,
    "/ZapfDingbats": 278,
}


def parse_encoding(
    ft: DictionaryObject, space_code: int
) -> Tuple[Union[str, Dict[int, str]], int]:
    encoding: Union[str, List[str], Dict[int, str]] = []
    if "/Encoding" not in ft:
        try:
            if "/BaseFont" in ft and ft["/BaseFont"] in charset_encoding:
                encoding = dict(
                    zip(range(256), charset_encoding[cast(str, ft["/BaseFont"])])
                )
            else:
                encoding = "charmap"
            return encoding, _default_fonts_space_width[cast(str, ft["/BaseFont"])]
        except Exception:
            if ft["/Subtype"] == "/Type1":
                return "charmap", space_code
            else:
                return "", space_code
    enc: Union(str, DictionaryObject) = ft["/Encoding"].get_object()  # type: ignore
    if isinstance(enc, str):
        try:
            if enc in charset_encoding:
                encoding = charset_encoding[enc].copy()
            elif enc in _predefined_cmap:
                encoding = _predefined_cmap[enc]
            else:
                raise Exception("not found")
        except Exception:
            warnings.warn(
                f"Advanced encoding {enc} not implemented yet",
                PdfReadWarning,
            )
            encoding = enc
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
        x: int = 0
        o: Union[int, str]
        for o in cast(DictionaryObject, cast(DictionaryObject, enc)["/Differences"]):
            if isinstance(o, int):
                x = o
            else:  # isinstance(o,str):
                try:
                    encoding[x] = adobe_glyphs[o]  # type: ignore
                except Exception:
                    encoding[x] = o  # type: ignore
                    if o == " ":
                        space_code = x
                x += 1
    if isinstance(encoding, list):
        encoding = dict(zip(range(256), encoding))
    return encoding, space_code


def parse_to_unicode(
    ft: DictionaryObject, space_code: int
) -> Tuple[Dict, int, List[int]]:
    map_dict: Dict[
        Any, Any
    ] = (
        {}
    )  # will store all translation code and map_dict[-1] we will have the number of bytes to convert
    int_entry: List[
        int
    ] = []  # will provide the list of cmap keys as int to correct encoding
    if "/ToUnicode" not in ft:
        return {}, space_code, []
    process_rg: bool = False
    process_char: bool = False
    cm: bytes = cast(DecodedStreamObject, ft["/ToUnicode"]).get_data()
    # we need to prepare cm before due to missing return line in pdf printed to pdf from word
    cm = (
        cm.strip()
        .replace(b"beginbfchar", b"\nbeginbfchar\n")
        .replace(b"endbfchar", b"\nendbfchar\n")
        .replace(b"beginbfrange", b"\nbeginbfrange\n")
        .replace(b"endbfrange", b"\nendbfrange\n")
        .replace(b"<<", b"\n{\n")  # text between << and >> not used but
        .replace(b">>", b"\n}\n")  # some solution to find it back
    )
    ll = cm.split(b"<")
    for i in range(len(ll)):
        j = ll[i].find(b">")
        if j >= 0:
            ll[i] = ll[i][:j].replace(b" ", b"") + b" " + ll[i][j + 1 :]
    cm = (
        (b" ".join(ll))
        .replace(b"[", b" [ ")
        .replace(b"]", b" ]\n ")
        .replace(b"\r", b"\n")
    )

    for l in cm.split(b"\n"):
        if l in (b"", b" "):
            continue
        if b"beginbfrange" in l:
            process_rg = True
        elif b"endbfrange" in l:
            process_rg = False
        elif b"beginbfchar" in l:
            process_char = True
        elif b"endbfchar" in l:
            process_char = False
        elif process_rg:
            lst = [x for x in l.split(b" ") if x]
            a = int(lst[0], 16)
            b = int(lst[1], 16)
            nbi = len(lst[0])
            map_dict[-1] = nbi // 2
            fmt = b"%%0%dX" % nbi
            if lst[2] == b"[":
                for sq in lst[3:]:
                    if sq == b"]":
                        break
                    map_dict[
                        unhexlify(fmt % a).decode(
                            "charmap" if map_dict[-1] == 1 else "utf-16-be",
                            "surrogatepass",
                        )
                    ] = unhexlify(sq).decode("utf-16-be", "surrogatepass")
                    int_entry.append(a)
                    a += 1
            else:
                c = int(lst[2], 16)
                fmt2 = b"%%0%dX" % len(lst[2])
                while a <= b:
                    map_dict[
                        unhexlify(fmt % a).decode(
                            "charmap" if map_dict[-1] == 1 else "utf-16-be",
                            "surrogatepass",
                        )
                    ] = unhexlify(fmt2 % c).decode("utf-16-be", "surrogatepass")
                    int_entry.append(a)
                    a += 1
                    c += 1
        elif process_char:
            lst = [x for x in l.split(b" ") if x]
            map_dict[-1] = len(lst[0]) // 2
            while len(lst) > 0:
                map_dict[
                    unhexlify(lst[0]).decode(
                        "charmap" if map_dict[-1] == 1 else "utf-16-be", "surrogatepass"
                    )
                ] = unhexlify(lst[1]).decode(
                    "utf-16-be", "surrogatepass"
                )  # join is here as some cases where the code was split
                int_entry.append(int(lst[0], 16))
                lst = lst[2:]
    for a, value in map_dict.items():
        if value == " ":
            space_code = a
    return map_dict, space_code, int_entry


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
