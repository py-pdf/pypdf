import struct
from binascii import Error as BinasciiError
from binascii import unhexlify
from functools import partial
from io import BytesIO
from typing import Any, Union, cast

from ._codecs import adobe_glyphs, charset_encoding
from ._utils import logger_error, logger_warning
from .errors import LimitReachedError
from .generic import (
    DecodedStreamObject,
    DictionaryObject,
    NullObject,
    StreamObject,
)

_predefined_cmap: dict[str, str] = {
    "/Identity-H": "utf-16-be",
    "/Identity-V": "utf-16-be",
    "/GB-EUC-H": "gbk",
    "/GB-EUC-V": "gbk",
    "/GBpc-EUC-H": "gb2312",
    "/GBpc-EUC-V": "gb2312",
    "/GBK-EUC-H": "gbk",
    "/GBK-EUC-V": "gbk",
    "/GBK2K-H": "gb18030",
    "/GBK2K-V": "gb18030",
    "/ETen-B5-H": "cp950",
    "/ETen-B5-V": "cp950",
    "/ETenms-B5-H": "cp950",
    "/ETenms-B5-V": "cp950",
    "/UniCNS-UTF16-H": "utf-16-be",
    "/UniCNS-UTF16-V": "utf-16-be",
    "/UniGB-UTF16-H": "gb18030",
    "/UniGB-UTF16-V": "gb18030",
    # Japanese CMaps (PDF Reference 1.7, Appendix H)
    "/90ms-RKSJ-H": "cp932",  # Shift-JIS (JIS X 0208-1990), horizontal
    "/90ms-RKSJ-V": "cp932",  # Shift-JIS (JIS X 0208-1990), vertical
    "/UniJIS-UTF16-H": "utf-16-be",  # Unicode UTF-16BE -> JIS, horizontal
    "/UniJIS-UTF16-V": "utf-16-be",  # Unicode UTF-16BE -> JIS, vertical
    # UCS2 in code
}


def get_encoding(
    ft: DictionaryObject
) -> tuple[Union[str, dict[int, str]], dict[Any, Any]]:
    encoding = _parse_encoding(ft)
    map_dict, int_entry = _parse_to_unicode(ft)

    # Apply rule from PDF ref 1.7 §5.9.1, 1st bullet:
    #   if cmap not empty encoding should be discarded
    #   (here transformed into identity for those characters)
    # If encoding is a string, it is expected to be an identity translation.
    if isinstance(encoding, dict):
        for x in int_entry:
            if x <= 255:
                encoding[x] = chr(x)

    return encoding, map_dict


def _parse_encoding(
    ft: DictionaryObject
) -> Union[str, dict[int, str]]:
    encoding: Union[str, list[str], dict[int, str]] = []
    # If ft["/Encoding"] exists, then use that for encoding. Otherwise, use StandardEncoding as a basis,
    # and add what the embedded font file says, if present. See Table 114, PDF Reference 1.7 / 2.0
    if "/Encoding" not in ft:
        if "/BaseFont" in ft and cast(str, ft["/BaseFont"]) in charset_encoding:
            # This will match Symbol and ZapfDingBats
            return dict(
                zip(range(256), charset_encoding[cast(str, ft["/BaseFont"])])
            )

        # Return StandardEncoding as fallback option. Note that a font's internal encoding can be used
        # to overwrite this, which we do for Type1 fonts in _character_map_from_(cff_)type1_font_file.
        return dict(
            zip(range(256), charset_encoding["/StandardEncoding"])
        )

    enc: Union[str, DictionaryObject, NullObject] = cast(
        Union[str, DictionaryObject, NullObject], ft["/Encoding"].get_object()
    )
    if isinstance(enc, str):
        try:
            # already done : enc = NameObject.unnumber(enc.encode()).decode()
            # for #xx decoding
            if enc in charset_encoding:
                encoding = charset_encoding[enc].copy()
            elif enc in _predefined_cmap:
                encoding = _predefined_cmap[enc]
            elif "-UCS2-" in enc:
                encoding = "utf-16-be"
            else:
                raise Exception("not found")
        except Exception:
            logger_error("Advanced encoding %(encoding)s not implemented yet", source=__name__, encoding=enc)
            encoding = enc
    elif isinstance(enc, DictionaryObject) and "/BaseEncoding" in enc:
        try:
            encoding = charset_encoding[cast(str, enc["/BaseEncoding"])].copy()
        except Exception:
            logger_error(
                "Advanced encoding %(encoding)s not implemented yet",
                source=__name__, encoding=encoding
            )
            encoding = charset_encoding["/StandardEncoding"].copy()
    else:
        encoding = charset_encoding["/StandardEncoding"].copy()
    if isinstance(enc, DictionaryObject) and "/Differences" in enc:
        x: int = 0
        o: Union[int, str]
        for o in cast(DictionaryObject, enc["/Differences"]):
            if isinstance(o, int):
                x = o
            else:  # isinstance(o, str):
                try:
                    if x < len(encoding):
                        encoding[x] = adobe_glyphs[o]  # type: ignore[index]
                except Exception:
                    encoding[x] = o  # type: ignore[index]
                x += 1
    if isinstance(encoding, list):
        encoding = dict(zip(range(256), encoding))
    return encoding


