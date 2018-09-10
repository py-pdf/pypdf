"""
Tests PDF primitives from PyPDF4.pdf.
"""
import binascii
import os
import sys
import unittest

from PyPDF4.pdf import PdfFileReader, PdfFileWriter

# Configure path environment
TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, 'Resources')

sys.path.append(PROJECT_ROOT)


class PdfReaderTestCases(unittest.TestCase):
    def testFileLoad(self):
        """
        Test loading and parsing of a file. Extract text of the file and
        compare to expected textual output. Expected outcome: file loads, text
        matches expected.
        """
        with open(
                os.path.join(RESOURCE_ROOT, 'crazyones.pdf'), 'rb'
        ) as inputfile:
            # Load PDF file from file
            ipdf = PdfFileReader(inputfile)
            ipdfP1 = ipdf.getPage(0)

            # Retrieve the text of the PDF
            with open(
                    os.path.join(RESOURCE_ROOT, 'crazyones.txt'), 'rb'
            ) as pdftext_file:
                pdftext = pdftext_file.read()

            ipdf_p1_text = ipdfP1.extractText(). \
                replace('\n', '').encode('utf-8')

            # Compare the text of the PDF to a known source
            self.assertEqual(
                ipdf_p1_text, pdftext,
                msg='PDF extracted text differs from expected value.'
                    '\n\nExpected:\n\n%r\n\nExtracted:\n\n%r\n\n'
                    % (pdftext, ipdf_p1_text)
            )

    def testJpegImage(self):
        '''
        Test loading and parsing of a file. Extract the image of the file and
        compare to expected textual output. Expected outcome: file loads, image
        matches expected.
        '''

        with open(os.path.join(RESOURCE_ROOT, 'jpeg.pdf'), 'rb') as inputfile:
            # Load PDF file from file
            ipdf = PdfFileReader(inputfile)

            # Retrieve the text of the image
            with open(
                    os.path.join(RESOURCE_ROOT, 'jpeg.txt'), 'r'
            ) as pdftext_file:
                imagetext = pdftext_file.read()

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
        ipdf = PdfFileReader(os.path.join(RESOURCE_ROOT, 'crazyones.pdf'))
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
