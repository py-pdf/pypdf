# PyPDF2 font handler - Original Chris Johnson  May2000 "
# Provides various functions to handle character encoding within PDFs
# which should improve text extraction and other command stream text
# features which depend on the font that is in use.
#
# The primary functions are
# - FetchFontExtended - reads the PDF font object including various
#   encoding related objects
# - as_text - converts pdf objects to unicode
# to do
# - this code must be considered a 'work in progress' so testing, testing, testing
# - add assertions and error if STRICT
# - properly handle PDF text objects - perhaps reconverting original bytes
#   and setting an object property to indicate this
# - implement some sort of cache based on object number\
#
# Chris  Johnson
import io
import unicodedata
import urllib.request

import PyPDF2
from PyPDF2.filters import *
from PyPDF2.generic import *
from PyPDF2.utils import glyph2unicode

TRACE = False


class toUnicode(DictionaryObject):
    def __init__(
        self,
        id,
        codespacerange=None,
        codelength=None,
        loaded=None,
        fchars=None,
        franges=None,
        ROS=None,
        baseencoding=None,
        diffs=None,
        debug=False,
    ):
        ErrorMessage = "ToUnicode parse error found {} expecting {} "
        self.StandardCodecs = [
            "/StandardEncoding",
            "/MacRomanEncoding",
            "/WinAnsiEncoding",
            "/MacExpertEncoding",
        ]

        self.StandardEncodings = [
            "/StandardEncoding",
            "/MacRomanEncoding",
            "/WinAnsiEncoding",
            "/MacExpertEncoding",
        ]
        self.StandardEncodingsb = [
            b"/StandardEncoding",
            b"/MacRomanEncoding",
            b"/WinAnsiEncoding",
            b"/MacExpertEncoding",
        ]
        self.known_encodings = [
            "/Symbol",
            "/ZapfDingbats",
            "/StandardEncoding",
            "/MacRomanEncoding",
            "/WinAnsiEncoding",
            "/MacExpertEncoding",
        ]
        self.known_encodingsb = [
            b"/Symbol",
            b"/ZapfDingbats",
            b"/StandardEncoding",
            b"/MacRomanEncoding",
            b"/WinAnsiEncoding",
            b"/MacExpertEncoding",
        ]

        x = ErrorMessage.format("#", "#")
        self.id = id
        self.loaded = loaded
        self.fchars = fchars
        self.franges = franges
        self.ROS = ROS
        self.baseencoding = baseencoding
        self.codespacerange = codespacerange
        if diffs is not None:
            if debug:
                print("we have /Differences")
            self.diffs = diffs
            self.ucodes = toUnicode.checkDiffs(self.diffs)
        else:
            if debug:
                print("we have no /Differences ")
            self.diffs = None
        # if codespacerange:
        #    self.codespacerange=codespacerange
        if codelength is not None:
            self.codelength = codelength
        elif codespacerange is not None:
            self.codelength = [len(range[0]) for range in codespacerange]
        elif baseencoding in (self.StandardEncodings):
            self.codelength = 1
        elif baseencoding in (self.StandardEncodingsb):
            self.codelength = 1
        elif baseencoding == "/Symbol":
            self.codelength = 1
        elif baseencoding == "/ZapfDingbats":
            self.codelength = 1
        else:
            self.codelength = None

    def setId(id):
        self.id = id

    def setid(id):
        self.id = id

    def tell(self, What="Summary"):
        print("Unicode aware Font object  CJ version *")
        print(
            "Loaded {}   id {} ".format(self.loaded, self.id),
        )
        print("ROS")
        print(self.ROS)
        print("Encoding")
        print(self.baseencoding)
        print("Codespace")
        if self.codespacerange:
            print(self.codespacerange)
        if self.codelength:
            print("Codelength={}".format(self.codelength))
        print("Fchars ")
        if self.fchars:
            print("has {} fchars".format(len(self.fchars)))
            if What == "All":
                for fchar in self.fchars.items():
                    print(fchar)
                for fchar in self.fchars.items():
                    print(fchar)
        print("Franges ")
        if self.franges:
            print("has {} franges".format(len(self.franges)))
            if What == "All":
                for frange in self.franges:
                    print(frange)
        print("Differences")
        if self.diffs:
            print("has {} differences".format(len(self.diffs)))
            if What == "All":
                for diff in se.f.diffs:
                    print(diffs, end=" ")
                print()
        print("==============================")

    def code2text(self, codebytes):
        def shift(res0, offset):
            patts = ("?", ">B", ">H", ">W", ">I")
            try:
                pat = patts[len(res0)]
                int0 = struct.unpack(pat, res0)[0]
                intx = int0 + offset
                bytx = struct.pack(pat, intx)
                return bytx
            except:
                if isinstance(res0, PyPDF2.generic.ArrayObject):
                    return res0[offset]

        def inrange(source, rfrom, rto, pos=0):  #
            if source[pos] < rfrom[0] or source[pos] > rto[0]:
                return False
            elif len(rfrom) == 1:
                return True
            elif source[pos + 1] < rfrom[1] or source[pos + 1] > rto[1]:
                return False
            elif len(rfrom) == 2:
                return True
            elif source[pos + 2] < rfrom[2] or source[pos + 2] > rto[2]:
                return False
            elif len(rfrom) == 3:
                return True
            elif source[pos + 3] < rfrom[3] or source[pos + 3] > rto[3]:
                return False
            elif len(rfrom) == 4:
                return True
            else:
                raise

        if False:
            if debug:
                self.tell(What="All")
            if len(codebytes) % self.codelength[0] == 0:
                pass  # as expected
            else:
                print(
                    f"code2text fed with odd length source {len(codebytes)} for {self.codelength=} "
                )
                if debug:
                    self.tell(What="All")

        BFROM = 0
        BTO = 1
        BREL = bfrom = 1

        i = 0
        o = 0
        utf16_result = bytearray(b"")

        while i < len(codebytes):

            Match = False

            for bfchar in self.fchars.items():
                if bfchar[0] == codebytes[i : i + len(bfchar[0])]:
                    utf16_result.extend(bfchar[1])
                    Match = True
                    i += len(bfchar[0])
                    break

            if Match:
                continue

            for bfrange in self.franges:
                # each byte must be in range
                if inrange(codebytes, bfrange[0], bfrange[1], pos=i):
                    Match = True
                    l = len(bfrange[0]) - 1
                    offset = codebytes[i + l] - bfrange[0][l]
                    result = shift(bfrange[2], offset)
                    utf16_result.extend(result)
                    i += l + 1
                    break
                else:
                    continue

            if not Match:
                utf16_result.extend(b"\xff\xfd")
                i += 1

        text = utf16_result.decode("UTF-16BE")
        return text

    # --------------------------------------------------------------

    def loadSource(source, id, pdf=None, debug=False):
        my_object_number = -999
        if debug:
            print("loadSource " * 5)
        if TRACE:
            import pdb

            pdb.set_trace()
        valid_command_tokens = [
            b"findresource",
            b"defineresource",
            b"pop",
            b"begin",
            b"dict",
            b"end",
            b"def",
            b"begincmap",
            b"endcmap",
            b"begincodespacerange",
            b"endcodespacerange",
            b"beginbfchar",
            b"beginbfrange",
            b"endbfchar",
            b"endbfrange",
        ]
        for t in valid_command_tokens:
            assert type(t) == bytes

        franges = []
        fchars = dict()
        codespaceranges = list()
        dictionary_stack = list()
        currentdict = dict()

        def readCommand(source):
            command_operands = []
            command_operator = ""
            pos_before_read = source.tell()
            token = readObject(source, pdf)
            pos_after_read = source.tell()

            while True:
                if pos_after_read == pos_before_read:
                    break
                if token in valid_command_tokens:
                    break
                command_operands.append(token)

                skipWhitespace(source)
                token = readObject(source, pdf)

            command_operator = token
            return (command_operator, command_operands)

        def do_nothing(operator, operand):
            pass

        def do_begin(operator, operand):

            currentdict.clear()  # actually should not do this but use the current dict e.g. as got by find resource
            dictionary_stack.append(currentdict)

        def do_end(operator, operand):

            currentdict.clear()  # actually should not do this but use the current dict e.g. as got by find resource
            dictionary_stack.append(currentdict)

        def do_def(operator, operand):
            try:
                currentdict[operand[0]] = operand[1]
            except:
                print(f"issue with {operator=} {operand=} ")

        def do_dict(operator, operand):
            """creates an empty dictionary with an initial capacity of int elements and
            pushes the created dictionary object on the operand stack. int is expected
            to be a nonnegative integer. The dictionary is allocated in local or global VM
            according to the VM allocation mode.
            """
            try:
                size = operand.pop()
                empty_dict = DictionaryObject()
                operand.append(empty_dict)
            except:
                print(f"issue with {operator=} {operand=} ")

        def do_begincodespacerange(operator, operand):
            nonlocal my_object_number
            my_object_number = operand.pop()

        def do_endcodespacerange(operator, operand):
            # from and to ranges  1,2 or 3 byte limits -
            # limit test will be   from[n]<=code[n]<=to[n]   where n is nth byte if one, two or three byte codet
            nonlocal codespaceranges
            nonlocal my_object_number
            codespaceranges = [
                (operand[i], operand[i + 1]) for i in range(0, len(operand), 2)
            ]
            my_object_number
            operand.clear()
            if debug:
                print("handled endcodespacerange")

        def do_beginbfrange(operator, operand):
            nonlocal my_object_number
            my_object_number = operand.pop()

        def do_endbfrange(operator, operand):
            nonlocal franges
            this_set = [
                (operand[i], operand[i + 1], operand[i + 2])
                for i in range(0, len(operand), 3)
            ]
            franges.extend(this_set)

        def do_beginbfchar(operator, operand):
            nonlocal my_object_number
            my_object_number = operand.pop()

        def do_endbfchar(operator, operand):
            nonlocal fchars

            for i in range(0, len(operand), 2):
                fchars[operand[i]] = operand[i + 1]

            operand.clear()

        if debug:
            print(source)
        if isinstance(source, io.BytesIO):
            pass  # as its what we expect
            source_pos = source.tell()
        elif isinstance(source, bytes):
            # streamify it
            source = io.BytesIO(source)
        else:
            msg = "ToUnicode data is {} not bytes or bytestream ????".format(
                type(source)
            )
            utils.PdfReadError(msg)

        last_pos = -1
        pos = source.tell()

        while True:
            if last_pos == pos:
                break

            last_pos = pos

            (command, parms) = readCommand(source)

            if debug:
                print(f"====x============= {command}       {parms} ", flush=True)
            if command == b"findresource":
                if debug:
                    print("find resource ignored")
            elif command == b"begin":
                do_begin(command, parms)
            elif command == b"def":
                do_def(command, parms)
            elif command == b"begin":
                do_begin(command, parms)
            elif command == b"begincodespacerange":
                do_begincodespacerange(command, parms)
            elif command == b"endcodespacerange":
                do_endcodespacerange(command, parms)
            elif command == b"beginbfrange":
                do_beginbfrange(command, parms)
            elif command == b"endbfrange":
                do_endbfrange(command, parms)
            elif command == b"beginbfchar":
                do_beginbfchar(command, parms)
            elif command == b"endbfchar":
                do_endbfchar(command, parms)
            elif True:
                if debug:
                    print(f"command {command} not understood")
            skipWhitespace(source)
            pos = source.tell()
        if debug:
            print("returning with current dictionary ")
        if debug:
            print(currentdict)
        if debug:
            print(f"{codespaceranges=}")

        return toUnicode(
            id,
            loaded=True,
            franges=franges,
            fchars=fchars,
            ROS=currentdict,
            codespacerange=codespaceranges,
        )

    loadSource = staticmethod(loadSource)

    def getAGLFB():

        # read adobe glyph lists
        # start with the aglfm which has current names only annotated with proper unicode names
        # add the full glyph-list

        gdict = dict()

        aglfn = "https://raw.githubusercontent.com/adobe-type-tools/agl-aglfn/master/aglfn.txt"
        glist = "https://raw.githubusercontent.com/adobe-type-tools/agl-aglfn/master/glyphlist.txt"

        for site in [aglfn, glist]:

            with urllib.request.urlopen(site) as file:
                l = file.readline()
                while True:
                    l = file.readline()
                    if len(l) < 1:
                        break
                    if l[:1] == b"#":
                        pass
                    else:

                        t1 = l.find(b";")
                        t2 = l.find(b";", t1 + 1)
                        t3 = l.find(b";", t2 + 1)
                        if site == aglfn:
                            hex = l[:t1]
                            glyph = l[t1 + 1 : t2]
                            # unicode_name = l[t2+1:]
                        else:
                            glyph = l[:t1]
                            hex = l[t1 + 1 : t2]
                        glyph_name = b"/" + glyph
                        try:
                            hchar = "".join(
                                [
                                    chr(int(hex.split(b" ")[i], 16))
                                    for i in range(hex.count(b" ") + 1)
                                ]
                            )
                        except:
                            print("error reading glyph table", l)
                            print(hex)

                        gdict[glyph_name] = hchar
        return gdict

    def checkDiffs(dlist, debug=False):
        if debug:
            print("Loading diffs >>>>>>>>>>>>>>>>>>>>>>>>>>")
        # print (dlist)
        gdict = toUnicode.getAGLFB()
        # print( gdict)
        dcodes = [None for i in range(256)]
        ucodes = [None for i in range(256)]
        for item in dlist:
            if isinstance(item, int):
                cp = item
            else:
                assert item[:1], "/"
                # print( cp, item, '<<', )
                dcodes[cp] = item
                cp += 1

        info_nd = 0  # defined as notdef
        info_zd = 0  # def
        info_dd = 0  # defined

        for cp in range(256):
            if dcodes[cp] == "/.notdef":
                unicode = "?"
                info_nd += 1
            elif dcodes[cp]:
                bname = dcodes[cp].encode("utf-8")
                try:
                    unicode = gdict[bname]
                    info_dd += 1
                except:
                    unicode = None
                    info_zd += 1
            else:
                unicode = None
            ucodes[cp] = unicode
        if debug:
            print(
                "Difference table {} known, {} spec notdef  {} failed ".format(
                    info_dd, info_nd, info_zd
                )
            )
        return ucodes

    def loadEncoding(esource, id, pdf=None, debug=False):
        known_encodings = [
            "/Symbol",
            "/ZapfDingbats",
            "/StandardEncoding",
            "/MacRomanEncoding",
            "/WinAnsiEncoding",
            "/MacExpertEncoding",
        ]
        # MacRomanEncoding is a latin1 variant
        # WinAnsiEncoding is a latin 1 variant
        # MacExpertEncoding is an extended Mac Roman

        if isinstance(esource, str):
            if esource in (known_encodings):
                info = " encoding is known"
            else:
                info = " encoding is NOT known"
            if debug:
                print("=+=+=Loaded empty ToUnicode xlate table", esource, info)
            return toUnicode(
                id,
                loaded=False,
                franges=None,
                ROS=None,
                codespacerange=None,
                baseencoding=esource,
                diffs=None,
            )

        elif isinstance(esource, PyPDF2.generic.DictionaryObject):
            enc = esource["/BaseEncoding"]
            dfs = esource["/Differences"]
            _ucodes = toUnicode.checkDiffs(dfs)
            if dfs:
                note = " with differences "
            else:
                note = " no differences"
            if debug:
                print("=+=+=Loaded empty ToUnicode xlate table", enc, note)
            return toUnicode(
                id,
                loaded=False,
                franges=None,
                ROS=None,
                codespacerange=None,
                baseencoding=enc,
                diffs=dfs,
            )

        else:
            VarType = type(esource)
            if debug:
                print("=+=+=+load encoding finds type {}".format(VarType))
            return toUnicode(
                id,
                loaded=False,
                franges=None,
                ROS=None,
                codespacerange=None,
                baseencoding=esource,
            )

    loadEncoding = staticmethod(loadEncoding)

    def xlateBytes(self, bs, replace=None, debug=False):
        # start with empty output
        # for each n (pair?) of bytes (code)  # this dont work for n byte charsets
        # if code  mapped use mapping
        # if code  is in range then use mapping
        # if mapping is based on some other mapping try that
        # if no joy put "undefined character"

        def Nvl(p1=None, p2=None, p3=None):
            if p1:
                return p1
            elif p2:
                return p2
            elif p3:
                return p3

        def DoIf(bool, whenTrue=None, whenFalse=None):
            if bool:
                return whenTrue
            else:
                return whenFalse

        base_codecs = {
            "/WinAnsiEncoding": "iso-8859-1",
            "/MacRomanEncoding": "mac_roman",
            "/StandardEncoding": "Latin-1",
            "/MacExpertEncoding": "Latin-1",
            "/Symbol": "Latin-1",
            "/ZapfDingbats": "Latin-1",
        }

        # note that MacExpert codec is wrong and last two seem to work
        #

        if self.baseencoding in base_codecs:
            codec = base_codecs[self.baseencoding]
            if self.diffs:
                if debug:
                    print("xlatebytes has diffs - bytewise tranlation")
                # ucodes = toUnicode.checkDiffs(self.diffs)
                ucodes = self.ucodes
                cs = [
                    Nvl(
                        p1=ucodes[b],
                        p2=bytes([b]).decode("iso-8859-1", "replace"),
                        p3="?",
                    )
                    for b in bs
                ]
                ustring = "".join(cs)
            else:
                ustring = bs.decode("iso-8859-1", "replace")

            ubytes = ustring.encode("UTF-16BE")
            return ubytes

            #    try:
        elif self.baseencoding == "/ZapfDingbats":
            # print ( "xlatebytes this is wrong, widgets not a latin font" )
            #
            ustring = bs.decode("Latin-1", "replace")
            ubytes = ustring.encode("UTF-16BE")
            return ubytes
            # cps = [bs[i:i+cl] for i in range(0,len(bs),cl)]
            # res = bytearray( b'')
            # for cp in cps:
            #    try:
        elif self.loaded:
            if debug:
                print("Unicode xlate")
            cl = self.codelength
            cps = [bs[i : i + cl] for i in range(0, len(bs), cl)]
            res = bytearray(b"")
            for cp in cps:

                # try a character mapping then a range mapping
                #
                if cp in self.fchars:
                    res.extend(self.fchars[cp])
                    if debug:
                        print("fchar table match", end="")
                        print(self.fchars[cp])
                else:
                    for frange in self.franges:
                        if cp < frange[0]:
                            res.extend([0, 0])
                            break
                        elif cp < frange[1]:
                            # we have a match
                            # compare last bytes as int
                            cpo = cp[-1]
                            cfo = frange[0][-1]
                            offset = cpo - cfo
                            # if list f addresses
                            if isinstance(frange[2], bytes):
                                if offset == 0:
                                    res.extend(frange[2])
                                else:
                                    bb = bytearray(frange[2])
                                    ca, cb = divmod(bb[-1] + offset, 256)
                                    bb[-1] = cb
                                    if ca > 0:
                                        bb[-2] = bb[-2] + ca
                                    res.extend(bb)
                            else:
                                res.extend(frange[2][offset])

                            break
                    pass

            bres = bytes(res)
            return bres
        else:
            print("xlatebytes non standard encoding {}".format(self.baseencoding))
            if debug:
                self.tell()