def _parse_to_unicode(
    ft: DictionaryObject
) -> tuple[dict[Any, Any], list[int]]:
    from ._font import HAS_FONTTOOLS  # noqa: PLC0415

    # We store all character mappings in map_dict. In map_dict[-1] we store the byte length
    # of the character codes (or CIDs) encoded inside the ToUnicode stream.
    map_dict: dict[Any, Any] = {}

    # We provide the list of cmap keys in int_entry to correct encoding later on in get_encoding().
    int_entry: list[int] = []

    if "/ToUnicode" not in ft:
        if ft.get("/Subtype", "") == "/Type1":
            font_descriptor = ft.get("/FontDescriptor")
            if not font_descriptor:
                return map_dict, int_entry

            # We try to read encoding from an embedded font file, if we can. See Table 126 about embedded font
            # file organization in the PDF specification 1.7 for details.
            font_file_handlers = (
                # A normal Type1 font file, can be part of a Type1 or MMType1 font dictionary.
                (
                    "/FontFile",
                    lambda _: True,
                    _character_map_from_type1_font_file
                ),
                # A CFF Type1 font file, as part of a Type1 or MMType1 font dictionary, when subtype is Type1C.
                (
                    "/FontFile3",
                    lambda stream: stream.get("/Subtype") == "/Type1C",
                    _character_map_from_cff_type1_font_file,
                )
            )
            for font_file, condition, font_file_processor in font_file_handlers:
                if (
                    font_file in font_descriptor and
                    isinstance(font_file_dict := font_descriptor[font_file], StreamObject) and
                    condition(font_file_dict)
                ):
                    if font_file == "/FontFile3" and not HAS_FONTTOOLS:
                        logger_warning(
                            (
                                "fontTools is required to fully parse the encoding of a CFF Type1 font in font "
                                "dictionary %(ft)s, but is not installed. Consider installing fontTools if you "
                                "encounter encoding problems."
                            ),
                            source=__name__,
                            ft=ft,
                        )
                        return map_dict, int_entry

                    font_file_data = font_file_dict.get_data()
                    if not font_file_data:
                        return map_dict, int_entry

                    return font_file_processor(font_file_data, map_dict, int_entry)

            return map_dict, int_entry

        return {}, []

    process_rg: bool = False
    process_char: bool = False
    multiline_rg: Union[
        tuple[int, int], None
    ] = None  # tuple = (current_char, remaining size) ; cf #1285 for example of file
    cm = prepare_cm(ft)
    for line in cm.split(b"\n"):
        process_rg, process_char, multiline_rg = process_cm_line(
            line.strip(b" \t"),
            process_rg,
            process_char,
            multiline_rg,
            map_dict,
            int_entry,
        )

    map_dict.pop(-1, None)  # Don't pass the -1 key, we only used it to temporarily store encoding length

    return map_dict, int_entry


def prepare_cm(ft: DictionaryObject) -> bytes:
    tu = ft["/ToUnicode"]
    cm: bytes
    if isinstance(tu, StreamObject):
        cm = cast(DecodedStreamObject, ft["/ToUnicode"]).get_data()
    else:  # if (tu is None) or cast(str, tu).startswith("/Identity"):
        # the full range 0000-FFFF will be processed
        cm = b"beginbfrange\n<0000> <0001> <0000>\nendbfrange"
    if isinstance(cm, str):
        cm = cm.encode()
    # we need to prepare cm before due to missing return line in pdf printed
    # to pdf from word
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
            if j == 0:
                # string is empty: stash a placeholder here (see below)
                # see https://github.com/py-pdf/pypdf/issues/1111
                content = b"."
            else:
                content = ll[i][:j].replace(b" ", b"")
            ll[i] = content + b" " + ll[i][j + 1 :]
    cm = (
        (b" ".join(ll))
        .replace(b"[", b" [ ")
        .replace(b"]", b" ]\n ")
        .replace(b"\r", b"\n")
    )
    return cm


