"""Test the pypdf._writer and _optional_content_groups (OCGs) functionality."""

from copy import deepcopy
from io import BytesIO
from typing import NoReturn

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    BooleanObject,
    ByteStringObject,
    DictionaryObject,
    FloatObject,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
    PdfObject,
    TextStringObject,
)
from pypdf.generic import _optional_content_groups as ocg
from tests import RESOURCE_ROOT, SAMPLE_ROOT


def _assert_ocg_output(output_path, expected_pages) -> PdfReader:
    # Utility function to check that the output PDF
    # contains expected OCG structures and
    # that the references are correctly preserved.
    output = PdfReader(output_path)
    assert len(output.pages) == expected_pages
    properties = output.root_object["/OCProperties"]
    assert properties["/OCGs"]
    for reference in properties["/OCGs"]:
        assert isinstance(reference, IndirectObject)
        assert reference.pdf is output
        assert reference.get_object()["/Type"] == "/OCG"
    return output


def test_ocg_append_metadata_preservation(tmp_path):
    # Trying to get OCGs to append while preserving the OCGs in the original document
    writer = PdfWriter(clone_from=RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR.pdf")

    reader_append = PdfReader(SAMPLE_ROOT / "029-optional-content-groups/ocg_map_test.pdf")

    # 1. Trigger the append with the modified merge code that include the OCGs
    writer.append(reader_append)

    # 2. Add or change metadata values
    writer.add_metadata({
        "/Author": "Test Author",
        "/Producer": "Test Producer",
        "/Title": "Test Title",
        "/Subject": "Test Subject",
        "/Keywords": "Test Keywords",
        "/Creator": "Test Creator",
        "/CustomField": "Test CustomField",
    })

    writer.write(tmp_path / "output-ocg_append_metadata_preservation.pdf")
    # Check that the output PDF contains the expected OCGs and that the references are correctly preserved.
    output = _assert_ocg_output(
        tmp_path / "output-ocg_append_metadata_preservation.pdf", len(writer.pages)
    )
    # Check that the metadata in the output PDF matches the metadata set in the writer.
    for key, value in writer.metadata.items():
        assert output.metadata[key] == value

def test_ocg_append_metadata_reverse_order(tmp_path):
    # Testing the same scenario, but PDFs appended in reverse order
    writer = PdfWriter(clone_from=SAMPLE_ROOT / "029-optional-content-groups/ocg_map_test.pdf")

    reader_append = PdfReader(RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR.pdf")

    # 1.Trigger the append with the modified merge code that include the OCGs
    writer.append(reader_append)

    # 2. Add or change metadata values
    writer.add_metadata({
        "/Author": "Test Author",
        "/Producer": "Test Producer",
        "/Title": "Test Title",
        "/Subject": "Test Subject",
        "/Keywords": "Test Keywords",
        "/Creator": "Test Creator",
        "/CustomField": "Test CustomField",
    })

    writer.write(tmp_path / "output-ocg_append_metadata_reverse_order.pdf")
    # Check that the output PDF contains the expected OCGs and that the references are correctly preserved.
    output = _assert_ocg_output(
        tmp_path / "output-ocg_append_metadata_reverse_order.pdf", len(writer.pages)
    )
    # Check that the metadata in the output PDF matches the metadata set in the writer.
    for key, value in writer.metadata.items():
        assert output.metadata[key] == value

def test_ocg_insert_with_merge(tmp_path):
    # This test is meant to output a PDF that is comparable to the test_workflows.py
    # "test_merge_output" test of expected vs actual size. Though it might be different due to
    # the metadata being preserved.
    # Should be named "Seige_of_Vicksburg_Sample_OCR-crazyones-merged.pdf" in the Resource root
    # or https://github.com/py-pdf/pypdf/blob/main/resources/Seige_of_Vicksburg_Sample_OCR-crazyones-merged.pdf
    writer = PdfWriter(clone_from=RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR.pdf")

    reader_append = PdfReader(RESOURCE_ROOT / "crazyones.pdf")

    # Trigger the append with the modified merge code that include the OCGs
    writer.merge(1, reader_append)

    writer.write(tmp_path / "output-ocg_insert_with_merge.pdf")
    # Check that the output PDF contains the expected OCGs and that the references are correctly preserved.
    _assert_ocg_output(tmp_path / "output-ocg_insert_with_merge.pdf", len(writer.pages))

def test_ocg_insert_with_merge_no_clone(tmp_path):
    # This test is meant to output a PDF that is comparable to the test_workflows.py output
    # but without the old metadata preserved by "clone_from" parameter and
    # results in a differing file size.
    # The difference between the following for
    # the test_workflows.py "test_merge_output" test:
    # cloning which preserves metadata: 220,005
    # no cloning, metadata not preserved: 217,997
    writer = PdfWriter()
    writer.append(RESOURCE_ROOT / "Seige_of_Vicksburg_Sample_OCR.pdf")

    reader_append = PdfReader(RESOURCE_ROOT / "crazyones.pdf")

    # Trigger the append with the modified merge code that include the OCGs
    writer.merge(1, reader_append)

    writer.write(tmp_path / "output-ocg_insert_with_merge_no_clone.pdf")
    # Check that the output PDF contains the expected OCGs and that the references are correctly preserved.
    _assert_ocg_output(tmp_path / "output-ocg_insert_with_merge_no_clone.pdf", len(writer.pages))

@pytest.fixture
def ocg_objects():
    # Create a source PDF with OCGs and prepare a writer for translation tests.
    source = PdfWriter()
    references = ArrayObject([
        source._add_object(DictionaryObject({
            NameObject("/Type"): NameObject("/OCG"),
            NameObject("/Name"): TextStringObject(name),
        }))
        for name in ("Roads", "Labels")
    ])
    writer = PdfWriter()
    mapping = writer._id_translated.setdefault(id(source), {})
    return source, writer, references, mapping


def test_ocg_translate_and_deduplicate(ocg_objects):
    # test the translation and deduplication of OCG indirect objects
    _, writer, references, mapping = ocg_objects
    translated = ocg._translate_ocg_indirect_object(writer, references[0], mapping)
    assert translated.pdf is writer
    assert translated.get_object()["/Name"] == "Roads"
    assert ocg._translate_ocg_indirect_object(writer, references[0], mapping) == translated
    assert ocg._translate_ocg_indirect_object(writer, references[0].get_object(), mapping) == translated
    assert ocg._translate_ocg_indirect_object(writer, DictionaryObject(), mapping) is None
    assert ocg._translate_ocg_indirect_object(writer, NullObject(), mapping) is None
    values = ArrayObject([TextStringObject("label"), translated])
    ocg._append_unique_indirect_reference(values, translated)
    ocg._append_unique_indirect_reference(values, TextStringObject("another label"))
    assert values == ["label", translated, "another label"]


@pytest.mark.parametrize("value", [None, NullObject(), DictionaryObject()])
def test_ocg_reference_array_invalid(value, ocg_objects):
    # test that invalid OCG reference arrays are mapped to an empty list
    _, writer, _, mapping = ocg_objects
    assert ocg._map_ocg_reference_array(writer, value, mapping) == []


def test_ocg_reference_array_translation(ocg_objects):
    # test that valid OCG reference arrays are correctly translated and deduplicated
    source, writer, references, mapping = ocg_objects
    values = source._add_object(ArrayObject([references[0], NullObject(), references[0], references[1]]))
    mapped = ocg._map_ocg_reference_array(writer, values, mapping)
    assert [reference.get_object()["/Name"] for reference in mapped] == ["Roads", "Labels"]
    assert all(reference.pdf is writer for reference in mapped)
    assert ocg._translate_ocg_indirect_object(writer, source._add_object(NumberObject(1)), mapping) is None


@pytest.mark.parametrize("value", [
    TextStringObject("Layers"), ByteStringObject(b"Layers"), NameObject("/View"),
    NumberObject(1), FloatObject(1.5), BooleanObject(True), NullObject(),
])
def test_ocg_order_scalar(value, ocg_objects):
    # test that scalar values in the OCG order structure are returned as-is
    _, writer, _, mapping = ocg_objects
    assert ocg._map_ocg_order_structure(writer, value, mapping) is value


def test_ocg_order_nested_structures(ocg_objects):
    # test that nested structures in the OCG order are correctly mapped and translated
    source, writer, references, mapping = ocg_objects
    order = ArrayObject([
        TextStringObject("Layers"), references[0],
        source._add_object(ArrayObject([references[1], ArrayObject()])),
        DictionaryObject({
            NameObject("/Type"): NameObject("/OCMD"),
            NameObject("/OCGs"): references,
            NameObject("/VE"): ArrayObject([NameObject("/And"), references[0]]),
            NameObject("/Empty"): ArrayObject(),
        }),
    ])
    mapped = ocg._map_ocg_order_structure(writer, order, mapping)
    assert mapped[0] == "Layers"
    assert mapped[1].get_object()["/Name"] == "Roads"
    assert mapped[2][0].get_object()["/Name"] == "Labels"
    assert mapped[3]["/Type"] == "/OCMD"
    assert mapped[3]["/OCGs"] == [mapped[1], mapped[2][0]]
    assert mapped[3]["/VE"] == ["/And", mapped[1]]
    assert "/Empty" not in mapped[3]
    assert ocg._map_ocg_order_structure(writer, None, mapping) is None
    assert ocg._map_ocg_order_structure(writer, ArrayObject(), mapping) is None
    assert ocg._map_ocg_order_structure(writer, DictionaryObject({NameObject("/OCGs"): ArrayObject()}), mapping) is None


def test_ocg_configuration_mapping(ocg_objects):
    # test that OCG configuration dictionaries are correctly mapped and translated
    _, writer, references, mapping = ocg_objects
    configuration = DictionaryObject({
        NameObject(key): references for key in ("/ON", "/OFF", "/Locked")
    })
    configuration.update({
        NameObject("/Order"): ArrayObject([TextStringObject("Layers"), references[0]]),
        NameObject("/Name"): TextStringObject("View"),
        NameObject("/BaseState"): NameObject("/ON"),
        NameObject("/Count"): NumberObject(2),
        NameObject("/Scale"): FloatObject(1.5),
        NameObject("/Enabled"): BooleanObject(True),
        NameObject("/Unsupported"): DictionaryObject(),
    })
    mapped = ocg._map_ocg_configuration(writer, configuration, mapping)
    for key in ("/ON", "/OFF", "/Locked"):
        assert [reference.get_object()["/Name"] for reference in mapped[key]] == ["Roads", "Labels"]
    assert mapped["/Order"][0] == "Layers"
    for key in ("/Name", "/BaseState", "/Count", "/Scale", "/Enabled"):
        assert mapped[key] is configuration[key]
    assert "/Unsupported" not in mapped
    assert ocg._map_ocg_configuration(writer, None, mapping) is None
    assert ocg._map_ocg_configuration(writer, DictionaryObject({
        NameObject("/ON"): ArrayObject(), NameObject("/Order"): ArrayObject(),
    }), mapping) is None


def test_ocg_radio_button_mapping(ocg_objects):
    # test that radio button groups are correctly mapped and translated
    source, writer, references, mapping = ocg_objects
    groups = source._add_object(DictionaryObject({
        NameObject("/Group"): references,
        NameObject("/Empty"): ArrayObject(),
        NameObject("/Invalid"): NullObject(),
    }))
    mapped = ocg._map_radio_button_groups(writer, groups, mapping)
    assert list(mapped) == ["/Group"]
    assert [reference.get_object()["/Name"] for reference in mapped["/Group"]] == ["Roads", "Labels"]
    assert ocg._map_radio_button_groups(writer, None, mapping) is None
    assert ocg._map_radio_button_groups(writer, ArrayObject(), mapping) is None
    assert ocg._map_radio_button_groups(writer, DictionaryObject(), mapping) is None


@pytest.mark.parametrize("target", [
    NullObject(), NumberObject(1), DictionaryObject(),
    DictionaryObject({NameObject("/OCGs"): NullObject()}),
])
def test_ocg_target_properties(target, ocg_objects):
    # test that the target OCG properties are correctly retrieved and mapped
    _, writer, references, mapping = ocg_objects
    target = deepcopy(target)
    invalid = isinstance(target, NumberObject) or (isinstance(target, DictionaryObject) and "/OCGs" in target)
    mapped = ocg._map_ocg_reference_array(writer, references, mapping)
    writer.root_object[NameObject("/OCProperties")] = target
    result = ocg._get_target_oc_properties(writer, mapped)
    if invalid:
        assert result is None
        assert writer.root_object["/OCProperties"] is target
    else:
        assert result["/OCGs"] == mapped
        assert writer.root_object["/OCProperties"] is result


@pytest.mark.parametrize(("source_default", "target_default"), [
    (None, None), (NullObject(), None), (DictionaryObject(), NullObject()),
])
def test_ocg_default_invalid(source_default, target_default, ocg_objects):
    # test that invalid default OCG configurations are correctly identified and rejected
    _, writer, _, mapping = ocg_objects
    source = DictionaryObject()
    target = DictionaryObject()
    if source_default is not None:
        source[NameObject("/D")] = source_default
    if target_default is not None:
        target[NameObject("/D")] = target_default
    assert ocg._merge_oc_default(writer, source, target, mapping) is False


@pytest.mark.parametrize("target_order", [None, ArrayObject(), NullObject()])
@pytest.mark.parametrize("source_order_kind", ["missing", "reference", "array"])
def test_ocg_default_merge(target_order, source_order_kind, ocg_objects):
    # test that the default OCG configurations are correctly merged into the target
    source, writer, references, mapping = ocg_objects
    target_order = deepcopy(target_order)
    default = DictionaryObject({
        NameObject("/ON"): references,
        NameObject("/OFF"): ArrayObject([references[1]]),
        NameObject("/Locked"): ArrayObject(),
        NameObject("/BaseState"): NameObject("/OFF"),
        NameObject("/Name"): TextStringObject("Source"),
        NameObject("/Creator"): TextStringObject("Test"),
        NameObject("/Intent"): NameObject("/View"),
        NameObject("/ListMode"): NameObject("/AllPages"),
    })
    if source_order_kind != "missing":
        default[NameObject("/Order")] = (
            ArrayObject([references[0]]) if source_order_kind == "array" else references[0]
        )
    translated = ocg._map_ocg_reference_array(writer, references, mapping)
    target_default = DictionaryObject({
        NameObject("/ON"): writer._add_object(ArrayObject([translated[0]])),
        NameObject("/OFF"): NullObject(),
        NameObject("/Name"): TextStringObject("Target"),
    })
    if target_order is not None:
        target_default[NameObject("/Order")] = writer._add_object(target_order)
    source_properties = DictionaryObject({NameObject("/D"): source._add_object(default)})
    target_properties = DictionaryObject({NameObject("/D"): writer._add_object(target_default)})
    assert ocg._merge_oc_default(writer, source_properties, target_properties, mapping)
    assert target_default["/ON"] == translated
    assert isinstance(target_default["/OFF"], NullObject)
    assert "/Locked" not in target_default
    assert target_default["/Name"] == "Target"
    for key in ("/BaseState", "/Creator", "/Intent", "/ListMode"):
        assert target_default[key] == default[key]
    if isinstance(target_order, NullObject):
        assert isinstance(target_default["/Order"], NullObject)
    elif source_order_kind == "missing":
        if target_order is None:
            assert "/Order" not in target_default
        else:
            assert target_default["/Order"] == []
    else:
        assert target_default["/Order"] == [translated[0]]


@pytest.mark.parametrize("source_configs", [
    None, NullObject(), ArrayObject(), ArrayObject([NullObject(), DictionaryObject()]),
])
def test_ocg_configurations_invalid(source_configs, ocg_objects):
    # test that invalid OCG configurations are correctly ignored and not added to the target
    _, writer, _, mapping = ocg_objects
    source = DictionaryObject()
    if source_configs is not None:
        source[NameObject("/Configs")] = source_configs
    target = DictionaryObject()
    ocg._merge_oc_configurations(writer, source, target, mapping)
    assert "/Configs" not in target


@pytest.mark.parametrize("existing_configs", [None, ArrayObject(), NullObject()])
def test_ocg_configurations_merge(existing_configs, ocg_objects):
    # test that valid OCG configurations are correctly merged into the target
    source, writer, references, mapping = ocg_objects
    configuration = DictionaryObject({
        NameObject("/Name"): TextStringObject("Alternate"),
        NameObject("/OFF"): ArrayObject([references[1]]),
    })
    source_properties = DictionaryObject({NameObject("/Configs"): source._add_object(ArrayObject([
        source._add_object(configuration), configuration,
    ]))})
    target = DictionaryObject()
    if existing_configs is not None:
        target[NameObject("/Configs")] = writer._add_object(existing_configs)
    ocg._merge_oc_configurations(writer, source_properties, target, mapping)
    if isinstance(existing_configs, NullObject):
        assert isinstance(target["/Configs"], NullObject)
    else:
        assert len(target["/Configs"]) == 2
        for reference in target["/Configs"]:
            assert reference.pdf is writer
            assert reference.get_object()["/Name"] == "Alternate"
            assert reference.get_object()["/OFF"][0].get_object()["/Name"] == "Labels"


def test_ocg_radio_button_merge(ocg_objects):
    # test that radio button properties are correctly merged into the target
    _, writer, references, mapping = ocg_objects
    target = DictionaryObject()
    ocg._merge_radio_button_properties(writer, DictionaryObject(), target, mapping)
    ocg._merge_radio_button_properties(
        writer, DictionaryObject({NameObject("/RBGroups"): NullObject()}), target, mapping
    )
    assert target == {}
    source = DictionaryObject({NameObject("/RBGroups"): DictionaryObject({
        NameObject("/Group"): ArrayObject([references[0]]),
    })})
    ocg._merge_radio_button_properties(writer, source, target, mapping)
    first = target["/RBGroups"]["/Group"][0]
    source["/RBGroups"][NameObject("/Group")].append(references[1])
    source["/RBGroups"][NameObject("/Other")] = ArrayObject([references[1]])
    ocg._merge_radio_button_properties(writer, source, target, mapping)
    assert target["/RBGroups"]["/Group"][0] == first
    assert [reference.get_object()["/Name"] for reference in target["/RBGroups"]["/Group"]] == ["Roads", "Labels"]
    assert target["/RBGroups"]["/Other"] == [target["/RBGroups"]["/Group"][1]]


@pytest.mark.parametrize("properties", [
    None, NullObject(), ArrayObject(), DictionaryObject(),
    DictionaryObject({NameObject("/OCGs"): ArrayObject()}),
])
def test_ocg_preserve_invalid_properties(properties):
    # test that invalid OC properties are handled correctly in the target
    # in this case, the properties are either None, NullObject, or an empty structure
    # and should not be added to the target
    source = PdfWriter()
    if properties is not None:
        source.root_object[NameObject("/OCProperties")] = source._add_object(properties)
    stream = BytesIO()
    source.write(stream)
    writer = PdfWriter()
    ocg._preserve_oc_properties(writer, PdfReader(stream))
    assert "/OCProperties" not in writer.root_object


@pytest.mark.parametrize("target_is_invalid", [False, True])
def test_ocg_preserve_without_default(target_is_invalid, ocg_objects):
    # test that OC properties are handled correctly whether the target has
    # or does not have a valid OCProperties dictionary
    source, writer, references, _ = ocg_objects
    source.root_object[NameObject("/OCProperties")] = DictionaryObject({NameObject("/OCGs"): references})
    stream = BytesIO()
    source.write(stream)
    if target_is_invalid:
        writer.root_object[NameObject("/OCProperties")] = NumberObject(1)
    ocg._preserve_oc_properties(writer, PdfReader(stream))
    if target_is_invalid:
        assert writer.root_object["/OCProperties"] == 1
    else:
        assert len(writer.root_object["/OCProperties"]["/OCGs"]) == 2
        assert "/D" not in writer.root_object["/OCProperties"]


@pytest.mark.parametrize("same_reader", [False, True])
def test_ocg_append_round_trip(same_reader, ocg_objects):
    # test that appending a PDF with OCG properties
    # preserves the correct structure and references
    source, writer, references, _ = ocg_objects
    source.add_blank_page(width=100, height=100)
    source.root_object[NameObject("/OCProperties")] = DictionaryObject({
        NameObject("/OCGs"): references,
        NameObject("/D"): DictionaryObject({
            NameObject("/ON"): ArrayObject([references[0]]),
            NameObject("/OFF"): ArrayObject([references[1]]),
            NameObject("/Locked"): ArrayObject([references[1]]),
            NameObject("/Order"): ArrayObject([TextStringObject("Layers"), references]),
            NameObject("/BaseState"): NameObject("/OFF"),
        }),
        NameObject("/Configs"): ArrayObject([DictionaryObject({
            NameObject("/Name"): TextStringObject("Alternate"),
            NameObject("/ON"): ArrayObject([references[1]]),
        })]),
    })
    source_stream = BytesIO()
    source.write(source_stream)
    reader = PdfReader(source_stream)
    writer.append(reader)
    writer.append(reader if same_reader else PdfReader(BytesIO(source_stream.getvalue())))
    output_stream = BytesIO()
    writer.write(output_stream)
    output = _assert_ocg_output(output_stream, 2)
    properties = output.root_object["/OCProperties"]
    assert len(properties["/OCGs"]) == (2 if same_reader else 4)
    roads, labels = properties["/OCGs"][:2]
    other_roads, other_labels = properties["/OCGs"][:2] if same_reader else properties["/OCGs"][2:]
    assert properties["/D"]["/ON"] == ([roads] if same_reader else [roads, other_roads])
    assert properties["/D"]["/OFF"] == ([labels] if same_reader else [labels, other_labels])
    assert properties["/D"]["/Locked"] == ([labels] if same_reader else [labels, other_labels])
    assert properties["/D"]["/BaseState"] == "/OFF"
    assert properties["/D"]["/Order"] == ["Layers", [roads, labels], "Layers", [other_roads, other_labels]]
    assert len(properties["/Configs"]) == 2
    for configuration, expected_label in zip(properties["/Configs"], [labels, other_labels]):
        assert configuration.get_object()["/Name"] == "Alternate"
        assert configuration.get_object()["/ON"] == [expected_label]


def test_ocg_order_unsupported_object(ocg_objects):
    # test that the OCG order mapping returns None for unsupported objects
    _, writer, _, mapping = ocg_objects
    assert ocg._map_ocg_order_structure(writer, PdfObject(), mapping) is None


def test_ocg_order_resolution_failure(monkeypatch, ocg_objects):
    # test that the OCG order mapping returns None when resolution of an indirect object fails
    _, writer, references, mapping = ocg_objects

    def fail_to_resolve(reference) -> NoReturn:
        raise ValueError("Invalid order reference")

    monkeypatch.setattr(ocg, "_translate_ocg_indirect_object", lambda *_args: None)
    monkeypatch.setattr(IndirectObject, "get_object", fail_to_resolve)
    assert ocg._map_ocg_order_structure(writer, references[0], mapping) is None
