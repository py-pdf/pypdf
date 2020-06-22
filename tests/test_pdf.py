"""
Tests PDF primitives from pypdf.pdf.

Note for future developers: if defining some code in a ``testX()`` method
that relies on a "fixture data" (e.g. a test file to read from) place it in the
``/tests/fixture_data/testX/`` path (see some of the examples below to have a
hint on how to do this).
"""
# TODO:  switch dependence to pathlib.
import binascii
from io import BytesIO
import os
from os.path import abspath, basename, dirname, join, pardir
import sys
import tempfile
import unittest

from pypdf.generic import IndirectObject, readObject
from pypdf.pdf import PdfFileReader, PdfFileWriter

# Configure path environment
PROJECT_ROOT = abspath(join(dirname(__file__), pardir))
TEST_DATA_ROOT = join(PROJECT_ROOT, "tests", "fixture_data")

sys.path.append(PROJECT_ROOT)


class PdfReaderTestCases(unittest.TestCase):
    """ [EXPLAIN THIS CLASS.] """

    def setUp(self):
        # Variable defining the path where the method to be run next can store
        # its own fixture (test) data.
        self.localDataRoot = join(TEST_DATA_ROOT, self.id().split(".")[-1])

    def testDel(self):
        """
        Tests the ``__del__()`` method of ``PdfFileReader`` and
        ``PdfFileWriter`` ensuring that no exceptions are raised.
        """
        r = PdfFileReader(join(TEST_DATA_ROOT, "crazyones.pdf"))
        w = PdfFileWriter(BytesIO(b""))

        try:
            r.__del__()
            self.assertTrue(True)
        except Exception as e:  # pylint: disable=broad-except
            self.assertTrue(
                False,
                "Exception '%s' was raised in %s.__del__()"
                % (e, PdfFileReader.__name__),
            )

        try:
            w.__del__()
            self.assertTrue(True)
        except Exception as e:  # pylint: disable=broad-except
            self.assertTrue(
                False,
                "Exception '%s' was raised in %s.__del__()"
                % (e, PdfFileWriter.__name__),
            )

    def testFileLoad(self):
        """
        Test loading and parsing of a file. Extract text of the file and
        compare to expected textual output. Expected outcome: file loads, text
        matches expected.
        """
        with open(join(TEST_DATA_ROOT, "crazyones.pdf"), "rb") as inputfile:
            # Load PDF file from file
            r = PdfFileReader(inputfile)
            page1 = r.getPage(0)

            # Retrieve the text of the PDF
            with open(join(self.localDataRoot, "crazyones.txt"), "rb") as pdftextFile:
                pdftext = pdftextFile.read()

            page1Text = page1.extractText().replace("\n", "").encode("utf-8")

            # Compare the text of the PDF to a known source
            self.assertEqual(
                pdftext,
                page1Text,
                msg="PDF extracted text differs from expected value."
                "\n\nExpected:\n\n%r\n\nExtracted:\n\n%r\n\n" % (pdftext, page1Text),
            )

            r.close()

    def testJpegImage(self):
        """
        Test loading and parsing of a file. Extract the image of the file and
        compare to expected textual output. Expected outcome: file loads, image
        matches expected.
        """
        with open(join(TEST_DATA_ROOT, "jpeg.pdf"), "rb") as inputfile:
            # Load PDF file from file
            r = PdfFileReader(inputfile)

            # Retrieve the text of the image
            with open(join(self.localDataRoot, "jpeg.txt"), "r") as pdftextFile:
                imagetext = pdftextFile.read()

            page1 = r.getPage(0)
            xObject = page1["/Resources"]["/XObject"].getObject()
            data = xObject["/Im4"].getData()

            # Compare the text of the PDF to a known source
            self.assertEqual(
                binascii.hexlify(data).decode(),
                imagetext,
                msg="PDF extracted image differs from expected value."
                "\n\nExpected:\n\n%r\n\nExtracted:\n\n%r\n\n"
                % (imagetext, binascii.hexlify(data).decode()),
            )

            r.close()

    def testXRefTableObjects(self):
        """
        Ensures that after ``PdfFileReader._parsePdfFile()`` all the indirect
        references from the XRef-Table *only* have been loaded as expected.
        Objects from the free entries list are included as well in the test.

        This case tests the part of ``PdfFileReader.objects()`` responsible for
        generating the Cross-Reference Table entries too.
        """
        self.maxDiff = None
        inputFiles = (
            "jpeg.pdf",
            "Seige_of_Vicksburg_Sample_OCR.pdf",
            "SF424_page2.pdf",
        )

        for filename in inputFiles:
            filepath = join(TEST_DATA_ROOT, filename)
            xtablepath = join(self.localDataRoot, filename)
            r = PdfFileReader(filepath)
            # The two below are (id, gen, byte offset)-valued lists
            actualItems = list()
            expItems = list()

            for ref in r.objects(PdfFileReader.R_XTABLE, True):
                actualItems.append(
                    (
                        ref.idnum,
                        ref.generation,
                        r._xrefTable[ref.generation][ref.idnum][0],
                    )
                )

            r.close()
            # We artificially read the XRef Table entries that we know belong
            # to filepath, and store them into expItems.
            expItems = sorted(self._parseXRefTable(xtablepath, (0, 1, 2)))
            actualItems = sorted(actualItems)
            expItems = sorted(expItems)

            self.assertListEqual(
                expItems, actualItems, "Differences found in " + filename
            )

    def testXRefStreamObjects(self):
        """
        Like ``PdfReaderTestCases.testXRefTableObjects()``, except that it
        tests objects referenced by the Cross-Reference Stream.
        ``PdfFileReader.objects()`` second part (dealing with XStream objects)
        is invoked and implicitly tested.
        """
        inputFiles = ("crazyones.pdf",)

        for filename in inputFiles:
            filepath = join(self.localDataRoot, filename)
            r = PdfFileReader(join(TEST_DATA_ROOT, filename))
            # Two lists of tuples as explained by Table 18
            actualItems = list()
            expItems = list()

            with open(filepath, "r") as instream:
                for line in instream:
                    if not line or line.isspace() or line.startswith("%"):
                        continue

                    this_type, field2, field3 = (int(f) for f in line.split())
                    expItems.append((this_type, field2, field3))

            for item in r.objects(PdfFileReader.R_XSTREAM, True):
                priv8Item = r._xrefStm[item.idnum]

                if priv8Item[0] in {0, 1}:
                    self.assertEqual(priv8Item[2], item.generation)
                elif priv8Item[0] == 2:
                    self.assertEqual(item.generation, 0)

                actualItems.append(priv8Item)

            r.close()
            actualItems = sorted(actualItems)
            expItems = sorted(expItems)

            self.assertListEqual(
                expItems,
                actualItems,
                "Didn't correctly read the Cross-Reference Stream",
            )

    def testReadXRefStreamCompressedObjects(self):  # pylint: disable=too-many-locals
        """
        Targets the same objects as ``testXRefStreamObjects()``, but instead
        of ensuring an identity between the list of items read and the one
        expected, it verifies that their *contents* are identical.

        This method does **not** test ``PdfFileReader.objects()`` as two of the
        previous test cases did.
        """
        self.maxDiff = None
        inputFiles = ("crazyones.pdf",)
        # expItems and actualItems will contain two-element tuples, where the
        # first element is the object ID, used to sort.
        sortKey = lambda e: e[0]
        compressedObj = lambda e: e[1][0] == 2

        for filename in inputFiles:
            filepath = join(self.localDataRoot, filename)
            r = PdfFileReader(join(TEST_DATA_ROOT, filename))
            expItems = list()
            actualItems = list()

            with open(filepath, "rb") as instream:
                for line in instream:
                    if not line or line.isspace() or line.startswith(b"%"):
                        continue

                    globalId, offset, obj = line.split(b" ", 2)
                    globalId, offset = int(globalId), int(offset)

                    with BytesIO(obj) as objStream:
                        obj = readObject(objStream, r)

                    expItems.append((globalId, obj))

            for itemid, _item in filter(compressedObj, r._xrefStm.items()):
                # We deal exclusively with compressed objects (from Table 18 of
                # ISO 32000 reference, 2008) whose generation number is 0
                actualItems.append(
                    # (ID, PdfObject) tuples
                    (itemid, IndirectObject(itemid, 0, r).getObject())
                )

            r.close()
            expItems = sorted(expItems, key=sortKey)
            actualItems = sorted(actualItems, key=sortKey)

            self.assertListEqual(expItems, actualItems)

    def testXTableAgainstXStream(self):
        """
        In section 7.5.8.4 of ISO 32000, "Compatibility with Applications That
        Do Not Support Compressed Reference Streams", the standard describes a
        means of crafting PDF files designed for versions 1.5+ that can be
        opened nevertheless by readers that support older versions.

        This test case verifies that all the items hidden by the XRef Table in
        non-conforming readers are *all and exactly* loaded into the XRef
        Stream by readers that support PDF 1.5+.
        """
        self.maxDiff = None
        # TO-DO Possibly add a few other files to this test case
        inputFiles = ("GeoBase_NHNC1_Data_Model_UML_EN.pdf",)

        for filename in inputFiles:
            filepath = join(self.localDataRoot, filename)
            expItems = {e[0]: e[1:] for e in self._parseXRefTable(filepath, (0, 2, 3))}
            actualItems = list()
            r = PdfFileReader(join(TEST_DATA_ROOT, filename))

            for ref in r.objects(PdfFileReader.R_XSTREAM, True):
                actualItems.append(ref)

            r.close()
            actualItems = sorted(actualItems, key=lambda e: e.idnum)
            expKeys = sorted(expItems.keys())
            actualKeys = list(map(lambda e: e.idnum, actualItems))

            self.assertListEqual(
                expKeys, actualKeys, "Lists of item IDs are not identical"
            )

            for e, a in zip(expKeys, actualItems):
                self.assertEqual(e, a.idnum, "Items ID does not correspond")

                # If an item is in use in the XRef Stream, ensure then that it
                # is marked free in the XRef Table.
                if r._xrefStm[a.idnum][0] in (2,):
                    self.assertTrue(
                        expItems[e][-1],
                        "Item %d should be hid by the XRef Table, but it was "
                        "not." % e,
                    )

    def testIsObjectFree(self):
        """
        Tests the ``PdfFileReader.isObjectFree()` method.
        """
        # TO-DO Find PDF files that feature free-entry lists. We are checking
        # isObjectFree() only against used items.
        inputFiles = (
            "jpeg.pdf",
            "Seige_of_Vicksburg_Sample_OCR.pdf",
            "SF424_page2.pdf",
        )

        for filename in inputFiles:
            filepath = join(self.localDataRoot, filename)
            r = PdfFileReader(join(TEST_DATA_ROOT, filename))
            expItems = self._parseXRefTable(filepath, (0, 1, 3))
            actualItems = list()

            for ref in r.objects(PdfFileReader.R_XTABLE, True):
                actualItems.append(
                    # This is where isObjectFree() gets invoked
                    (ref.idnum, ref.generation, r.isObjectFree(ref))
                )

            r.close()
            expItems = sorted(expItems)
            actualItems = sorted(actualItems)

            self.assertListEqual(expItems, actualItems)

    def testContextManager(self):
        """
        Tests the context manager implementation (the ``with <expr> as
        identifier`` feature) of ``PdfFileReader``.
        """
        inputFiles = (
            "jpeg.pdf",
            "Seige_of_Vicksburg_Sample_OCR.pdf",
            "SF424_page2.pdf",
        )

        for filename in inputFiles:
            r = None

            with PdfFileReader(join(TEST_DATA_ROOT, filename)) as r:
                # Test assertions not strictly related to the whole test case
                self.assertEqual(filename, basename(r.filepath))
                self.assertFalse(r.isClosed)

            self.assertTrue(r.isClosed)

    @staticmethod
    def _parseXRefTable(filepath, mask=tuple()):
        """
        Parses a Cross-Reference Table, such as the sampled ones used for
        testing.

        :param filepath: file path where the table is stored in.
        :param mask: a list of fields' indices indicating which fields are to
            be returned. For example, ``(0, 2, 3)`` indicates that only the
            ``id``, ``byteOffset`` and ``isFree`` fields have to be returned.
        :return: an iterable of items of the form
            ``(id, gen, byteOffset, isFree)`` if ``mask`` hasn't been set,
            otherwise an iterable of all the items ``mask`` has specified.
        """
        startid = None
        expecteditems = None
        itemssofar = None

        if not mask:
            mask = tuple(range(4))

        with open(filepath, "r") as instream:
            for line in instream:
                if not line or line.isspace() or line.startswith("%"):
                    continue

                tokens = line.strip().split()

                # We are beginning a new sub reference section
                if len(tokens) == 2:
                    if itemssofar != expecteditems:
                        raise ValueError(
                            'Line "%d %d" specified %d items, %d read'  # pylint: disable=bad-string-format-type
                            % (startid, expecteditems, expecteditems, itemssofar)
                        )

                    startid = int(tokens[0])
                    expecteditems = int(tokens[1])
                    itemssofar = 0
                elif len(tokens) == 3:  # New object info to add
                    # We yield an (id, gen, byte offset) tuple
                    output = (
                        startid + itemssofar,
                        int(tokens[1]),
                        int(tokens[0]),
                        tokens[2] == "f",
                    )
                    yield tuple(output[s] for s in mask)

                    itemssofar += 1
                else:
                    raise ValueError("Unexpected token in %s" % filepath)

    def testProperties(self):
        """
        The switch from PyPDF2 to PyPDF4 sees many stylistic changes, including
        the use of the ``@property`` decorator (where possible) and pruning out
        of unnecessary arguments to ``property()`` as a function.
        In some cases, functions that previously had a ``@property`` accessor
        have it no more (to remove duplicate accesses).

        This test ensures that the two styles, the older and the newer, are
        functionally equivalent.
        """
        properties = (
            "documentInfo",
            "xmpMetadata",
            "numPages",
            "pages",
            "pageLayout",
            "pageMode",
            "isEncrypted",
        )
        methods = ("getNamedDestinations", "getOutlines")

        for p in properties:
            self.assertIsInstance(getattr(PdfFileReader, p), property)

        for m in methods:
            self.assertTrue(
                hasattr(PdfFileReader, m),
                "%s() is not part of %s" % (m, PdfFileReader.__name__),
            )
            self.assertTrue(
                callable(getattr(PdfFileReader, m)),
                "%s.%s() is not callable" % (PdfFileReader.__name__, m),
            )

    def testAddAttachment(self):
        """
        Tests the addAttachment function for attaching a single file.

        Since the Names array in the EmbeddedFiles dictionary contains both the
        name (string) and indirect object (dictionary) for each file, we have
        to check for two entries per attached file.
        """

        _, testfile = tempfile.mkstemp()

        try:
            # Make PDF with attachment
            with PdfFileReader(join(TEST_DATA_ROOT, "jpeg.pdf")) as reader:
                with PdfFileWriter(testfile) as writer:
                    writer.appendPagesFromReader(reader)
                    with open(
                        join(  # pylint: disable=bad-continuation
                            TEST_DATA_ROOT, "attachment_small.png"
                        ),
                        "rb",  # pylint: disable=bad-continuation  # pylint: disable=bad-continuation
                    ) as attachment_stream:
                        read_data = attachment_stream.read()
                        writer.addAttachment("attachment_small.png", read_data)
                    writer.write()

            # Check for attachment entries
            with PdfFileReader(testfile) as pdf:
                # For caching _cachedObjects data
                pdf.numPages  # pylint: disable=pointless-statement
                for _k, v in pdf._cachedObjects.items():
                    if "/Type" in v:
                        if v["/Type"] == "/Catalog":
                            self.assertIsNotNone(v["/Names"]["/EmbeddedFiles"])
                            real = len(v["/Names"]["/EmbeddedFiles"]["/Names"])
                            self.assertEqual(2, real)
        finally:
            os.remove(testfile)

    def testAttachFiles(self):
        """
        Tests the addAttachment function for attaching multiple files.

        Since the Names array in the EmbeddedFiles dictionary contains both the
        name (string) and indirect object (dictionary) for each file, we have
        to check for two entries per attached file.
        """

        numAttachments = 3
        _, testfile = tempfile.mkstemp()

        try:
            # Make PDF with attachment
            with PdfFileReader(join(TEST_DATA_ROOT, "jpeg.pdf")) as reader:
                with PdfFileWriter(testfile) as writer:
                    writer.appendPagesFromReader(reader)

                    writer.attachFiles(
                        [join(TEST_DATA_ROOT, "attachment_small.png")] * numAttachments
                    )
                    writer.write()

            # Check for attachment entries
            with PdfFileReader(testfile) as pdf:
                # For caching _cachedObjects data
                pdf.numPages  # pylint: disable=pointless-statement
                for _k, v in pdf._cachedObjects.items():
                    if "/Type" in v:
                        if v["/Type"] == "/Catalog":
                            self.assertIsNotNone(v["/Names"]["/EmbeddedFiles"])
                            real = len(v["/Names"]["/EmbeddedFiles"]["/Names"])
                            self.assertEqual(numAttachments * 2, real)
        finally:
            os.remove(testfile)