def process_cm_line(
    line: bytes,
    process_rg: bool,
    process_char: bool,
    multiline_rg: Union[tuple[int, int], None],
    map_dict: dict[Any, Any],
    int_entry: list[int],
) -> tuple[bool, bool, Union[tuple[int, int], None]]:
    if line == b"" or line[0] == 37:  # 37 = %
        return process_rg, process_char, multiline_rg
    line = line.replace(b"\t", b" ")
    if b"beginbfrange" in line:
        process_rg = True
    elif b"endbfrange" in line:
        process_rg = False
    elif b"beginbfchar" in line:
        process_char = True
    elif b"endbfchar" in line:
        process_char = False
    elif process_rg:
        try:
            multiline_rg = parse_bfrange(line, map_dict, int_entry, multiline_rg)
        except (ValueError, IndexError) as error:
            logger_warning("Skipping broken line %(line)r: %(error)s", source=__name__, line=line, error=error)
    elif process_char:
        try:
            parse_bfchar(line, map_dict, int_entry)
        except (ValueError, IndexError) as error:
            logger_warning("Skipping broken line %(line)r: %(error)s", source=__name__, line=line, error=error)
    return process_rg, process_char, multiline_rg


# Usual values should be up to 65_536.
MAPPING_DICTIONARY_SIZE_LIMIT = 100_000

# Typical /ToUnicode CMaps use 1-4 byte source codes.
# This is intentionally generous.
# The actual limit is doubled, as each byte is represented by two hex characters.
MAX_CMAP_CODE_BYTES = 8
MAX_CMAP_STRING_BYTES = 512
MAX_CMAP_CODE_BYTES_LIMIT = MAX_CMAP_CODE_BYTES * 2
MAX_CMAP_STRING_BYTES_LIMIT = MAX_CMAP_STRING_BYTES * 2


def _check_mapping_size(size: int) -> None:
    if size > MAPPING_DICTIONARY_SIZE_LIMIT:
        raise LimitReachedError(f"Maximum /ToUnicode size limit reached: {size} > {MAPPING_DICTIONARY_SIZE_LIMIT}.")


def _check_token_length(token: bytes, limit: int) -> None:
    token_length = len(token)
    if token_length > limit:
        description = {
            MAX_CMAP_CODE_BYTES_LIMIT: "code",
            MAX_CMAP_STRING_BYTES_LIMIT: "string",
        }.get(limit, "token")

        raise LimitReachedError(
            f"Maximum /ToUnicode {description} length exceeded: {token_length} > {limit}."
        )


def __parse_bfrange__decode(map_dict: dict[Any, Any], code: int) -> str:
    # `map_dict[-1]` is the number of bytes each source code occupies. Building
    # the bytes directly with `int.to_bytes` avoids the hex round-trip of
    # `unhexlify(b"%%0%dX" % (map_dict[-1] * 2) % code)` (format to hex, parse
    # the hex back to bytes), which is measurably cheaper for large maps.
    return code.to_bytes(map_dict[-1], "big").decode(
        "charmap" if map_dict[-1] == 1 else "utf-16-be",
        "surrogatepass",
    )


def parse_bfrange(
    line: bytes,
    map_dict: dict[Any, Any],
    int_entry: list[int],
    multiline_rg: Union[tuple[int, int], None],
) -> Union[tuple[int, int], None]:
    lst = line.split()
    closure_found = False
    entry_count = len(int_entry)
    _check_mapping_size(entry_count)
    decode_utf16 = partial(bytes.decode, encoding="utf-16-be", errors="surrogatepass")
    if multiline_rg is not None:
        a = multiline_rg[0]  # a, b not in the current line
        b = multiline_rg[1]
        for sq in lst:
            if sq == b"]":
                closure_found = True
                break
            _check_token_length(sq, limit=MAX_CMAP_STRING_BYTES_LIMIT)
            entry_count += 1
            _check_mapping_size(entry_count)
            map_dict[
                __parse_bfrange__decode(map_dict=map_dict, code=a)
            ] = decode_utf16(unhexlify(sq))
            int_entry.append(a)
            a += 1
    else:
        _check_token_length(lst[0], limit=MAX_CMAP_CODE_BYTES_LIMIT)
        _check_token_length(lst[1], limit=MAX_CMAP_CODE_BYTES_LIMIT)
        a = int(lst[0], 16)
        b = int(lst[1], 16)
        nbi = max(len(lst[0]), len(lst[1]))
        map_dict[-1] = (nbi + 1) // 2
        if lst[2] == b"[":
            for sq in lst[3:]:
                if sq == b"]":
                    closure_found = True
                    break
                _check_token_length(sq, limit=MAX_CMAP_STRING_BYTES_LIMIT)
                entry_count += 1
                _check_mapping_size(entry_count)
                map_dict[
                    __parse_bfrange__decode(map_dict=map_dict, code=a)
                ] = decode_utf16(unhexlify(sq))
                int_entry.append(a)
                a += 1
        else:  # case without list
            _check_token_length(lst[2], limit=MAX_CMAP_STRING_BYTES_LIMIT)
            c = int(lst[2], 16)
            fmt2 = b"%%0%dX" % max(4, len(lst[2]))
            closure_found = True
            range_size = max(0, b - a + 1)
            _check_mapping_size(entry_count + range_size)  # This can be checked beforehand.
            while a <= b:
                destination = unhexlify(fmt2 % c)
                _check_token_length(destination, limit=MAX_CMAP_CODE_BYTES_LIMIT)
                map_dict[
                    __parse_bfrange__decode(map_dict=map_dict, code=a)
                ] = decode_utf16(destination)
                int_entry.append(a)
                a += 1
                c += 1
    return None if closure_found else (a, b)


