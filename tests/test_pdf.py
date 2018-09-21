"""
Tests PDF primitives from pypdf.pdf.
"""
import binascii
import sys
import unittest

from os.path import abspath, dirname, join, pardir

# Configure path environment
PROJECT_ROOT = abspath(
    join(dirname(__file__), pardir)
)
TESTS_DATA_ROOT = join(PROJECT_ROOT, "tests", "fixture_data")

sys.path.append(PROJECT_ROOT)

from pypdf.pdf import PdfFileReader, PdfFileWriter


class PdfReaderTestCases(unittest.TestCase):
    def testDel(self):
        """
        Tests the ``__del__()`` method of ``PdfFileReader`` and
        ``PdfFileWriter`` ensuring that no exceptions are raised.
        """
        r = PdfFileReader(join(TESTS_DATA_ROOT, "crazyones.pdf"))
        w = PdfFileWriter()

        try:
            # This may generate some collateral warnings in stderr when del r
            # is performed by the GC
            r.__del__()
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(
                False,
                "Exception '%s' was raised in %s.__del__()" %
                (e, PdfFileReader.__name__)
            )

        try:
            w.__del__()
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(
                False,
                "Exception '%s' was raised in %s.__del__()" %
                (e, PdfFileWriter.__name__)
            )

    def testFileLoad(self):
        """
        Test loading and parsing of a file. Extract text of the file and
        compare to expected textual output. Expected outcome: file loads, text
        matches expected.
        """
        with open(
                join(TESTS_DATA_ROOT, 'crazyones.pdf'), 'rb'
        ) as inputfile:
            # Load PDF file from file
            ipdf = PdfFileReader(inputfile)
            ipdfP1 = ipdf.getPage(0)

            # Retrieve the text of the PDF
            with open(
                    join(TESTS_DATA_ROOT, 'crazyones.txt'), 'rb'
            ) as pdftextFile:
                pdftext = pdftextFile.read()

            ipdfP1Text = ipdfP1.extractText().\
                replace('\n', '').encode('utf-8')

            # Compare the text of the PDF to a known source
            self.assertEqual(
                ipdfP1Text, pdftext,
                msg='PDF extracted text differs from expected value.'
                    '\n\nExpected:\n\n%r\n\nExtracted:\n\n%r\n\n'
                    % (pdftext, ipdfP1Text)
            )

    def testJpegImage(self):
        """
        Test loading and parsing of a file. Extract the image of the file and
        compare to expected textual output. Expected outcome: file loads, image
        matches expected.
        """
        with open(join(TESTS_DATA_ROOT, 'jpeg.pdf'), 'rb') as inputfile:
            # Load PDF file from file
            ipdf = PdfFileReader(inputfile)

            # Retrieve the text of the image
            with open(
                    join(TESTS_DATA_ROOT, 'jpeg.txt'), 'r'
            ) as pdftextFile:
                imagetext = pdftextFile.read()

            ipdfP0 = ipdf.getPage(0)
            xObject = ipdfP0['/Resources']['/XObject'].getObject()
            data = xObject['/Im4'].getData()

            # Compare the text of the PDF to a known source
            self.assertEqual(
                binascii.hexlify(data).decode(), imagetext,
                msg='PDF extracted image differs from expected value.'
                    '\n\nExpected:\n\n%r\n\nExtracted:\n\n%r\n\n'
                    % (imagetext, binascii.hexlify(data).decode())
            )

    def testXRefTableObjects(self):
        """
        Ensures that after ``PdfFileReader._parsePdfFile()`` all the indirect
        references from the XRef-Table *only* have been loaded as expected.
        Objects from the free entries list are included as well in the test.

        This case tests the part of ``PdfFileReader.objects()`` responsible for
        generating the Cross-Reference Table entries too.
        """
        self.maxDiff = None
        LOCAL_DATA_ROOT = join(
            TESTS_DATA_ROOT, self.testXRefTableObjects.__name__
        )
        inputFiles = (
            "jpeg.pdf", "GeoBase_NHNC1_Data_Model_UML_EN.pdf",
            "Seige_of_Vicksburg_Sample_OCR.pdf", "SF424_page2.pdf"
        )

        for file in inputFiles:
            filepath = join(TESTS_DATA_ROOT, file)
            xtablepath = join(LOCAL_DATA_ROOT, file)
            r = PdfFileReader(filepath)
            # The two below are (id, gen, byte offset)-valued lists
            actualItems = list()
            expItems = list()

            for ref in r.objects(PdfFileReader.OBJ_XTABLE, True):
                actualItems.append(
                    (ref.idnum, ref.generation,\
                     r._xref[ref.generation][ref.idnum][0])
                )

            actualItems = sorted(actualItems)

            # With this block we artificially read the XRef Table entries that
            # we know belong to filepath, and store them into expItems
            with open(xtablepath, "r") as instream:
                startid = None
                expecteditems = None
                itemssofar = None

                for line in instream:
                    if not line or line.isspace() or line.startswith("%"):
                        continue

                    tokens = line.strip().split()

                    # We are beginning a new sub reference section
                    if len(tokens) == 2:
                        if itemssofar != expecteditems:
                            raise ValueError(
                                "Line \"%d %d\" specified %d items, %d read"
                                % (startid, expecteditems, expecteditems,
                                   itemssofar)
                            )

                        startid = int(tokens[0])
                        expecteditems = int(tokens[1])
                        itemssofar = 0
                    elif len(tokens) == 3:  # New object info to add
                        # We append an (id, gen, byte offset) tuple
                        expItems.append((
                            startid + itemssofar, int(tokens[1]),
                            int(tokens[0])
                        ))
                        itemssofar += 1
                    else:
                        raise ValueError(
                            "Something unexpected was written in %s"
                            % xtablepath
                        )

            expItems = sorted(expItems)
            self.assertListEqual(expItems, actualItems)

    def testProperties(self):
        """
        The switch from PyPDF2 to PyPDF4 sees many stylistic changes, including
        the use of the @property decorator (where possible) and pruning out
        of unnecessary arguments to property() as a function.
        This test ensures that the two styles, the older and the newer, are
        functionally equivalent.
        """
        properties = (
            "documentInfo", "xmpMetadata", "numPages", "namedDestinations",
            "outlines", "pages", "pageLayout", "pageMode", "isEncrypted"
        )

        for p in properties:
            self.assertIsInstance(getattr(PdfFileReader, p), property)


