import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    cast,
)

from ..constants import (
    CatalogAttributes,
)
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

if sys.version_info >= (3, 11):
    pass
else:
    pass

if TYPE_CHECKING:
    from .._doc_common import PdfDocCommon

def _append_unique_indirect(values: ArrayObject, value: PdfObject) -> None:
    """
    Utility function to check if an indirect object is already present in an array
    of indirect objects and append it only if it is not.

    Args:
        values: The array of indirect objects to which the new object should be appended.
        value: The indirect object to be appended if it is not already present in the array.
    """
    if isinstance(value, IndirectObject) and any(
        isinstance(existing, IndirectObject) and existing.idnum == value.idnum
        for existing in values
    ):
        return
    values.append(value)


def _translate_ocg_indirect_object(
    self: Any, obj: Any, trslat: dict[int, int]
) -> Optional[IndirectObject]:
    """
    Merge the pages from the given file into the output file at the
    specified page number.

    Args:
        obj: The object to be translated such as an indirect object from the reader.
        trslat: A dictionary mapping source object IDs to their corresponding
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
    if source_id in trslat:
        return IndirectObject(trslat[source_id], 0, self)
    if isinstance(source_obj, DictionaryObject):
        source_obj.clone(self)
    if source_id not in trslat:
        return None
    return IndirectObject(trslat[source_id], 0, self)


def _map_ocg_array(
    self: Any, values: Any, trslat: dict[int, int]
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
        mapped_ref = _translate_ocg_indirect_object(self, value, trslat)
        if mapped_ref is None:
            continue
        _append_unique_indirect(mapped, mapped_ref)
    return mapped


def _map_ocg_order(self: Any, value: Any, trslat: dict[int, int]) -> Optional[PdfObject]:
    """
    This function recursively maps the order of OCGs from the reader to the writer,
    handling both indirect objects and arrays.

    Args:
        value: The OCG order object from the reader, which can be an indirect object, array, or dictionary.
        trslat: A dictionary mapping source object IDs to their corresponding translated object IDs in the writer.

    Returns:
        The mapped OCG order object for the writer, or None if it cannot be mapped.
    """
    mapped_ref = _translate_ocg_indirect_object(self, value, trslat)
    if mapped_ref is not None:
        return mapped_ref
    if isinstance(value, IndirectObject):
        # Some PDFs store deep /Order branches as indirect arrays or dictionaries.
        # Resolve and map recursively so nested layer trees are preserved.
        try:
            return _map_ocg_order(self, value.get_object(), trslat)
        except Exception:
            return None
    if isinstance(value, ArrayObject):
        mapped = ArrayObject()
        for item in value:
            mapped_item = _map_ocg_order(self, item, trslat)
            # this ensures that only successfully mapped items are included in the final array
            if mapped_item is None:
                continue
            mapped.append(mapped_item)
        return mapped if len(mapped) > 0 else None
    if isinstance(
        value,
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
        return value
    # Handle OCMDs (Optional Content Membership Dictionaries) which are DictionaryObjects
    # These can appear in the Order hierarchy to define visibility logic
    if isinstance(value, DictionaryObject):
        mapped_dict = DictionaryObject()
        for key, val in value.items():
            if key == "/OCGs":
                # Map the OCG references array inside the OCMD
                mapped_array = _map_ocg_array(self, val, trslat)
                if len(mapped_array) == 0:
                    continue
                mapped_dict[key] = mapped_array
                continue
            if not isinstance(val, (ArrayObject, DictionaryObject, IndirectObject)):
                # Copy scalar properties (names, strings, etc.) as-is
                mapped_dict[key] = val
                continue
            mapped_val = _map_ocg_order(self, val, trslat)
            if mapped_val is None:
                continue
            # Recursively map nested structures
            mapped_dict[key] = mapped_val
        return mapped_dict if len(mapped_dict) > 0 else None
    return None


def _map_rbgroups(self: Any, rbgroups: Any, trslat: dict[int, int]) -> Optional[DictionaryObject]:
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
    if isinstance(rbgroups, IndirectObject):
        rbgroups = rbgroups.get_object()
    if not isinstance(rbgroups, DictionaryObject):
        return None
    mapped = DictionaryObject()
    for key, value in rbgroups.items():
        if not isinstance(value, ArrayObject):
            continue
        # Each RBGroup entry is an array of OCG references
        mapped_array = _map_ocg_array(self, value, trslat)
        if len(mapped_array) == 0:
            continue
        mapped[key] = mapped_array
    return mapped if len(mapped) > 0 else None


def _map_config_dict(self: Any, config: Any, trslat: dict[int, int]) -> Optional[DictionaryObject]:
    """
    This function maps the /Config dictionary from the reader to the writer and should
    translate the OCG references within the configuration to their writer equivalents.

    Args:
        config: The /Config dictionary from the reader.
        trslat: A dictionary mapping source object IDs to their corresponding
            translated object IDs in the writer.

    Returns:
        A mapped configuration dictionary with translated OCG references, or None if
        the input is not a valid dictionary or if no mappings are found.
    """
    if not isinstance(config, DictionaryObject):
        return None
    mapped = DictionaryObject()
    for key, value in config.items():
        if key in ("/ON", "/OFF", "/Locked"):
            # These are arrays of OCG references
            mapped_array = _map_ocg_array(self, value, trslat)
            if len(mapped_array) == 0:
                continue
            mapped[key] = mapped_array
            continue
        if key == "/Order":
            # Order can be nested arrays and names
            mapped_order = _map_ocg_order(self, value, trslat)
            if mapped_order is None:
                continue
            mapped[key] = mapped_order
            continue
        if not isinstance(value, (TextStringObject, NameObject, NumberObject, FloatObject, BooleanObject)):
            continue
        # Copy scalar properties as-is
        mapped[key] = value
    return mapped if len(mapped) > 0 else None


def _merge_oc_properties(self: Any, reader: "PdfDocCommon") -> None:
    """
    Merge the OCG properties from the reader into the writer's root object.

    Args:
        reader: The PDF reader containing the source OCG properties.

    This function ensures that the OCGs and their associated properties from the
    reader are preserved in the output PDF by mapping the reader's OCG references
    to the corresponding references in the writer and merging them into the writer's
    root object.
    """
    # Get access to /Root via root_object
    source_root = reader.root_object
    # Using the "OC_PROPERTIES" defined in constants.py
    # if no OCGs then skip this
    if (
        CatalogAttributes.OC_PROPERTIES not in source_root
        or is_null_or_none(source_root[CatalogAttributes.OC_PROPERTIES])
    ):
        return
    trslat = self._id_translated.setdefault(id(reader), {})
    source_oc_properties = cast(
        DictionaryObject, source_root[CatalogAttributes.OC_PROPERTIES].get_object()
    )

    # Get both OCGs and OCMDs from the reader and map them to the writer's references
    source_ocgs = _map_ocg_array(self, source_oc_properties.get("/OCGs"), trslat)
    if len(source_ocgs) == 0:
        return
    if CatalogAttributes.OC_PROPERTIES not in self._root_object or is_null_or_none(
        self._root_object[CatalogAttributes.OC_PROPERTIES]
    ):
        target_oc_properties = DictionaryObject()
        target_oc_properties[NameObject("/OCGs")] = source_ocgs
        self._root_object[NameObject(CatalogAttributes.OC_PROPERTIES)] = self._add_object(
            target_oc_properties
        )
    else:
        target_oc_properties = cast(
            DictionaryObject,
            cast(IndirectObject, self._root_object[CatalogAttributes.OC_PROPERTIES]).get_object(),
        )
        if "/OCGs" not in target_oc_properties:
            target_oc_properties[NameObject("/OCGs")] = ArrayObject()
        target_ocgs = target_oc_properties["/OCGs"]
        if isinstance(target_ocgs, IndirectObject):
            target_ocgs_object = target_ocgs.get_object()
        else:
            target_ocgs_object = target_ocgs
        target_ocgs = cast(ArrayObject, target_ocgs_object)
        for source_ref in source_ocgs:
            _append_unique_indirect(target_ocgs, source_ref)
    source_default = source_oc_properties.get("/D")
    if isinstance(source_default, IndirectObject):
        source_default = source_default.get_object()
    if not isinstance(source_default, DictionaryObject):
        return
    target_oc_properties = cast(
        DictionaryObject,
        self._root_object[CatalogAttributes.OC_PROPERTIES].get_object(),
    )
    target_default = target_oc_properties.get("/D", DictionaryObject())
    if isinstance(target_default, IndirectObject):
        target_default = target_default.get_object()
    target_default = cast(DictionaryObject, target_default)
    for key in ("/ON", "/OFF", "/Locked"):
        mapped = _map_ocg_array(self, source_default.get(key), trslat)
        if len(mapped) == 0:
            continue
        existing = cast(ArrayObject, target_default.get(key, ArrayObject()))
        for mapped_ref in mapped:
            _append_unique_indirect(existing, mapped_ref)
        target_default[NameObject(key)] = existing
    mapped_order = _map_ocg_order(self, source_default.get("/Order"), trslat)
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
    _merge_rb_properties(self, source_oc_properties, target_oc_properties, trslat)

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
        config_obj = config.get_object() if isinstance(config, IndirectObject) else config
        if not isinstance(config_obj, DictionaryObject):
            continue
        mapped_config = _map_config_dict(self, config_obj, trslat)
        if mapped_config is None:
            continue
        mapped_configs.append(self._add_object(mapped_config))
    if len(mapped_configs) == 0:
        return
    if "/Configs" not in target_oc_properties:
        target_oc_properties[NameObject("/Configs")] = mapped_configs
        return
    # Append new configs, avoiding duplicates
    existing_configs = cast(ArrayObject, target_oc_properties["/Configs"])
    for mapped_config in mapped_configs:
        _append_unique_indirect(existing_configs, mapped_config)


# Merge /RBGroups if present (radio-button groups define mutually exclusive OCG sets)
def _merge_rb_properties(
    self: Any,
    source_oc_properties: DictionaryObject,
    target_oc_properties: DictionaryObject,
    trslat: dict[int, int],
) -> None:
    if "/RBGroups" not in source_oc_properties:
        return
    mapped_rbgroups = _map_rbgroups(self, source_oc_properties.get("/RBGroups"), trslat)
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
