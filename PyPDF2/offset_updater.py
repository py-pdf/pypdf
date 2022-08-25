from collections.abc import Iterable
import logging
import re
import sys

# offset_updater.py --- Updates offsets and lengths in a simple PDF file.
# 2022-08-25, Sascha Rogmann: Initial version.
# License: https://github.com/py-pdf/PyPDF2/blob/main/LICENSE


def usage():
    """Print a short main-usage."""
    print("Usage: [--encoding Encoding] PDF-file-in PDF-file-out")
    print(f"  {sys.argv[0]} adjusts stream-lengths and xref-offsets")
    print("  in simple pdf files (ASCII only).")
    print("  Unsupported: e.g. generations > 0, multiple xrefs")


def update_lines(linesIn: Iterable[str], encoding: str) -> Iterable[str]:
    """Iterates over the lines of a pdf-files and updates offsets.

    The input is expected to be a pdf without binary-sections.

    :param linesIn: An Iterable over the lines including line-breaks.
    :param encoding: The encoding, e.g. "iso-8859-1" or "UTF-8".
    :return The output is a list of lines to be written in the given encoding.
    """
    logger = logging.getLogger("update_lines")
    regExpObj = re.compile(r"^([0-9]+) ([0-9]+) obj *")
    regExpContent = re.compile(r"^(.*)")
    regExpLength = re.compile(r"^(.*/Length )([0-9]+)( .*)", re.DOTALL)

    linesOut = []  # lines to be written
    mapOffsets = {}  # map from line-number to offset
    mapObjOffset = {}  # map from object-number to offset
    lineNo = 0  # current line-number (starting at 0)
    offsetOut = 0  # current offset in output-file
    lineXref = None  # line-number of xref-line (in xref-section only)
    lineStartxref = None  # line-number of startxref-line
    currentObj = None  # number of current object
    currentLengthLine = None  # line containing stream-length
    lenStream = None  # length of stream (in stream only)
    mapStreamLen = {}  # map from object-number to length /Length of stream
    mapObjLengthLine = {}  # map from object-number to /Length-line
    mapObjLengthLineNo = {}  # map from object-number to lineNo of /Length-line
    for line in linesIn:
        lineNo += 1
        mContent = regExpContent.match(line)
        if mContent is None:
            raise RuntimeError(f"Line {lineNo} without line-break.")
        content = mContent.group(1)
        mapOffsets[lineNo] = offsetOut
        mObj = regExpObj.match(line)
        if mObj is not None:
            currentObj = mObj.group(1)
            logger.info(f"line {lineNo}: object {currentObj}")
            mapObjOffset[currentObj] = int(offsetOut)
        if content == "xref":
            offsetXref = offsetOut
            lineXref = lineNo
        elif content == "startxref":
            lineStartxref = lineNo
            lineXref = None
        elif content == "stream":
            logger.info(f"line {lineNo}: start stream")
            lenStream = 0
        elif content == "endstream":
            logger.info(f"line {lineNo}: end stream")
            if currentObj is None:
                raise RuntimeError(
                    f"Line {lineNo}: " + "endstream without object-start."
                )
            if lenStream is None:
                raise RuntimeError(f"Line {lineNo}: endstream without stream.")
            logger.info(f"line {lineNo}: /Length {lenStream}")
            mapStreamLen[currentObj] = lenStream
        elif content == "endobj":
            currentObj = None
        elif currentObj is not None and lenStream is None:
            mLength = regExpLength.match(line)
            if mLength is not None:
                logger.info(f"line {lineNo}, /Length: {content}")
                mapObjLengthLine[currentObj] = line
                mapObjLengthLineNo[currentObj] = lineNo
        elif currentObj is not None and lenStream is not None:
            lenStream += len(line.encode(encoding))
        elif lineXref is not None and lineNo > lineXref + 2:
            objNo = lineNo - lineXref - 2
            if objNo <= len(mapObjOffset) and str(objNo) in mapObjOffset:
                eol = line[-2:]
                xrefUpd = ("%010d" % mapObjOffset[str(objNo)]) + " 00000 n"
                logger.info(f"{content} -> {xrefUpd}")
                line = xrefUpd + eol
        elif lineStartxref is not None and lineNo == lineStartxref + 1:
            line = "%d\n" % offsetXref
        linesOut.append(line)

        offsetOut += len(line.encode(encoding))

    for currentObj, streamLen in mapStreamLen.items():
        if not currentObj in mapObjLengthLine:
            raise RuntimeError(
                f"obj {currentObj} with stream-len {len} has no object-length-line: {mapObjLengthLine}"
            )
        mLength = regExpLength.match(mapObjLengthLine[currentObj])
        lenDigits = len(mLength.group(2))
        lenFormat = "%%0%dd" % lenDigits
        line = mLength.group(1) + (lenFormat % streamLen) + mLength.group(3)
        linesOut[mapObjLengthLineNo[currentObj] - 1] = line

    return linesOut


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    argIdx = 1
    encoding = "iso-8859-1"
    if sys.argv[argIdx] == "--encoding":
        encoding = sys.argv[argIdx + 1]
        print(f"Encoding {encoding}")
        argIdx += 2
    if argIdx >= len(sys.argv):
        usage()
        sys.exit(1)
    if sys.argv[argIdx] == "-v":
        logging.basicConfig(level=logging.INFO)
        argIdx += 1
    if argIdx + 1 >= len(sys.argv):
        usage()
        sys.exit(1)
    fileIn = sys.argv[argIdx]
    fileOut = sys.argv[argIdx + 1]

    print(f"Read {fileOut}")

    with open(fileIn, "r") as f:
        linesOut = update_lines(f, encoding)

    with open(fileOut, "wb") as f:
        for line in linesOut:
            f.write(line.encode(encoding))

    print(f"Wrote {fileOut}")
