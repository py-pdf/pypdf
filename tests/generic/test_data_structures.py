"""Test the pypdf.generic._data_structures module."""
import os
import subprocess
import sys
from io import BytesIO
from pathlib import Path
from typing import Callable

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.errors import LimitReachedError
from pypdf.generic import (
    ArrayObject,
    ContentStream,
    DictionaryObject,
    NameObject,
    NullObject,
    RectangleObject,
    StreamObject,
    TreeObject,
)
from tests import RESOURCE_ROOT, get_data_from_url

try:
    import resource
except ImportError:
    resource = None  # type: ignore[assignment]


def test_dictionary_object__get_next_object_position() -> None:
    reader = PdfReader(RESOURCE_ROOT / "crazyones.pdf")

    # reader.xref = {0: {7: 15, 9: 10245, 12: 939, 14: 2999, 16: 4982, 18: 9949, 22: 11160}}
    assert DictionaryObject._get_next_object_position(
        position_before=12345, position_end=999999, generations=list(reader.xref), pdf=reader
    ) == 999999  # No value after 12345 in dictionary
    assert DictionaryObject._get_next_object_position(
        position_before=11111, position_end=999999, generations=list(reader.xref), pdf=reader
    ) == 11160  # First value after 11111 in dictionary.
    assert DictionaryObject._get_next_object_position(
        position_before=42, position_end=999999, generations=list(reader.xref), pdf=reader
    ) == 939  # First value after 42 in dictionary.

    # New generation.
    reader.xref[1] = {7: 42, 24: 15000}
    assert DictionaryObject._get_next_object_position(
        position_before=10, position_end=999999, generations=list(reader.xref), pdf=reader
    ) == 15


def test_tree_object__cyclic_reference(caplog: pytest.LogCaptureFixture) -> None:
    writer = PdfWriter()
    child1_object = DictionaryObject()
    child1 = writer._add_object(child1_object)
    child2 = writer._add_object(DictionaryObject({NameObject("/Next"): child1}))
    child3 = writer._add_object(DictionaryObject({NameObject("/Next"): child2}))
    child1_object[NameObject("/Next")] = child3
    tree = TreeObject()
    tree[NameObject("/First")] = child2
    tree[NameObject("/Last")] = writer._add_object(DictionaryObject())

    assert list(tree.children()) == [child2.get_object(), child1.get_object(), child3.get_object()]
    assert "Detected cycle in outline structure for " in caplog.text


@pytest.mark.enable_socket
def test_array_object__clone_same_object_multiple_times(caplog: pytest.LogCaptureFixture) -> None:
    url = "https://github.com/user-attachments/files/25412858/Draft_OSMF_financial_statement_2013.pdf"
    name = "issue2991.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))

    writer = PdfWriter()
    for page in reader.pages:
        page2 = writer.add_page(page)
        assert page2.mediabox == RectangleObject((0, 0, 595, 841))
    assert caplog.messages == []


def test_array_object__clone_same_stream_multiple_times() -> None:
    writer = PdfWriter()

    # Unique streams.
    stream1 = StreamObject()
    stream1.set_data(b"Hello World!")
    stream2 = StreamObject()
    stream2.set_data(b"Lorem ipsum!")

    # Shared streams.
    shared_streams = [StreamObject() for _ in range(3)]
    for index, shared_stream in enumerate(shared_streams):
        shared_stream.set_data(f"Shared stream {index}".encode())

    # Add to writer.
    writer._add_object(stream1)
    writer._add_object(stream2)
    shared_references = [writer._add_object(shared_stream) for shared_stream in shared_streams]

    # Arrays.
    array1 = ArrayObject([stream1.indirect_reference, *shared_references])
    array2 = ArrayObject([stream2.indirect_reference, *shared_references])

    # Cloned.
    cloned1 = array1.clone(pdf_dest=writer)
    cloned2 = array2.clone(pdf_dest=writer)

    # Nullify one shared object.
    writer._replace_object(shared_references[1].indirect_reference, NullObject())

    # The first entry is always different. The remaining shared entries should be dedicated copies.
    assert cloned1[1:] != cloned2[1:]

    assert ContentStream(stream=array1, pdf=None).get_data() == b"Hello World!\nShared stream 0\nShared stream 2\n"
    assert ContentStream(stream=array2, pdf=None).get_data() == b"Lorem ipsum!\nShared stream 0\nShared stream 2\n"
    assert (
        ContentStream(stream=cloned1, pdf=None).get_data() ==
        b"Hello World!\nShared stream 0\nShared stream 1\nShared stream 2\n"
    )
    assert (
        ContentStream(stream=cloned2, pdf=None).get_data() ==
        b"Lorem ipsum!\nShared stream 0\nShared stream 1\nShared stream 2\n"
    )


@pytest.mark.enable_socket
def test_dictionary_object__read_from_stream__limit() -> None:
    name = "read_from_stream__length_2gb.pdf"
    url = "https://github.com/user-attachments/files/25842437/read_from_stream__length_2gb.pdf"

    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))
    page = reader.pages[0]

    with pytest.raises(
            expected_exception=LimitReachedError,
            match=r"^Declared stream length of 2147483647 exceeds maximum allowed length\.$"
    ):
        page.extract_text()