def as_text(pdf_thing, default="", encoding="latin-1"):
    """Convert a binary or text string to a (unicode) string
    may use one of
         1 a to_unicode object
         2 a byte to character lookup table (for diffs)
         3 the name of a known adobe encoding e.g /MacRoman
         4 the name of a python coded e.g. Latin-1
    Objects that are already unicode are not changed"""

    if encoding is None:
        print("as_text with Encoding of None ")
        encoding = "latin-1"

    if isinstance(pdf_thing, (TextStringObject)):
        return pdf_thing
    elif isinstance(pdf_thing, (ByteStringObject, bytes)) and isinstance(
        encoding, toUnicode
    ):
        return encoding.code2text(pdf_thing)
    elif isinstance(pdf_thing, (ByteStringObject, bytes)) and isinstance(
        encoding, dict
    ):
        tstr = ""
        for ord in pdf_thing:
            try:
                tchar = encodng[ord]
                tstr += tchar
            except:
                # print( f'byte has no repl {ord} ' )
                tstr += "?"
        return tstr
    elif isinstance(pdf_thing, (ByteStringObject, bytes)):
        return decode_builtin(pdf_thing, encoding)
    else:
        return default


def FetchFontExtended(currentobject, id, Debug=False):
    """
    Return the standard fonts in current page or form
    plus encoding object that allows translation.

    encoding is returned as a
        to_unicode
        dict giving strings for each byte
        string with the name of a known encoding

    character interpretation
      1   /ToUnicode
      2   /Differences in encoding object
      3   /Encoding
      4   implied by /Symbol or /ZapfDingbats font
      5   a mapping via Type3 (mixed font) font - potentially recursively
      5   Implied by one of other 14 standard fonts i.e. Latin-1
      6   Held within the font itself

    """
    # print( "~~~~~~~~~~~~~~~~~~~toUnicode.py~~~~~~")
    debug = Debug

    pdf_fonts = {}
    pdf_fonts2u = {}
    pdf_font_subtypes = {}
    pdf_font_encodings = {}

    fonts = {}
    try:

        current_font = currentobject["/Resources"]["/Font"][id].getObject()
        current_font_subtype = current_font["/Subtype"]
        current_font_encoding = current_font["/Encoding"]
        current_font_to_unicode = current_font["/ToUnicode"]
    except KeyError:
        fonts = {}
        print("page has no fonts")
        return None, None  # pdf_fonts, ue
    except:
        print("unknown error retrieving fonts for page")
        return None, None  # pdf_fonts, ue
    """            character interpretation
              1   /ToUnicode 
              2   /Differences in encoding object
              3   /Encoding
              4   implied by /Symbol or /ZapfDingbats font
              5   a mapping via Type3 (mixed font) font - potentially recursively
              6   Implied by one of other 14 standard fonts i.e. Latin-1
              7   Held within the font itself   
            """

    if False:
        pass
    elif current_font_to_unicode is not None:  # 1

        to_unicode_stream = current_font_to_unicode.getData()
        tu = toUnicode.loadSource(to_unicode_stream, id)
        encoding = tu

    elif isinstance(current_font_encoding, DictionaryObject):  # 2

        Diff = current_font_encoding["/Differences"]
        entries = len(Diff)
        i = 0
        source = 0
        repl = dict()
        while i < entries:
            assert isinstance(Diff[i], NumberObject)
            source = Diff[i] + 0
            i += 1
            while (i < entries) and (isinstance(Diff[i], NumberObject) == False):
                char = glyph2unicode(Diff[i])
                repl[source] = char
                source += 1
                i += 1
        encoding = repl
    elif current_font_encoding in (
        "/WinAnsiEncoding",
        "/MacRomanEncoding",
        "/StandardEncoding",
        "/PDFDocEncoding",
    ):  # 3
        encoding = current_font_encoding

    elif current_font["/BaseFont"] in ("/Symbol", "/ZapfDingbats"):  # 4
        encoding = current_font["/BaseFont"]

    elif font_subtype in ("/Type3"):  # 5
        if debug:
            print(key, "+=+=+ /Type3 fonts not handled yet")
        encoding = None
    else:
        if debug:
            print(key, "+=+=+ unable to obtain font encoding +=")
        # need to test for some standard fonts
    return current_font, encoding
