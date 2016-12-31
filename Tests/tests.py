import os, sys, unittest

# Configure path environment
TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, 'Resources')

sys.path.append(PROJECT_ROOT)

# Test imports
import unittest
from PyPDF2 import PdfFileReader


class PdfReaderTestCases(unittest.TestCase):
    def test_PdfReaderFileLoad(self):
        '''    Test loading and parsing of a file. Extract text of the file and compare to expected
            textual output. Expected outcome: file loads, text matches expected.
        '''
        with open(os.path.join(RESOURCE_ROOT, 'crazyones.pdf'), 'rb') as inputfile:
            
            # Load PDF file from file
            ipdf = PdfFileReader(inputfile)
            ipdf_p1 = ipdf.getPage(0)
            
            # Retrieve the text of the PDF
            pdftext_file = open(os.path.join(RESOURCE_ROOT, 'crazyones.txt'), 'r')
            pdftext = pdftext_file.read()
            ipdf_p1_text = ipdf_p1.extractText()
            
            # Compare the text of the PDF to a known source
            self.assertEqual(ipdf_p1_text.encode('utf-8', errors='ignore'), pdftext,
                msg='PDF extracted text differs from expected value.\n\nExpected:\n\n%r\n\nExtracted:\n\n%r\n\n'
                    % (pdftext, ipdf_p1_text.encode('utf-8', errors='ignore')))