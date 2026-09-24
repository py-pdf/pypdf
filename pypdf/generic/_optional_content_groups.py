from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Optional,
    Union,
    cast,
)

from pypdf._reader import PdfReader

from ..constants import CatalogAttributes
from ._base import (
    BooleanObject,
    ByteStringObject,
    FloatObject,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
    PdfObject,
    TextStringObject,
    is_null_or_none,
)
from ._data_structures import (
    ArrayObject,
    DictionaryObject,
)

if TYPE_CHECKING:
    from .._writer import PdfWriter


_OCG_STATE_KEYS = ("/ON", "/OFF", "/Locked")
_TranslationMap = dict[Union[int, Literal["PreventGC"]], Any]


def _append_unique_indirect(indirectObjArray: ArrayObject, indirectValue: PdfObject) -> None:
    """
    Utility function to check if an indirect object is already present in an array
    of indirect objects and append it only if it is not found in the array.

    Args:
        indirectObjArray: The array of indirect objects to which the new indirect PDFOObject should be appended
            if it is not found.
        indirectValue: The indirect object to be appended if it is not already present in the array.
    """
    if isinstance(indirectValue, IndirectObject) and any(
        isinstance(existing, IndirectObject) and existing.idnum == indirectValue.idnum
        for existing in indirectObjArray
    ):
        return
    indirectObjArray.append(indirectValue)


def _translate_ocg_indirect_object(
    writer: "PdfWriter", obj: PdfObject, source_translated_mapping: _TranslationMap
) -> Optional[IndirectObject]:
    """
    Translates an indirect object from the reader to the writer, ensuring that
    the object is correctly referenced in the output PDF. If the object has
    already been translated, it returns the corresponding indirect object
    in the writer. Otherwise, it clones the object into the writer and updates
    the mapping.

    Args:
        writer: The PdfWriter instance to which the object should be translated.
        obj: The PDF object to be translated. This can be an indirect object
        or a dictionary object with an indirect reference.
        source_translated_mapping: A dictionary mapping source object IDs to their corresponding
            translated object IDs in the writer. This is meant to ensure
            that indirect objects are correctly referenced in the output PDF.
    """
    if isinstance(obj, IndirectObject):
        source_id = obj.idnum
        source_obj = obj.get_object()
    elif isinstance(obj, DictionaryObject) and getattr(obj, "indirect_reference", None):
        source_id = cast(IndirectObject, obj.indirect_reference).idnum
        source_obj = obj
    else:
        return None
    if source_id in source_translated_mapping:
        return IndirectObject(source_translated_mapping[source_id], 0, writer)
    if isinstance(source_obj, DictionaryObject):
        source_obj.clone(writer)
    if source_id not in source_translated_mapping:
        return None
    return IndirectObject(source_translated_mapping[source_id], 0, writer)


def _map_ocg_reference_array(
    writer: "PdfWriter", values: Optional[PdfObject], trslat: _TranslationMap
) -> ArrayObject:
    """
    This function maps an array of OCG indirect objects from the reader to the writer
    using the provided "trslat" dictionary. It ensures that only unique references
    are added to the mapped array.

    Args:
        values: The array of OCG indirect objects from the reader.
        trslat: A dictionary mapping source object IDs to their corresponding
            translated object IDs in the writer. This is meant to ensure
            that indirect objects are correctly referenced in the output PDF.
    """
    mapped = ArrayObject()
    if isinstance(values, IndirectObject):
        values = values.get_object()
    if not isinstance(values, ArrayObject):
        return mapped
    for value in values:
        mapped_reference = _translate_ocg_indirect_object(writer, value, trslat)
        if mapped_reference is None:
            continue
        _append_unique_indirect(mapped, mapped_reference)
    return mapped


def _map_ocg_order_structure(writer: "PdfWriter", order_object: Optional[PdfObject],
                             trslat: _TranslationMap) -> Optional[PdfObject]:
    """
    This function recursively maps the order of OCGs from the reader to the writer,
    handling both indirect objects and arrays.

    Args:
        order_object: The OCG order object from the reader, which can be an indirect object, array, or dictionary.
        trslat: A dictionary mapping source object IDs to their corresponding translated object IDs in the writer.

    Returns:
        The mapped OCG order object for the writer, or None if it cannot be mapped.
    """
    if order_object is None:
        return None
    mapped_reference = _translate_ocg_indirect_object(writer, order_object, trslat)
    if mapped_reference is not None:
        return mapped_reference
    if isinstance(order_object, IndirectObject):
        # Some PDFs store deep /Order branches as indirect arrays or dictionaries.
        # Resolve and map recursively so nested layer trees are preserved.
        try:
            return _map_ocg_order_structure(writer, order_object.get_object(), trslat)
        # If resolving the indirect object fails, return None
        except Exception:
            return None
    if isinstance(order_object, ArrayObject):
        mapped = ArrayObject()
        for item in order_object:
            mapped_item = _map_ocg_order_structure(writer, item, trslat)
            # this ensures that only successfully mapped items are included in the final array
            if mapped_item is None:
                continue
            mapped.append(mapped_item)
        return mapped or None
    # These are types that may appear in the /Order array and should be preserved.
    # NameObject represents a PDF name, such as /Type, and can serve as a
    # dictionary key. TextStringObject represents a layer or group text label.
    if isinstance(
        order_object,
        (
            TextStringObject,
            ByteStringObject,
            NameObject,
            NumberObject,
            FloatObject,
            BooleanObject,
            NullObject,
        ),
    ):
        return order_object
    # Handle OCMDs (Optional Content Membership Dictionaries) which are DictionaryObjects
    # These can appear in the Order hierarchy to define visibility logic
    if isinstance(order_object, DictionaryObject):
        mapped_dict = DictionaryObject()
        for key, value in order_object.items():
            if key == "/OCGs":
                # Map the OCG references array inside the OCMD
                mapped_array = _map_ocg_reference_array(writer, value, trslat)
                if not mapped_array:
                    continue
                mapped_dict[key] = mapped_array
                continue
            if not isinstance(value, (ArrayObject, DictionaryObject, IndirectObject)):
                # Copy scalar properties (names, strings, etc.) as-is
                mapped_dict[key] = value
                continue
            mapped_value = _map_ocg_order_structure(writer, value, trslat)
            if mapped_value is None:
                continue
            # Recursively map nested structures
            mapped_dict[key] = mapped_value
        return mapped_dict or None
    return None


