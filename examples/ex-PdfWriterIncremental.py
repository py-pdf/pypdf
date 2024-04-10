#!/usr/bin/env vpython3
import io
from pathlib import Path
from pypdf import PdfReader, PdfWriterIncremental
from pypdf.annotations import Text

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


def main():
    pdf_path = RESOURCE_ROOT / "toy.pdf"
    with open(pdf_path, 'rb') as fp:
        datau = fp.read()
    startdata = len(datau)
    fi = io.BytesIO(datau)
    reader = PdfReader(fi)

    writer = PdfWriterIncremental(reader)

    # Act
    text_annotation = Text(
        text="Hello World\nThis is incremental pdf with annotation!",
        rect=(150, 550, 500, 650),
        open=True,
    )
    #writer.get_root_for_update()
    page = writer.get_page(0)
    writer.add_annotation(page, text_annotation)

    # Assert: You need to inspect the file manually
    with open('toy.pdf', "wb") as fp:
        fp.write(datau)
        fi = io.BytesIO()
        writer.write(fi)
        fp.write(fi.getvalue())

if __name__ == '__main__':
    main()