class AddJsTestCase(unittest.TestCase):
    """ [EXPLAIN THIS CLASS.] """

    def setUp(self):
        """ [EXPLAIN THIS CONVENIENCE.] """
        reader = PdfFileReader(join(TEST_DATA_ROOT, "crazyones.pdf"))
        self.writer = PdfFileWriter(BytesIO(b""))
        self.writer.appendPagesFromReader(reader)

    def testAdd(self):
        """ [EXPLAIN THIS TEST.] """
        self.writer.addJS("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")

        self.assertIn(
            "/Names",
            self.writer._rootObject,
            "addJS should add a name catalog in the root object.",
        )
        self.assertIn(
            "/JavaScript",
            self.writer._rootObject["/Names"],
            "addJS should add a JavaScript name tree under the name catalog.",
        )
        self.assertIn(
            "/JavaScript",
            self.writer._rootObject,
            "addJS should add a JavaScript action to the catalog.",
        )

    def testOverwrite(self):
        """ [EXPLAIN THIS TEST.] """
        self.writer.addJS("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
        first_js = self._getJavascriptName()

        self.writer.addJS("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
        second_js = self._getJavascriptName()

        self.assertNotEqual(
            first_js,
            second_js,
            "addJS should overwrite the previous script in the catalog.",
        )

    def _getJavascriptName(self):
        self.assertIn("/Names", self.writer._rootObject)
        self.assertIn("/JavaScript", self.writer._rootObject["/Names"])
        self.assertIn("/Names", self.writer._rootObject["/Names"]["/JavaScript"])
        return self.writer._rootObject["/Names"]["/JavaScript"]["/Names"][0]