def _map_radio_button_groups(writer: "PdfWriter", rbgroups: Optional[DictionaryObject],
                              trslat: _TranslationMap) -> Optional[DictionaryObject]:
    """
    This function maps the /RBGroups dictionary from the reader to the writer,
    so radio button groups are preserved. It translates OCG references within
    the RBGroups to their writer equivalents.

    Args:
        rbgroups: The /RBGroups dictionary from the reader.
        trslat: A dictionary mapping source object IDs to their corresponding
            translated object IDs in the writer.

    Returns:
        A mapped RBGroups dictionary with translated OCG references, or None if
        the input is not a valid dictionary or if no mappings are found.
    """
    if rbgroups is None:
        return None
    rbgroups_object: Optional[PdfObject] = rbgroups
    if isinstance(rbgroups_object, IndirectObject):
        rbgroups_object = rbgroups_object.get_object()
    if not isinstance(rbgroups_object, DictionaryObject):
        return None
    mapped = DictionaryObject()
    for key, value in rbgroups_object.items():
        if not isinstance(value, ArrayObject):
            continue
        # Each RBGroup entry is an array of OCG references
        mapped_array = _map_ocg_reference_array(writer, value, trslat)
        if not mapped_array:
            continue
        mapped[key] = mapped_array
    return mapped or None


def _map_ocg_configuration(writer: "PdfWriter", configuration: Optional[DictionaryObject],
                           trslat: _TranslationMap) -> Optional[DictionaryObject]:
    """
    This function maps the /Config dictionary from the reader to the writer and should
    translate the OCG references within the configuration to their writer equivalents.

    Args:
        configuration: The /Config dictionary from the reader.
        trslat: A dictionary mapping source object IDs to their corresponding
            translated object IDs in the writer.

    Returns:
        A mapped configuration dictionary with translated OCG references, or None if
        the input is not a valid dictionary or if no mappings are found.
    """
    if not isinstance(configuration, DictionaryObject):
        return None
    mapped = DictionaryObject()
    for key, value in configuration.items():
        if key in _OCG_STATE_KEYS:
            # These are arrays of OCG references
            mapped_array = _map_ocg_reference_array(writer, value, trslat)
            if not mapped_array:
                continue
            mapped[key] = mapped_array
            continue
        if key == "/Order":
            # Order can be nested arrays and names
            mapped_order = _map_ocg_order_structure(writer, value, trslat)
            if mapped_order is None:
                continue
            mapped[key] = mapped_order
            continue
        if not isinstance(value, (TextStringObject, NameObject, NumberObject, FloatObject, BooleanObject)):
            continue
        # Copy scalar properties as-is
        mapped[key] = value
    return mapped or None


