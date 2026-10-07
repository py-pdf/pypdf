"""Test the pypdf._configuration module."""
from unittest import mock

import pytest

from pypdf import Configuration, PdfReader, apply_configuration, get_configuration, overwrite_configuration
from pypdf._configuration import (
    CURRENT_CONFIGURATION,
    WARNED_LEGACY_OVERWRITES,
    _determine_jbig2dec_binary,
    apply_legacy_configuration,
)
from tests import RESOURCE_ROOT


def test_configuration__with_overwrites() -> None:
    reference = Configuration()

    no_parameters = Configuration().with_overwrites()
    assert reference == no_parameters
    assert id(reference) != id(no_parameters)

    with_parameters = Configuration().with_overwrites(
        array_based_stream_maximum_output_length=1337,
        jbig2dec_binary="/path/to/my/binary"
    )
    assert with_parameters != reference
    assert with_parameters.array_based_stream_maximum_output_length == 1337
    assert with_parameters.jbig2dec_binary == "/path/to/my/binary"

    with_parameters2 = with_parameters.with_overwrites(page_tree_maximum_entries=42)
    assert with_parameters2 != with_parameters
    assert with_parameters2.array_based_stream_maximum_output_length == 1337
    assert with_parameters2.jbig2dec_binary == "/path/to/my/binary"
    assert with_parameters2.page_tree_maximum_entries == 42


def test_get_configuration() -> None:
    reference = Configuration()

    result = get_configuration()
    assert reference == result
    assert id(reference) != id(result)


def test_overwrite_configuration() -> None:
    old_configuration = CURRENT_CONFIGURATION.get()
    try:
        configuration1 = get_configuration()

        # Nothing to overwrite.
        overwrite_configuration()
        assert get_configuration() == configuration1

        # Do some basic change to make sure that with a clean class, this is reset correctly.
        overwrite_configuration(flate_maximum_columns=10)
        assert get_configuration() == configuration1.with_overwrites(flate_maximum_columns=10)

        # Class passed.
        overwrite_configuration(Configuration().with_overwrites(array_based_stream_maximum_output_length=1337))
        configuration2 = get_configuration()
        assert configuration2 != configuration1
        assert configuration2 == configuration1.with_overwrites(array_based_stream_maximum_output_length=1337)

        # Kwargs passed.
        overwrite_configuration(page_tree_maximum_entries=42)
        configuration3 = get_configuration()
        assert configuration3 != configuration2
        assert configuration3 == configuration2.with_overwrites(page_tree_maximum_entries=42)

        # Both passed.
        overwrite_configuration(
            Configuration().with_overwrites(zlib_maximum_recovery_input_length=7331),
            page_tree_maximum_depth=15
        )
        configuration4 = get_configuration()
        assert configuration4 != configuration3
        assert configuration4 == configuration1.with_overwrites(
            zlib_maximum_recovery_input_length=7331, page_tree_maximum_depth=15
        )
    finally:
        CURRENT_CONFIGURATION.set(old_configuration)


def test_overwrite_configuration__configuration_replaces_current() -> None:
    old_configuration = CURRENT_CONFIGURATION.get()
    try:
        overwrite_configuration(page_tree_maximum_entries=123)

        configuration = Configuration(page_tree_maximum_entries=456)
        overwrite_configuration(configuration)

        assert get_configuration() == configuration
    finally:
        CURRENT_CONFIGURATION.set(old_configuration)


def test_apply_configuration() -> None:
    old_configuration = CURRENT_CONFIGURATION.get()
    try:
        configuration1 = get_configuration()

        # Nothing to overwrite.
        with apply_configuration():
            assert get_configuration() == configuration1
        assert get_configuration() == configuration1

        # Class passed.
        with apply_configuration(Configuration().with_overwrites(array_based_stream_maximum_output_length=1337)):
            configuration2 = get_configuration()
            assert configuration2 == configuration1.with_overwrites(array_based_stream_maximum_output_length=1337)
        assert get_configuration() == configuration1

        # Kwargs passed.
        with apply_configuration(page_tree_maximum_entries=42):
            configuration3 = get_configuration()
            assert configuration3 == configuration1.with_overwrites(page_tree_maximum_entries=42)
        assert get_configuration() == configuration1

        # Both passed.
        with apply_configuration(
                Configuration().with_overwrites(zlib_maximum_recovery_input_length=7331),
                page_tree_maximum_depth=15
        ):
            configuration4 = get_configuration()
            assert configuration4 == configuration1.with_overwrites(
                zlib_maximum_recovery_input_length=7331, page_tree_maximum_depth=15
            )
        assert get_configuration() == configuration1
    finally:
        CURRENT_CONFIGURATION.set(old_configuration)


def test_apply_configuration__nested() -> None:
    old_configuration = CURRENT_CONFIGURATION.get()
    try:
        configuration1 = get_configuration()

        # Nothing to overwrite.
        with apply_configuration():
            assert get_configuration() == configuration1

            with apply_configuration(Configuration().with_overwrites(array_based_stream_maximum_output_length=1337)):
                configuration2 = get_configuration()
                assert configuration2 == configuration1.with_overwrites(array_based_stream_maximum_output_length=1337)

                with apply_configuration(page_tree_maximum_entries=42):
                    configuration3 = get_configuration()
                    assert configuration3 == configuration2.with_overwrites(page_tree_maximum_entries=42)

                    with apply_configuration(page_tree_maximum_entries=99):
                        assert get_configuration() == configuration2.with_overwrites(page_tree_maximum_entries=99)
                    assert get_configuration() == configuration3

                    with apply_configuration(
                        Configuration().with_overwrites(zlib_maximum_recovery_input_length=7331),
                        page_tree_maximum_depth=15
                    ):
                        configuration4 = get_configuration()
                        assert configuration4 == configuration1.with_overwrites(
                            zlib_maximum_recovery_input_length=7331, page_tree_maximum_depth=15
                        )

                    assert get_configuration() == configuration3
                assert get_configuration() == configuration2
            assert get_configuration() == configuration1
        assert get_configuration() == configuration1
    finally:
        CURRENT_CONFIGURATION.set(old_configuration)