def parse_bfchar(line: bytes, map_dict: dict[Any, Any], int_entry: list[int]) -> None:
    lst = [x for x in line.split(b" ") if x]
    new_count = len(lst) // 2
    _check_mapping_size(len(int_entry) + new_count)  # This can be checked beforehand.
    map_dict[-1] = len(lst[0]) // 2
    while len(lst) > 1:
        map_to = ""
        # placeholder (see above) means empty string
        if lst[1] != b".":
            try:
                map_to = unhexlify(lst[1]).decode(
                    "charmap" if len(lst[1]) < 4 else "utf-16-be", "surrogatepass"
                )  # join is here as some cases where the code was split
            except BinasciiError as exception:
                logger_warning(
                    "Got invalid hex string: %(exception)s (%(lst_value)r)",
                    source=__name__,
                    exception=exception,
                    lst_value=lst[1],
                )
        map_dict[
            unhexlify(lst[0]).decode(
                "charmap" if map_dict[-1] == 1 else "utf-16-be", "surrogatepass"
            )
        ] = map_to
        int_entry.append(int(lst[0], 16))
        lst = lst[2:]


def _glyph_name_to_unicode(glyph_name: str) -> Union[str, None]:
    try:
        return adobe_glyphs[glyph_name]
    except KeyError:
        if not glyph_name.startswith("/uni"):
            return None
        try:
            return chr(int(glyph_name[4:], 16))
        except ValueError:  # pragma: no cover
            return None


def _character_map_from_cff_type1_font_file(
    font_data: bytes,
    map_dict: dict[Any, Any],
    int_entry: list[int],
) -> tuple[dict[Any, Any], list[int]]:
    try:
        from fontTools.cffLib import CFFFontSet  # noqa: PLC0415
        cff_set = CFFFontSet()
        cff_set.decompile(BytesIO(font_data), None)  # This can raise ValueError, AssertionError, struct.error.
        cff_font = cff_set.topDictIndex[0]           # First font in CFF set; Can raise AttributeError or IndexError.
        cff_encoding = cff_font.Encoding             # Can raise AttributeError.
        # Encoding can fall back to literal strings "StandardEncoding" or "ExpertEncoding", which we do not parse.
        if isinstance(cff_encoding, str):
            return map_dict, int_entry
        for i in range(min(len(cff_encoding), 256)):
            glyph_name = cff_encoding[i]
            if not glyph_name or glyph_name == ".notdef":
                continue
            if unipoint := _glyph_name_to_unicode(f"/{glyph_name}"):
                map_dict[chr(i)] = unipoint
                int_entry.append(i)
        return map_dict, int_entry

    except (struct.error, AssertionError, AttributeError, IndexError, ValueError):
        return map_dict, int_entry


def _character_map_from_type1_font_file(
    font_data: bytes,
    map_dict: dict[Any, Any],
    int_entry: list[int],
) -> tuple[dict[Any, Any], list[int]]:
    txt = font_data.split(b"eexec\n")[0]  # Only the clear part
    encoding_part = txt.split(b"/Encoding")
    if len(encoding_part) < 2:
        return map_dict, int_entry
    txt = encoding_part[1]  # To get the encoding part
    lines = txt.replace(b"\r", b"\n").split(b"\n")
    for li in lines:
        if li.startswith(b"dup"):
            words = [_w for _w in li.split(b" ") if _w != b""]
            if len(words) < 3 or (len(words) > 3 and words[3] != b"put"):
                continue
            try:
                i = int(words[1])
            except ValueError:  # pragma: no cover
                continue

            unipoint = _glyph_name_to_unicode(words[2].decode())
            if unipoint:
                map_dict[chr(i)] = unipoint
                int_entry.append(i)

    return map_dict, int_entry