def _preserve_oc_properties(writer: "PdfWriter", reader: PdfReader) -> None:
    """
    This function ensures that the OCGs and their associated properties from the
    reader are preserved in the output PDF by mapping the reader's OCG references
    to the corresponding references in the writer and merging them into the writer's
    root object.

    Args:
        writer: The PDF writer where the OCG properties should be preserved.
        reader: The PDF reader containing the source OCG properties.
    """
    source_root = reader.root_object
    # if no OCGs then skip this
    if is_null_or_none(
    source_oc_properties := source_root.get(CatalogAttributes.OC_PROPERTIES)):
        return
    trslat = writer._id_translated.setdefault(id(reader), {})
    source_oc_properties = cast(
        DictionaryObject, source_root[CatalogAttributes.OC_PROPERTIES].get_object()
    )

    # Get both OCGs and OCMDs from the reader and map them to the writer's references
    source_ocgs = _map_ocg_reference_array(writer, source_oc_properties.get("/OCGs"), trslat)
    if not source_ocgs:
        return
    if is_null_or_none(
        target_oc_properties := writer.root_object.get(
            CatalogAttributes.OC_PROPERTIES
        )
    ):
        target_oc_properties = DictionaryObject()
        target_oc_properties[NameObject("/OCGs")] = source_ocgs
        writer.root_object[NameObject(CatalogAttributes.OC_PROPERTIES)] = writer._add_object(
            target_oc_properties
        )
    else:
        if isinstance(target_oc_properties, IndirectObject):
            target_oc_properties = target_oc_properties.get_object()
        if not isinstance(target_oc_properties, DictionaryObject):
            return
        if "/OCGs" not in target_oc_properties:
            target_oc_properties[NameObject("/OCGs")] = ArrayObject()
        target_ocgs = target_oc_properties["/OCGs"]
        if isinstance(target_ocgs, IndirectObject):
            target_ocgs_object = target_ocgs.get_object()
        else:
            target_ocgs_object = target_ocgs
        target_ocgs = cast(ArrayObject, target_ocgs_object)
        for source_reference in source_ocgs:
            _append_unique_indirect(target_ocgs, source_reference)
    source_default = source_oc_properties.get("/D")
    if isinstance(source_default, IndirectObject):
        source_default = source_default.get_object()
    if not isinstance(source_default, DictionaryObject):
        return
    target_oc_properties = cast(
        DictionaryObject,
        writer.root_object[CatalogAttributes.OC_PROPERTIES].get_object(),
    )
    target_default = target_oc_properties.get("/D", DictionaryObject())
    if isinstance(target_default, IndirectObject):
        target_default = target_default.get_object()
    target_default = cast(DictionaryObject, target_default)
    for key in _OCG_STATE_KEYS:
        mapped = _map_ocg_reference_array(writer, source_default.get(key), trslat)
        if not mapped:
            continue
        existing = cast(ArrayObject, target_default.get(key, ArrayObject()))
        for mapped_reference in mapped:
            _append_unique_indirect(existing, mapped_reference)
        target_default[NameObject(key)] = existing
    mapped_order = _map_ocg_order_structure(writer, source_default.get("/Order"), trslat)
    if mapped_order is not None:
        if "/Order" not in target_default:
            target_default[NameObject("/Order")] = ArrayObject()
        target_order = cast(ArrayObject, target_default["/Order"])
        if isinstance(mapped_order, ArrayObject):
            target_order.extend(mapped_order)
        else:
            target_order.append(mapped_order)
    for key in ("/BaseState", "/Intent", "/ListMode", "/Name", "/Creator"):
        if key in source_default and key not in target_default:
            target_default[NameObject(key)] = source_default[key]
    target_oc_properties[NameObject("/D")] = target_default

    # Merge /RBGroups if present (radio-button groups define mutually exclusive OCG sets)
    _merge_radio_button_properties(writer, source_oc_properties, target_oc_properties, trslat)

    # Merge /Configs if present
    if "/Configs" not in source_oc_properties:
        return
    source_configs = source_oc_properties.get("/Configs")
    if isinstance(source_configs, IndirectObject):
        source_configs = source_configs.get_object()
    if not isinstance(source_configs, ArrayObject):
        return
    mapped_configs = ArrayObject()
    for config in source_configs:
        config_obj = config.get_object()
        if not isinstance(config_obj, DictionaryObject):
            continue
        mapped_config = _map_ocg_configuration(writer, config_obj, trslat)
        if mapped_config is None:
            continue
        mapped_configs.append(writer._add_object(mapped_config))
    if not mapped_configs:
        return
    if "/Configs" not in target_oc_properties:
        target_oc_properties[NameObject("/Configs")] = mapped_configs
        return
    # Append new configs, avoiding duplicates
    existing_configs = cast(ArrayObject, target_oc_properties["/Configs"])
    for mapped_config in mapped_configs:
        _append_unique_indirect(existing_configs, mapped_config)

def _merge_radio_button_properties(
    writer: "PdfWriter",
    source_oc_properties: DictionaryObject,
    target_oc_properties: DictionaryObject,
    trslat: _TranslationMap
) -> None:
    """
    Merge radio-button group properties from the source OCG properties into the target OCG properties.

    Args:
        writer: The PDF writer where the OCG properties should be preserved.
        source_oc_properties: The source OCG properties from the reader.
        target_oc_properties: The target OCG properties in the writer.
        trslat: A dictionary mapping source OCG object IDs to writer OCG object IDs.
    """
    if "/RBGroups" not in source_oc_properties:
        return
    mapped_rbgroups = _map_radio_button_groups(writer, source_oc_properties.get("/RBGroups"), trslat)
    if mapped_rbgroups is None:
        return
    if "/RBGroups" not in target_oc_properties:
        target_oc_properties[NameObject("/RBGroups")] = mapped_rbgroups
        return
    # Merge into existing RBGroups
    existing_rbgroups = cast(DictionaryObject, target_oc_properties["/RBGroups"])
    for key, value in mapped_rbgroups.items():
        if key not in existing_rbgroups:
            existing_rbgroups[key] = value
            continue
        # Merge the arrays, avoiding duplicates
        existing_array = cast(ArrayObject, existing_rbgroups[key])
        for item in value:
            _append_unique_indirect(existing_array, item)
