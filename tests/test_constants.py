"""Test the pypdf.constants module."""
import re
from collections.abc import Callable

import pytest
import pypdf.constants as constants

from pypdf.constants import (
    AnnotationDictionaryAttributes,
    CheckboxRadioButtonAttributes,
    FilterTypeAbbreviations,
    PDF_KEYS,
    CatalogDictionary,
    FieldDictionaryAttributes,
    FileSpecificationDictionaryEntries,
    GraphicsStateParameters,
    InteractiveFormDictEntries,
    OutlineFontFlag,
    UserAccessPermissions,
)
from pypdf.errors import DeprecationError


def test_slash_prefix():
    """
    Naming conventions of PDF_KEYS (constant names) are followed.

    This test function validates if PDF key names follow the required pattern:
    - Starts with a slash "/"
    - Followed by an uppercase letter
    - Contains alphanumeric characters (letters and digits)
    - The attribute name should be a case-insensitive match, with underscores removed
    """
    pattern = re.compile(r"^/[A-Z]+[a-zA-Z0-9]*$")
    deprecated_attributes = {
        FileSpecificationDictionaryEntries: {"Type", "Mac", "Unix", "Cl"},
        FilterTypeAbbreviations: {"AHx"},
        GraphicsStateParameters: {
            "OP", "op", "CA", "ca", "OP_STROKING", "OP_NON_STROKING",
            "CA_STROKING", "CA_NON_STROKING",
        },
        AnnotationDictionaryAttributes: {
            "Type", "Subtype", "Rect", "Contents", "Border", "StructParent"
        },
        InteractiveFormDictEntries: {"Fields", "NeedAppearances", "SigFlags"},
        FieldDictionaryAttributes: {"Parent", "Kids", "Ff", "Opt"},
        CheckboxRadioButtonAttributes: {"Opt"},
    }
    for cls in PDF_KEYS:
        if cls == CatalogDictionary:  # Deprecated
            continue
        for attr in dir(cls):
            if attr in deprecated_attributes.get(cls, set()):
                continue
            # Skip magic methods
            if attr.startswith("__") and attr.endswith("__"):
                continue

            # Skip methods
            constant_value = getattr(cls, attr)
            if isinstance(constant_value, Callable):
                continue

            assert constant_value.startswith("/")
            assert attr.replace("_", "").casefold() == constant_value[1:].casefold()

            # There are a few exceptions that may be lowercase
            if cls == GraphicsStateParameters and attr in ["ca", "op"]:
                continue

            assert pattern.match(constant_value)


def test_user_access_permissions__dict_handling():
    # Value is mix of configurable and reserved bits.
    # Reserved bits should not be part of the dictionary.
    as_dict = UserAccessPermissions(512 + 64 + 8).to_dict()
    assert as_dict == {
        "add_or_modify": False,
        "assemble_doc": False,
        "extract": False,
        "extract_text_and_graphics": True,
        "fill_form_fields": False,
        "modify": True,
        "print": False,
        "print_to_representation": False,
    }

    # Convert the dictionary back to an integer.
    # This should add the reserved bits automatically.
    permissions = UserAccessPermissions.from_dict(as_dict)
    assert permissions == 4294963912

    # Roundtrip for valid dictionary.
    data = {
        "add_or_modify": True,
        "assemble_doc": False,
        "extract": False,
        "extract_text_and_graphics": True,
        "fill_form_fields": False,
        "modify": True,
        "print": False,
        "print_to_representation": True,
    }
    assert UserAccessPermissions.from_dict(data).to_dict() == data

    # Empty inputs.
    assert UserAccessPermissions.from_dict({}) == 4294963392  # Reserved bits.
    assert UserAccessPermissions(0).to_dict() == {
        "add_or_modify": False,
        "assemble_doc": False,
        "extract": False,
        "extract_text_and_graphics": False,
        "fill_form_fields": False,
        "modify": False,
        "print": False,
        "print_to_representation": False,
    }

    # Unknown dictionary keys.
    data = {
        "add_or_modify": True,
        "key1": False,
        "key2": True,
    }
    unknown = {
        "key1": False,
        "key2": True,
    }
    with pytest.raises(
        ValueError,
        match=f"Unknown dictionary keys: {unknown!r}"
    ):
        UserAccessPermissions.from_dict(data)


def test_user_access_permissions__all():
    all_permissions = UserAccessPermissions.all()
    all_int = int(all_permissions)
    all_string = bin(all_permissions)

    assert all_string.startswith("0b")
    assert len(all_string[2:]) == 32  # 32-bit integer

    assert all_int & UserAccessPermissions.R1 == 0
    assert all_int & UserAccessPermissions.R2 == 0
    assert all_int & UserAccessPermissions.PRINT == UserAccessPermissions.PRINT
    assert all_int & UserAccessPermissions.R7 == UserAccessPermissions.R7
    assert all_int & UserAccessPermissions.R31 == UserAccessPermissions.R31


def test_catalog_dictionary():
    with pytest.raises(
        DeprecationError,
        match=(
            r"^CatalogDictionary is deprecated and was removed in pypdf 7\.0\.0\. "
            r"Use CatalogAttributes instead\.$"
        )
    ):
        assert isinstance(CatalogDictionary(), CatalogDictionary)

    with pytest.raises(
        DeprecationError,
        match=(
            r"^CatalogDictionary is deprecated and was removed in pypdf 7\.0\.0\. "
            r"Use CatalogAttributes instead\.$"
        )
    ):
        assert CatalogDictionary.TYPE == "/Type"

    assert CatalogDictionary.__name__ == "CatalogDictionary"

    with pytest.raises(
        AttributeError,
        match="type object 'CatalogDictionary' has no attribute 'INVALID'"
    ):
        assert CatalogDictionary.INVALID != "/INVALID"


