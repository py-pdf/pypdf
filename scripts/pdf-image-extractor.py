"""
Extract images from PDFs without resampling or altering.

Adapted from work by Sylvain Pelissier
http://stackoverflow.com/questions/2693820/extract-images-from-pdf-without-resampling-in-python
"""
from __future__ import print_function

import os
import sys

from PIL import Image
from os.path import abspath, dirname, join

PROJECT_ROOT = abspath(
    join(dirname(__file__), os.pardir)
)
sys.path.append(PROJECT_ROOT)

from pypdf import PdfFileReader


def main():
    if len(sys.argv) != 2:
        print("{}: <filepath>".format(sys.argv[0]))
        return 1

    filepath = sys.argv[1].strip()
    r = PdfFileReader(open(filepath, "rb"))
    pageNo = 0

    while (pageNo < r.numPages):
        page = r.getPage(pageNo)

        if '/XObject' in page['/Resources']:
            xObject = page['/Resources']['/XObject'].getObject()

            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                    data = xObject[obj].getData()

                    if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                        mode = "RGB"
                    else:
                        mode = "P"

                    if '/Filter' in xObject[obj]:
                        if xObject[obj]['/Filter'] == '/FlateDecode':
                            img = Image.frombytes(mode, size, data)
                            img.save(obj[1:] + ".png")
                        elif xObject[obj]['/Filter'] == '/DCTDecode':
                            img = open(obj[1:] + ".jpg", "wb")
                            img.write(data)
                            img.close()
                        elif xObject[obj]['/Filter'] == '/JPXDecode':
                            img = open(obj[1:] + ".jp2", "wb")
                            img.write(data)
                            img.close()
                        elif xObject[obj]['/Filter'] == '/CCITTFaxDecode':
                            img = open(obj[1:] + ".tiff", "wb")
                            img.write(data)
                            img.close()
                    else:
                        img = Image.frombytes(mode, size, data)
                        img.save(obj[1:] + ".png")
        else:
            print("No image found.")

        pageNo += 1


if __name__ == '__main__':
    sys.exit(main())