class AddJsTestCase(unittest.TestCase):
    def setUp(self):
        ipdf = PdfFileReader(join(TESTS_DATA_ROOT, 'crazyones.pdf'))
        self.pdfFileWriter = PdfFileWriter()
        self.pdfFileWriter.appendPagesFromReader(ipdf)

    def testAdd(self):
        self.pdfFileWriter.addJS(
            "this.print({bUI:true,bSilent:false,bShrinkToFit:true});"
        )

        self.assertIn(
            '/Names', self.pdfFileWriter._root_object,
            "addJS should add a name catalog in the root object."
        )
        self.assertIn(
            '/JavaScript', self.pdfFileWriter._root_object['/Names'],
            "addJS should add a JavaScript name tree under the name catalog."
        )
        self.assertIn(
            '/OpenAction', self.pdfFileWriter._root_object,
            "addJS should add an OpenAction to the catalog."
        )

    def testOverwrite(self):
        self.pdfFileWriter.addJS(
            "this.print({bUI:true,bSilent:false,bShrinkToFit:true});"
        )
        first_js = self._getJavascriptName()

        self.pdfFileWriter.addJS(
            "this.print({bUI:true,bSilent:false,bShrinkToFit:true});"
        )
        second_js = self._getJavascriptName()

        self.assertNotEqual(
            first_js, second_js,
            "addJS should overwrite the previous script in the catalog."
        )

    def _getJavascriptName(self):
        self.assertIn('/Names', self.pdfFileWriter._root_object)
        self.assertIn(
            '/JavaScript', self.pdfFileWriter._root_object['/Names']
        )
        self.assertIn(
            '/Names',
            self.pdfFileWriter._root_object['/Names']['/JavaScript']
        )
        return self.pdfFileWriter. \
            _root_object['/Names']['/JavaScript']['/Names'][0]
