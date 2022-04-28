"""
Extract images from PDF without resampling or altering.

Adapted from work by Sylvain Pelissier
http://stackoverflow.com/questions/2693820/extract-images-from-pdf-without-resampling-in-python
"""

import sys
from PIL import Image

import PyPDF2

def getColorSpace(obj):
    if '/ColorSpace' not in obj:
        mode = None
    elif obj['/ColorSpace'] == '/DeviceRGB':
            mode = "RGB"
    elif obj['/ColorSpace'] == '/DeviceCMYK':
        mode = "CMYK"
    elif obj['/ColorSpace'] == '/DeviceGray':
        mode = "P"
    else:
        if type(obj['/ColorSpace']) == PyPDF2.generic.ArrayObject:
            if obj['/ColorSpace'][0] == '/ICCBased':
                colorMap = obj['/ColorSpace'][1].getObject()['/N']
                if colorMap == 1:
                    mode = "P"
                elif colorMap == 3:
                    mode = "RGB"
                elif colorMap == 4:
                    mode = "CMYK"
                else:
                    mode = None
            else:
                mode = None
        else:
            mode = None
    return mode

if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print("\nUsage: python {} input_file page_number\n".format(sys.argv[0]))
        sys.exit(1)

    pdf = sys.argv[1]
    input1 = PyPDF2.PdfFileReader(open(pdf, "rb"))
    pageNumber = int(sys.argv[2], 10)

    if pageNumber < 0 or pageNumber >= input1.getNumPages():
        print("Page number must be between 0 and {:d}\n".format(input1.getNumPages()-1))
        sys.exit(1)

    page = input1.getPage(pageNumber)

    if '/XObject' in page['/Resources']:
        xObject = page['/Resources']['/XObject'].getObject()

        for obj in xObject:
            if xObject[obj]['/Subtype'] == '/Image':
                size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                data = xObject[obj].getData()
                mode = getColorSpace(xObject[obj])

                if '/Filter' in xObject[obj]:
                    if xObject[obj]['/Filter'] == '/DCTDecode' or '/DCTDecode' in xObject[obj]['/Filter']:
                        img = open(obj[1:] + ".jpg", "wb")
                        img.write(data)
                    elif xObject[obj]['/Filter'] == '/FlateDecode' or '/FlateDecode' in xObject[obj]['/Filter']:
                        if mode != None:
                            img = Image.frombytes(mode, size, data)
                            if mode == "CMYK":
                                img = img.convert("RGB")
                            img.save(obj[1:] + ".png")
                        else:
                            print("Color map nor supported for Image " + str(obj[1:]))
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