def test_apply_configuration__exception() -> None:
    configuration = get_configuration()

    with pytest.raises(RuntimeError), apply_configuration(page_tree_maximum_entries=42):
        assert get_configuration().page_tree_maximum_entries == 42
        raise RuntimeError

    assert get_configuration() == configuration


def test_apply_configuration__nested_exception() -> None:
    configuration = get_configuration()

    with apply_configuration(page_tree_maximum_entries=42):
        with pytest.raises(RuntimeError), apply_configuration(page_tree_maximum_entries=99):
            assert get_configuration().page_tree_maximum_entries == 99
            raise RuntimeError

        assert get_configuration().page_tree_maximum_entries == 42

    assert get_configuration() == configuration


def test_apply_legacy_configuration() -> None:
    WARNED_LEGACY_OVERWRITES.clear()
    try:
        # Nothing changed.
        with mock.patch("pypdf._configuration.overwrite_configuration") as overwrite_mock:
            apply_legacy_configuration()
        overwrite_mock.assert_not_called()

        # JBIG2 binary changed.
        with mock.patch("pypdf.filters.JBIG2DEC_BINARY", "/path/to/my/binary"), \
                pytest.warns(
                    expected_warning=DeprecationWarning,
                    match=(
                            r"^JBIG2DEC_BINARY is deprecated and will be removed in pypdf 7\.0\.0\. "
                            r"Use Configuration\.jbig2dec_binary instead\.$"
                    )
                ), \
                mock.patch("pypdf._configuration.overwrite_configuration") as overwrite_mock:
            apply_legacy_configuration()
        overwrite_mock.assert_called_once_with(jbig2dec_binary="/path/to/my/binary")

        # Second call should not warn.
        with mock.patch("pypdf.filters.JBIG2DEC_BINARY", "/path2/to/my/binary"), \
                mock.patch("pypdf._configuration.overwrite_configuration") as overwrite_mock:
            apply_legacy_configuration()
        overwrite_mock.assert_called_once_with(jbig2dec_binary="/path2/to/my/binary")

        # Regular value changed.
        with mock.patch("pypdf.filters.MAX_DECLARED_STREAM_LENGTH", 42), \
                pytest.warns(
                    expected_warning=DeprecationWarning,
                    match=(
                            r"^MAX_DECLARED_STREAM_LENGTH is deprecated and will be removed in pypdf 7\.0\.0\. "
                            r"Use Configuration\.maximum_declared_stream_length instead\.$"
                    )
                ), \
                mock.patch("pypdf._configuration.overwrite_configuration") as overwrite_mock:
            apply_legacy_configuration()
        overwrite_mock.assert_called_once_with(maximum_declared_stream_length=42)
    finally:
        WARNED_LEGACY_OVERWRITES.clear()


def test_apply_legacy_configuration__multiple_overrides(caplog) -> None:
    WARNED_LEGACY_OVERWRITES.clear()
    try:
        with mock.patch("pypdf.filters.MAX_DECLARED_STREAM_LENGTH", 42), \
                mock.patch("pypdf.filters.LZW_MAX_OUTPUT_LENGTH", 43), \
                mock.patch("pypdf._page.MERGE_CROP_BOX", "trimbox"), \
                mock.patch("pypdf._configuration.overwrite_configuration") as overwrite_mock, \
                pytest.warns(expected_warning=DeprecationWarning, match=r"^\S+ is deprecated and will be removed .+$"):
            apply_legacy_configuration()

        overwrite_mock.assert_called_once_with(
            maximum_declared_stream_length=42,
            lzw_maximum_output_length=43,
            page_merge_box="trimbox",
        )
    finally:
        WARNED_LEGACY_OVERWRITES.clear()


def test_apply_legacy_configuration__from_reader() -> None:
    with mock.patch(
            "pypdf.filters.MAX_DECLARED_STREAM_LENGTH", get_configuration().maximum_declared_stream_length // 2
    ), pytest.warns(
            expected_warning=DeprecationWarning,
            match=(
                r"^MAX_DECLARED_STREAM_LENGTH is deprecated and will be removed in pypdf 7\.0\.0\. "
                r"Use Configuration\.maximum_declared_stream_length instead\.$"
            )
    ):
        PdfReader(RESOURCE_ROOT / "crazyones.pdf")

    with mock.patch(
            "pypdf.filters.MAX_DECLARED_STREAM_LENGTH", get_configuration().maximum_declared_stream_length // 2
    ), apply_configuration(disable_legacy_handling=True):
        PdfReader(RESOURCE_ROOT / "crazyones.pdf")


def test_determine_jbig2dec_binary__cached() -> None:
    _determine_jbig2dec_binary.cache_clear()

    try:
        with mock.patch("shutil.which", return_value="/path/to/jbig2dec") as which_mock:
            assert _determine_jbig2dec_binary() == "/path/to/jbig2dec"
            assert _determine_jbig2dec_binary() == "/path/to/jbig2dec"

        which_mock.assert_called_once_with("jbig2dec")
    finally:
        _determine_jbig2dec_binary.cache_clear()
