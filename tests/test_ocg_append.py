"""Test the pypdf._writer module."""

import shutil
from io import BytesIO

from pypdf import (
    PdfReader,
    PdfWriter,
)
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    IndirectObject,
    NameObject,
    TextStringObject,
)

from . import RESOURCE_ROOT, SAMPLE_ROOT

GHOSTSCRIPT_BINARY = shutil.which("gs")

def test_ocg():
    # Trying to get OCGs to append while preserving the OCGs in the original document
    reader = PdfReader(RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR.pdf")
    writer = PdfWriter()
    # writer.append(reader)
    writer.clone_document_from_reader(reader)
    readerAppend = PdfReader(RESOURCE_ROOT / "ocg_map_test.pdf")

    # Trigger the append with the modified merge code that include the OCGs
    writer.append(readerAppend)

    # 2. Add or change metadata values
    # Note: Keys must start with a forward slash (/)
    writer.add_metadata({
        "/Author": "Test Author",
        "/Producer": "Test Producer",
        "/Title": "Test Title",
        "/Subject": "Test Subject",
        "/Keywords": "Test Keywords",
        "/Creator": "Test Creator",
        "/CustomField": "Test CustomField",
    })

    writer.write(SAMPLE_ROOT / "output-ocg_map_test-1.pdf")
def test_ocg_2():
    # Trying to get OCGs to append while preserving the OCGs in the original document
    reader = PdfReader(RESOURCE_ROOT / "ocg_map_test.pdf")
    writer = PdfWriter()
    # writer.append(reader)
    writer.clone_document_from_reader(reader)
    readerAppend = PdfReader(RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR.pdf")

    # Trigger the append with the modified merge code that include the OCGs
    writer.append(readerAppend)

    writer.write(SAMPLE_ROOT / "output-ocg_map_test-2.pdf")

def test_merge_preserves_ocgs() -> None:
    def _reader_with_single_ocg(layer_name: str) -> PdfReader:
        writer = PdfWriter()
        page = writer.add_blank_page(width=100, height=100)

        ocg_ref = writer._add_object(
            DictionaryObject(
                {
                    NameObject("/Type"): NameObject("/OCG"),
                    NameObject("/Name"): TextStringObject(layer_name),
                }
            )
        )

        page[NameObject("/Resources")] = DictionaryObject(
            {
                NameObject("/Properties"): DictionaryObject(
                    {NameObject("/MC0"): ocg_ref}
                )
            }
        )
        content = DecodedStreamObject()
        content.set_data(b"/OC /MC0 BDC\nEMC")
        page[NameObject("/Contents")] = writer._add_object(content)

        writer.root_object[NameObject("/OCProperties")] = writer._add_object(
            DictionaryObject(
                {
                    NameObject("/OCGs"): ArrayObject([ocg_ref]),
                    NameObject("/D"): DictionaryObject(
                        {
                            NameObject("/ON"): ArrayObject([ocg_ref]),
                            NameObject("/Order"): ArrayObject([ocg_ref]),
                        }
                    ),
                }
            )
        )

        buffer = BytesIO()
        writer.write(buffer)
        buffer.seek(0)
        return PdfReader(buffer)

    base_reader = _reader_with_single_ocg("Base Layer")
    import_reader = _reader_with_single_ocg("Imported Layer")

    writer = PdfWriter()
    writer.append(base_reader)
    writer.append(import_reader)

    out = BytesIO()
    writer.write(out)
    out.seek(0)
    merged_reader = PdfReader(out)

    oc_properties = merged_reader.root_object["/OCProperties"].get_object()
    assert isinstance(oc_properties, DictionaryObject)
    ocgs = oc_properties["/OCGs"]
    assert isinstance(ocgs, ArrayObject)

    names = set()
    for ref in ocgs:
        assert isinstance(ref, IndirectObject)
        ocg_obj = ref.get_object()
        assert isinstance(ocg_obj, DictionaryObject)
        names.add(str(ocg_obj.get("/Name", "")))
    assert names == {"Base Layer", "Imported Layer"}

    default_config = oc_properties["/D"]
    assert isinstance(default_config, DictionaryObject)
    assert isinstance(default_config.get("/ON"), ArrayObject)
    assert isinstance(default_config.get("/Order"), ArrayObject)
    assert len(default_config["/ON"]) == 2
    assert len(default_config["/Order"]) == 2
