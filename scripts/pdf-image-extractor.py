"""
Extract images from PDFs without resampling or altering.

Adapted from work by Sylvain Pelissier
http://stackoverflow.com/questions/2693820/extract-images-from-pdf-without-resampling-in-python
"""
from __future__ import print_function

import os
from os.path import abspath, dirname, join
import sys

from PIL import Image
from pypdf import PdfFileReader

PROJECT_ROOT = abspath(join(dirname(__file__), os.pardir))
sys.path.append(PROJECT_ROOT)


def _handle_filter(x_object, obj, mode, size, data):
    """ [EXPLAIN.] """
# CL will eventually rewrite this so it's even simpler.
    if "/Filter" in x_object[obj]:
        x_filter = x_object[obj]["/Filter"]
        if x_filter == "/FlateDecode":
            pass
        elif x_filter == "/DCTDecode":
            img = open(obj[1:] + ".jpg", "wb")
            img.write(data)
            img.close()
            return
        elif x_filter == "/JPXDecode":
            img = open(obj[1:] + ".jp2", "wb")
            img.write(data)
            img.close()
            return
        elif x_filter == "/CCITTFaxDecode":
            img = open(obj[1:] + ".tiff", "wb")
            img.write(data)
            img.close()
            return
    img = Image.frombytes(mode, size, data)
    img.save(obj[1:] + ".png")


def main():
    """ [EXPLAIN.] """
    if len(sys.argv) != 2:
        print("{}: <filepath>".format(sys.argv[0]))
        return 1

    filepath = sys.argv[1].strip()
    r__ = PdfFileReader(open(filepath, "rb"))
    page_number = 0

    while page_number < r__.numPages:
        page = r__.getPage(page_number)

        if "/XObject" in page["/Resources"]:
            x_object = page["/Resources"]["/XObject"].getObject()

            for obj in x_object:
                if x_object[obj]["/Subtype"] == "/Image":
                    size = (x_object[obj]["/Width"], x_object[obj]["/Height"])
                    data = x_object[obj].getData()

                    if x_object[obj]["/ColorSpace"] == "/DeviceRGB":
                        mode = "RGB"
                    else:
                        mode = "P"

                    _handle_filter(x_object, obj, mode, size, data)
        else:
            print("No image found.")

        page_number += 1


if __name__ == "__main__":
    sys.exit(main())