def _prepare_test_dictionary_object__read_from_stream__no_limit(
        path: Path
) -> tuple[str, dict[str, str], Callable[[], None]]:
    env = os.environ.copy()
    env["COVERAGE_PROCESS_START"] = "pyproject.toml"

    name = "read_from_stream__length_2gb.pdf"
    url = "https://github.com/user-attachments/files/25842437/read_from_stream__length_2gb.pdf"
    data = get_data_from_url(url=url, name=name)
    pdf_path = path / name
    pdf_path.write_bytes(data)
    pdf_path_str = pdf_path.resolve().as_posix()

    try:
        env["PYTHONPATH"] = "." + os.pathsep + env["PYTHONPATH"]
    except KeyError:
        env["PYTHONPATH"] = "."

    def limit_virtual_memory() -> None:
        limit_kb = 1_000_000
        limit_bytes = limit_kb * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))

    return pdf_path_str, env, limit_virtual_memory


@pytest.mark.enable_socket
@pytest.mark.skipif(condition=resource is None, reason="Does not have 'resource' module.")
@pytest.mark.skipif(sys.platform == "darwin", reason="RLIMIT_AS is unreliable.")
def test_dictionary_object__read_from_stream__no_limit(tmp_path: Path) -> None:
    pdf_path_str, env, limit_virtual_memory = _prepare_test_dictionary_object__read_from_stream__no_limit(tmp_path)

    source_file = tmp_path / "script.py"
    source_file.write_text(
        f"""
import sys
from pypdf import filters, PdfReader

filters.MAX_DECLARED_STREAM_LENGTH = sys.maxsize

with open({pdf_path_str!r}, mode="rb") as fd:
    reader = PdfReader(fd)
    print(reader.pages[0].extract_text())
"""
    )

    result = subprocess.run(  # noqa: S603  # We have the control here.
        [sys.executable, source_file],
        capture_output=True,
        env=env,
        text=True,
        preexec_fn=limit_virtual_memory,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.replace("\r", "").endswith("\nMemoryError\n")


@pytest.mark.enable_socket
@pytest.mark.skipif(condition=resource is None, reason="Does not have 'resource' module.")
@pytest.mark.skipif(sys.platform == "darwin", reason="RLIMIT_AS is unreliable.")
def test_dictionary_object__read_from_stream__no_limit__path(tmp_path: Path) -> None:
    pdf_path_str, env, limit_virtual_memory = _prepare_test_dictionary_object__read_from_stream__no_limit(tmp_path)

    source_file = tmp_path / "script.py"
    source_file.write_text(
        f"""
import sys
from pypdf import filters, PdfReader

filters.MAX_DECLARED_STREAM_LENGTH = sys.maxsize

reader = PdfReader({pdf_path_str!r})
print(reader.pages[0].extract_text())
"""
    )

    result = subprocess.run(  # noqa: S603  # We have the control here.
        [sys.executable, source_file],
        capture_output=True,
        env=env,
        text=True,
        preexec_fn=limit_virtual_memory,
    )
    assert result.returncode == 0
    assert result.stdout.replace("\r", "") == "Hello from pypdf\n"
    assert result.stderr == ""


def _get_array_based_buffer(stream_count: int, chunk_bytes: int) -> BytesIO:
    writer = PdfWriter()
    page = writer.add_blank_page(width=10, height=10)

    streams = [ContentStream(stream=None, pdf=writer) for _ in range(stream_count)]
    chunk = b"q\n" + (b"A" * chunk_bytes) + b"\nQ\n"
    for stream in streams:
        stream.set_data(chunk)
    contents = ArrayObject([writer._add_object(stream) for stream in streams])
    page[NameObject("/Contents")] = contents

    buffer = BytesIO()
    writer.write(buffer)
    buffer.flush()
    return buffer


@pytest.mark.timeout(10)
def test_content_stream__array_based__performance() -> None:
    buffer = _get_array_based_buffer(stream_count=10_000, chunk_bytes=7000)
    reader = PdfReader(buffer)
    _ = reader.pages[0].get_contents()


def test_content_stream__array_based__length() -> None:
    buffer = _get_array_based_buffer(stream_count=11_000, chunk_bytes=1)
    reader = PdfReader(buffer)
    with pytest.raises(
            expected_exception=LimitReachedError, match=r"^Array\-based stream has 11000 > 10000 elements\.$"
    ):
        _ = reader.pages[0].get_contents()


@pytest.mark.timeout(10)
def test_content_stream__array_based__output_length() -> None:
    buffer = _get_array_based_buffer(stream_count=10_000, chunk_bytes=8192)
    reader = PdfReader(buffer)
    with pytest.raises(
            expected_exception=LimitReachedError,
            match=r"^Array\-based stream has at least 75003501 > 75000000 output bytes\.$"
    ):
        _ = reader.pages[0].get_contents()
