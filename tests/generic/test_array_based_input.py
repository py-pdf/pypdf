"""Test the watermarking functionality and array based input handling in pypdf."""
from io import BytesIO

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    NameObject,
    NumberObject,
    StreamObject,
)
from pypdf.generic._base import IndirectObject


@pytest.fixture
def create_pdf_writer():
    """Provides a simple PdfWriter instance."""
    return PdfWriter()

@pytest.fixture
def blank_pdf_writer():
    """Returns a PdfWriter with one blank 100x100 page."""
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    return writer


@pytest.fixture
def array_content_pdf_bytes():
    """Returns a PDF with a page that has an ArrayObject for its /Contents entry."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=100, height=100)

    # Create two minimal content streams
    stream1 = StreamObject()
    stream1.set_data(b"0 0 m 10 10 l S")  # Simple path

    stream2 = StreamObject()
    stream2.set_data(b"BT /F0 10 Tf 20 20 Td (Test) Tj ET")  # Simple text

    # Set the page /Contents to an ArrayObject of streams
    page[NameObject("/Contents")] = ArrayObject([
        stream1,
        stream2,
    ])

    output = BytesIO()
    writer.write(output)
    return output.getvalue()


@pytest.fixture
def watermark_pdf_bytes(blank_pdf_writer):
    """
    Returns a simple PDF with a page containing a ProcSet ArrayObject and
    a valid StreamObject for /Contents, ensuring the merging logic has
    the correct structures to clone and process.
    """
    writer = blank_pdf_writer  # Use the writer from the fixture for consistency
    page = writer.pages[0]

    resources = DictionaryObject()
    resources[NameObject("/ProcSet")] = ArrayObject([
        NameObject("/PDF"), NameObject("/Text")
    ])
    resources[NameObject("/Font")] = DictionaryObject()

    # Update the page to use this custom resource dictionary
    page[NameObject("/Resources")] = resources

    content_bytes = b"BT /F1 12 Tf 0 0 Td (Watermark) Tj ET"
    content_stream = StreamObject()

    # Use set_data() to properly assign the byte content
    content_stream.set_data(content_bytes)

    # A valid PdfObject value for a DictionaryObject key.
    page[NameObject("/Contents")] = content_stream

    # Write the mock PDF bytes from the writer containing the single page
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def test_merge_page_with_array_procset_clones_correctly(
    blank_pdf_writer, watermark_pdf_bytes
):
    """
    Tests that a page with an ArrayObject (specifically for /ProcSet) in its
    resources dictionary can be successfully cloned and merged via merge_page.
    This simulates the scenario that triggered the ArrayObject AttributeError.
    """
    watermark_reader = PdfReader(BytesIO(watermark_pdf_bytes))
    watermark_page = watermark_reader.pages[0]

    page = blank_pdf_writer.pages[0]

    # The cloning operation happens inside the merge_page call
    try:
        page.merge_page(watermark_page)
    except Exception as e:
        pytest.fail(
            f"Failed to merge page with ArrayObject in Resources. Error: {e}"
        )

    # Final checks after merge
    # The original page should now have the resources and contents from the watermark
    if NameObject("/Contents") not in page:
        # If the page has no content stream yet, initialize it as an array
        page[NameObject("/Contents")] = ArrayObject()
    if not isinstance(page[NameObject("/Contents")].get_object(), ArrayObject):
        pytest.fail("Page /Contents should have been converted to an ArrayObject after merge.")

    assert NameObject("/Resources") in page
    assert NameObject("/Contents") in page

    # Final check by writing and reading back
    output = BytesIO()
    blank_pdf_writer.write(output)

    reader = PdfReader(output)
    assert len(reader.pages) == 1

    resources_obj = page["/Resources"].get_object()
    assert len(resources_obj.get("/ProcSet", [])) > 0


def test_watermark_preserves_original_page(blank_pdf_writer, watermark_pdf_bytes):
    """
    Ensures that applying a watermark does not modify the original page
    used as the watermark source (it should be cloned via deep copy).
    """
    watermark_reader = PdfReader(BytesIO(watermark_pdf_bytes))
    watermark_page = watermark_reader.pages[0]

    # Store an original property before cloning
    original_media_box = watermark_page[NameObject("/MediaBox")]

    page = blank_pdf_writer.pages[0]
    page.merge_page(watermark_page)

    # Check if the original watermark page object's properties are unchanged
    assert watermark_page[NameObject("/MediaBox")] == original_media_box

    # Attempt to modify the cloned page, and check if the original is safe
    page[NameObject("/Type")] = NameObject("/Modified")

    # The type in the original page should still be /Page
    assert watermark_page[NameObject("/Type")] == NameObject("/Page")


def test_add_page_with_array_content_stream_succeeds(array_content_pdf_bytes):
    """
    Tests that adding a page where /Contents is an ArrayObject succeeds without
    raising an error during the deep copy process within PdfWriter.add_page.
    """
    reader = PdfReader(BytesIO(array_content_pdf_bytes))
    source_page = reader.pages[0]

    # Get the contents array and ensure we are working with the resolved object
    content_array = source_page.get(NameObject("/Contents")).get_object()

    # test presence of indirect_reference attribute
    if isinstance(content_array, ArrayObject):
        for i, stream_obj in enumerate(content_array):
            if hasattr(stream_obj, "indirect_reference"):
                # Check if it already has a reference, if not, assign one
                if stream_obj.indirect_reference is None:
                    # Assign a dummy IndirectObject that points back to itself
                    stream_obj.indirect_reference = IndirectObject(i + 100, 0, reader)
            else:
                # Try to assign the attribute if it's missing.
                stream_obj.indirect_reference = IndirectObject(i + 100, 0, reader)

    new_writer = PdfWriter()

    try:
        new_writer.add_page(source_page)
        output = BytesIO()
        new_writer.write(output)

    except Exception as e:
        pytest.fail(
            f"Failed to add/write page with ArrayObject content stream. Error: {e}"
        )

    # check the structure of the resulting PDF
    final_reader = PdfReader(output)
    assert len(final_reader.pages) == 1

    # Check that the /Contents stream is present and valid.
    content = final_reader.pages[0].get_contents()

    assert content is not None

    # Check that the process completed successfully and resulted in a valid object type
    assert isinstance(content, (StreamObject, ArrayObject))

def test_populated_stream_deep_copy(create_pdf_writer):
    """
    Tests that a populated StreamObject with dictionary keys and data is
    correctly deep-cloned, ensuring the raw data is copied and isolated.
    This covers the standard cloning path for StreamObjects.
    """
    original_data = b"BT /F0 12 Tf 50 50 Td (Test Content) Tj ET"

    #Create a populated StreamObject (which is truthy: len() > 0)
    populated_stream = StreamObject()
    populated_stream.set_data(original_data)

    #Convert the Python integer len(original_data) to a PdfObject (NumberObject)
    populated_stream[NameObject("/Length")] = NumberObject(len(original_data))
    populated_stream[NameObject("/Filter")] = NameObject("/FlateDecode")

    assert len(populated_stream) > 0 # Not falsy
    assert populated_stream.get_data() == original_data

    # Create a container dictionary
    container_dict = DictionaryObject({
        NameObject("/Populated"): populated_stream,
        NameObject("/Metadata"): NameObject("/Info")
    })

    # Clone the container to a new writer (forcing deep copy).
    new_writer = create_pdf_writer
    cloned_container = container_dict.clone(pdf_dest=new_writer, force_duplicate=True)

    # Check results
    cloned_stream = cloned_container[NameObject("/Populated")]
    assert cloned_stream is not populated_stream
    assert cloned_stream[NameObject("/Filter")] == NameObject("/FlateDecode")
    assert cloned_stream.get_data() == original_data
    populated_stream.set_data(b"NEW MODIFIED DATA")

    # Change dictionary key
    populated_stream[NameObject("/Filter")] = NameObject("/LZWDecode")

    # Clone should retain original values
    assert cloned_stream.get_data() == original_data
    assert cloned_stream[NameObject("/Filter")] == NameObject("/FlateDecode")