@pytest.mark.parametrize(
    ("old_name", "new_name"),
    [("Type", "TYPE"), ("Mac", "MAC"), ("Unix", "UNIX"), ("Cl", "CL")],
)
def test_file_specification_deprecated_attributes(old_name, new_name):
    expected_message = (
        f"FileSpecificationDictionaryEntries.{old_name} is deprecated and will be removed "
        f"in pypdf 7.0.0. Use FileSpecificationDictionaryEntries.{new_name} instead."
    )
    with pytest.warns(DeprecationWarning, match=f"^{re.escape(expected_message)}$"):
        assert getattr(FileSpecificationDictionaryEntries, old_name) == getattr(
            FileSpecificationDictionaryEntries, new_name
        )


@pytest.mark.parametrize(
    ("container", "old_name", "new_name"),
    [
        (FilterTypeAbbreviations, "AHx", "AHX"),
        (GraphicsStateParameters, "OP", "OP_STROKING"),
        (GraphicsStateParameters, "op", "OP_NON_STROKING"),
        (GraphicsStateParameters, "CA", "CA_STROKING"),
        (GraphicsStateParameters, "ca", "CA_NON_STROKING"),
        (AnnotationDictionaryAttributes, "Type", "TYPE"),
        (AnnotationDictionaryAttributes, "Subtype", "SUBTYPE"),
        (AnnotationDictionaryAttributes, "Rect", "RECT"),
        (AnnotationDictionaryAttributes, "Contents", "CONTENTS"),
        (AnnotationDictionaryAttributes, "Border", "BORDER"),
        (AnnotationDictionaryAttributes, "StructParent", "STRUCT_PARENT"),
        (InteractiveFormDictEntries, "Fields", "FIELDS"),
        (InteractiveFormDictEntries, "NeedAppearances", "NEED_APPEARANCES"),
        (InteractiveFormDictEntries, "SigFlags", "SIG_FLAGS"),
        (FieldDictionaryAttributes, "Parent", "PARENT"),
        (FieldDictionaryAttributes, "Kids", "KIDS"),
        (FieldDictionaryAttributes, "Ff", "FF"),
        (FieldDictionaryAttributes, "Opt", "OPT"),
        (FieldDictionaryAttributes.FfBits, "ReadOnly", "READ_ONLY"),
        (FieldDictionaryAttributes.FfBits, "Required", "REQUIRED"),
        (FieldDictionaryAttributes.FfBits, "NoExport", "NO_EXPORT"),
        (FieldDictionaryAttributes.FfBits, "Multiline", "MULTILINE"),
        (FieldDictionaryAttributes.FfBits, "Password", "PASSWORD"),
        (FieldDictionaryAttributes.FfBits, "NoToggleToOff", "NO_TOGGLE_TO_OFF"),
        (FieldDictionaryAttributes.FfBits, "Radio", "RADIO"),
        (FieldDictionaryAttributes.FfBits, "Pushbutton", "PUSHBUTTON"),
        (FieldDictionaryAttributes.FfBits, "Combo", "COMBO"),
        (FieldDictionaryAttributes.FfBits, "Edit", "EDIT"),
        (FieldDictionaryAttributes.FfBits, "Sort", "SORT"),
        (FieldDictionaryAttributes.FfBits, "FileSelect", "FILE_SELECT"),
        (FieldDictionaryAttributes.FfBits, "MultiSelect", "MULTI_SELECT"),
        (FieldDictionaryAttributes.FfBits, "DoNotSpellCheck", "DO_NOT_SPELL_CHECK"),
        (FieldDictionaryAttributes.FfBits, "DoNotScroll", "DO_NOT_SCROLL"),
        (FieldDictionaryAttributes.FfBits, "Comb", "COMB"),
        (FieldDictionaryAttributes.FfBits, "RadiosInUnison", "RADIOS_IN_UNISON"),
        (FieldDictionaryAttributes.FfBits, "RichText", "RICH_TEXT"),
        (FieldDictionaryAttributes.FfBits, "CommitOnSelChange", "COMMIT_ON_SEL_CHANGE"),
        (CheckboxRadioButtonAttributes, "Opt", "OPT"),
        (OutlineFontFlag, "italic", "ITALIC"),
        (OutlineFontFlag, "bold", "BOLD"),
    ],
)
def test_deprecated_constant_attributes(container, old_name, new_name):
    old_qualified_name = f"{container.__qualname__}.{old_name}"
    new_qualified_name = f"{container.__qualname__}.{new_name}"
    expected_message = (
        f"{old_qualified_name} is deprecated and will be removed in pypdf 7.0.0. "
        f"Use {new_qualified_name} instead."
    )
    with pytest.warns(DeprecationWarning, match=f"^{re.escape(expected_message)}$"):
        assert getattr(container, old_name) == getattr(container, new_name)


@pytest.mark.parametrize(
    ("old_name", "new_name"),
    [("TypArguments", "TypeArguments"), ("TypFitArguments", "FitTypes")],
)
def test_deprecated_constant_classes(old_name, new_name):
    expected_message = (
        f"{old_name} is deprecated and will be removed in pypdf 7.0.0. "
        f"Use {new_name} instead."
    )
    with pytest.warns(DeprecationWarning, match=f"^{re.escape(expected_message)}$"):
        assert getattr(constants, old_name) is getattr(constants, new_name)
