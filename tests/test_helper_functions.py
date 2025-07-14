"""Test the helper functions in _utils.py"""
from datetime import datetime

import pytest

from pypdf.generic import (
    create_byte_string_object,
    create_date_string_object,
    create_name_object,
    create_number_object,
)


def test_create_number_object_valid_inputs():
    """Test create_number_object with valid inputs."""
    result = create_number_object(5)
    assert result == 5
    assert str(type(result)) == "<class 'pypdf.generic._base.NumberObject'>"

    result = create_number_object(5.5)
    assert result == 5.5
    assert str(type(result)) == "<class 'pypdf.generic._base.FloatObject'>"


def test_create_number_object_invalid_type():
    """Test create_number_object with invalid types to cover line 228."""
    with pytest.raises(TypeError, match="create_number_object expects float"):
        create_number_object("not a number")

    with pytest.raises(TypeError, match="create_number_object expects float"):
        create_number_object([1, 2, 3])

    with pytest.raises(TypeError, match="create_number_object expects float"):
        create_number_object({"key": "value"})


def test_create_number_object_nan_inf():
    """Test create_number_object with NaN and infinity to cover line 231."""
    with pytest.raises(ValueError, match="create_number_object does not accept NaN or infinite values"):
        create_number_object(float("nan"))

    with pytest.raises(ValueError, match="create_number_object does not accept NaN or infinite values"):
        create_number_object(float("inf"))

    with pytest.raises(ValueError, match="create_number_object does not accept NaN or infinite values"):
        create_number_object(float("-inf"))


def test_create_name_object_valid_inputs():
    """Test create_name_object with valid inputs."""
    result = create_name_object("/text/plain")
    assert result == "/text/plain"

    result = create_name_object("text/plain")
    assert result == "/text/plain"


def test_create_name_object_invalid_type():
    """Test create_name_object with invalid types to cover line 250."""
    with pytest.raises(TypeError, match="create_name_object expects str"):
        create_name_object(123)

    with pytest.raises(TypeError, match="create_name_object expects str"):
        create_name_object(["not", "a", "string"])

    with pytest.raises(TypeError, match="create_name_object expects str"):
        create_name_object(None)


def test_create_byte_string_object_valid_inputs():
    """Test create_byte_string_object with valid inputs."""
    test_bytes = b"test bytes"
    result = create_byte_string_object(test_bytes)
    assert result == test_bytes
    assert str(type(result)) == "<class 'pypdf.generic._base.ByteStringObject'>"


def test_create_byte_string_object_invalid_type():
    """Test create_byte_string_object with invalid types to cover line 272."""
    with pytest.raises(TypeError, match="create_byte_string_object expects bytes"):
        create_byte_string_object("not bytes")

    with pytest.raises(TypeError, match="create_byte_string_object expects bytes"):
        create_byte_string_object(123)

    with pytest.raises(TypeError, match="create_byte_string_object expects bytes"):
        create_byte_string_object([1, 2, 3])


def test_create_date_string_object_valid_inputs():
    """Test create_date_string_object with valid inputs."""
    test_date = datetime(2023, 1, 1, 12, 0, 0)
    result = create_date_string_object(test_date)
    expected_str = "D:20230101120000"
    assert result == expected_str
    assert str(type(result)) == "<class 'pypdf.generic._base.TextStringObject'>"


def test_create_date_string_object_invalid_type():
    """Test create_date_string_object with invalid types to cover line 291."""
    with pytest.raises(TypeError, match="create_date_string_object expects datetime"):
        create_date_string_object("not a datetime")

    with pytest.raises(TypeError, match="create_date_string_object expects datetime"):
        create_date_string_object(1234567890)

    with pytest.raises(TypeError, match="create_date_string_object expects datetime"):
        create_date_string_object(None)
