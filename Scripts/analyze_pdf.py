#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Help: Run 'analyze_pdf.py -h' in the directory this file resides in
or have a look into _cli().
"""

from PyPDF2 import PdfFileReader
import datetime
import argparse
import os, inspect, ntpath

class Document(object):

    def __init__(self, file):
        self.file = ntpath.basename(file)
        self._reader = PdfFileReader(file)
        self.meta = DocumentMetadata(self._reader.documentInfo)
        self.page_count = self._reader.numPages
        self.text = self._get_text()

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __unicode__(self):
	    return repr(self)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def _get_text(self):
        text = ''
        for i in range(self.page_count):
            text += self._reader.getPage(i).extractText()
        return text


class DocumentMetadata(object):

    def __init__(self, document_info):
        self.creation_date = datetime.datetime.strptime(document_info['/CreationDate'][2:15], "%Y%m%d%H%M%S")
        self.mod_date = datetime.datetime.strptime(document_info['/ModDate'][2:15], "%Y%m%d%H%M%S")
        self.producer = document_info['/Producer']
        self.creator = document_info['/Creator']
        self.author = document_info['/Author']

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __unicode__(self):
	    return repr(self)

    def __str__(self):
        return unicode(self).encode('utf-8')


def _cli():
    p = argparse.ArgumentParser(description='Analyzes a PDF file and writes some of its data into a text file.',
                                epilog='Limitations: The files are expected to exist in the current directory prior to script execution.')
    p.add_argument('-p', '--pages', action='store_true', help='output the page count')
    p.add_argument('-t', '--text', action='store_true', help='output the text content')
    p.add_argument('-v', '--verbose', action='store_true', help='print processing information')
    p.add_argument('input', help='PDF file which shall be analyzed (e.g. example.pdf)')
    p.add_argument('output', help='text file the PDF file data shall be put into (e.g. example.txt)')
    return p.parse_args()

def _extract_pdf_data(verbose, write_page_count, write_text, input, output):
    print('Start analyzing {}...'.format(args.input))
    abs_script_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    abs_input_path = os.path.join(abs_script_path, input)
    abs_output_path = os.path.join(abs_script_path, output)
    in_file = open(abs_input_path, 'rb')
    out_file = open(abs_output_path,'w')
    d = Document(abs_input_path)
    out_file.write("File name: {}\n".format(d.file))
    if verbose == True:
        print('...file name written...')
    if write_page_count == True:
        out_file.write("Page count: {}\n".format(d.page_count))
        if verbose == True:
            print('...page written...')
    if write_text == True:
        out_file.write("Text:\n{}\n".format(d.text))
        if verbose == True:
            print('...text written...')
    in_file.close()
    out_file.close()
    print('...writing into {} completed.'.format(output))

if __name__ == "__main__":
    args = _cli()
    _extract_pdf_data(args.verbose, args.pages, args.text, args.input, args.output)
