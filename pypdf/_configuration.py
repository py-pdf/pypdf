"""Configuration value handling."""
import dataclasses
import functools
import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Literal, Optional, Union


@functools.cache
def _determine_jbig2dec_binary() -> Optional[str]:
    """
    Small utility function to determine the `jbig2dec` binary path only once.

    Returns:
        The corresponding binary path if available.
    """
    return shutil.which("jbig2dec")


@dataclasses.dataclass(frozen=True)
class Configuration:
    """
    Configuration used while processing PDF files.

    These limits mostly protect against excessive resource consumption caused by malformed or malicious PDF files.

    .. note::

        Avoid relying on specific implementation details of this class. The main public API consists of the values
        being considered read-only for each instance with the overwrite method to create a new instance with the
        specified values changed.
    """

    maximum_declared_stream_length: int = 75_000_000
    """The maximum allowed declared ``/Length`` value for streams."""
    array_based_stream_maximum_output_length: int = 75_000_000
    """The maximum allowed output length for array-based streams."""

    jbig2_maximum_output_length: int = 75_000_000
    """
    The maximum allowed number of uncompressed bytes during decompression when using the ``/JBIG2Decode`` filter
    (JBIG2 images).
    """
    lzw_maximum_output_length: int = 75_000_000
    """
    The maximum allowed number of uncompressed bytes during decompression when using the ``/LZWDecode`` filter
    (LZW compression).
    """
    run_length_maximum_output_length: int = 75_000_000
    """
    The maximum allowed number of uncompressed bytes during decompression when using the ``/RunLengthDecode`` filter
    (run-length compression).
    """
    zlib_maximum_output_length: int = 75_000_000
    """
    The maximum allowed number of uncompressed bytes during decompression when using the ``/FlateDecode`` filter
    (zlib compression).
    """
    zlib_maximum_recovery_input_length: int = 5_000_000
    """
    The maximum allowed number of bytes to attempt the recovery with when using the ``/FlateDecode`` filter
    (zlib compression).
    """

    flate_maximum_columns: int = 250_000
    """The maximum allowed number of columns when using the ``/FlateDecode`` filter."""
    flate_maximum_row_length: int = 4_000_000
    """The maximum allowed row length when using the ``/FlateDecode`` filter."""

    image_maximum_buffer_size: int = 75_000_000
    """The maximum allowed number of bytes to allocate for images."""

    xmp_maximum_input_length: int = 5_000_000
    """The maximum allowed actual decompressed stream length in bytes for XMP data."""
    xmp_maximum_element_count: int = 100_000
    """The maximum allowed number of elements for XMP data."""

    outline_maximum_entries: int = 100_000
    """The maximum allowed number of outline entries."""
    outline_maximum_depth: int = 100
    """The maximum allowed depth for outline entries."""

    page_tree_maximum_entries: int = 100_000
    """The maximum allowed number of entries in the page tree."""
    page_tree_maximum_depth: int = 100
    """The maximum allowed depth of the page tree."""

    xform_maximum_invocations_per_extraction: int = 5_000
    """The maximum allowed number of ``/XObject`` forms per page during text extraction."""

    jbig2dec_binary: Optional[str] = dataclasses.field(default_factory=_determine_jbig2dec_binary)
    """
    The location of the ``jbig2dec`` binary.

    This either is a string holding the path to the binary, or ``None`` if the binary could not be found
    or the binary should not be called.
    """

    page_merge_box: Literal["cropbox", "trimbox"] = "cropbox"  # pypdf <= 3.4.0 used "trimbox"
    """The page box to use during merge."""

    disable_legacy_handling: bool = False
    """
    Temporary configuration value for applications which do not rely on old overwrites and thus
    are able to skip legacy handling.

    This disables looking for changes of the old constants during each initialization of the reader
    class. Please note that while this reduces the required overhead, it will disable all related
    deprecation warnings/errors. Setting this flag while legacy constants are intentionally being
    modified is unsupported/incorrect.

    After the deprecation period, this configuration value will be removed with its own deprecation
    period as well.
    """

    def with_overwrites(self, **kwargs: Any) -> "Configuration":
        """
        Creates a new configuration with the specified values overwritten.

        Args:
            **kwargs: Configuration field names and their new values.

        Returns:
            A new configuration with the specified values overwritten.
        """
        return dataclasses.replace(self, **kwargs)


# A default configuration without any value changes.
DEFAULT_CONFIGURATION = Configuration()

# The current configuration.
CURRENT_CONFIGURATION: ContextVar[Configuration] = ContextVar(
    "pypdf_configuration",
    default=DEFAULT_CONFIGURATION,
)


def get_configuration() -> Configuration:
    """
    Get the current configuration.

    Returns:
        The current configuration.
    """
    return CURRENT_CONFIGURATION.get()


def _build_configuration(
    configuration: Optional[Configuration],
    overwrites: dict[str, Any],
) -> Configuration:
    """
    Utility function to build a new configuration from the given values.

    Args:
        configuration: A possible explicit configuration to use instead of the current configuration.
        overwrites: Entries to overwrite.

    Returns:
        The generated configuration.
    """
    base = configuration if configuration is not None else get_configuration()
    return base.with_overwrites(**overwrites)


def overwrite_configuration(
    configuration: Optional[Configuration] = None,
    **overwrites: Any,
) -> Configuration:
    """
    Overwrite the configuration for the current execution context.

    Args:
        configuration: A direct configuration instance to use.
        **overwrites: Configuration parameters to overwrite in the current or given configuration.

    Returns:
        The new configuration.
    """
    new_configuration = _build_configuration(configuration, overwrites)
    CURRENT_CONFIGURATION.set(new_configuration)
    return new_configuration


@contextmanager
def apply_configuration(
    configuration: Optional[Configuration] = None,
    **overwrites: Any,
) -> Iterator[Configuration]:
    """
    Temporarily overwrite the configuration.

    Args:
        configuration: A direct configuration instance to use.
        **overwrites: Configuration parameters to overwrite in the current or given configuration.

    Returns:
        The new configuration.
    """
    new_configuration = _build_configuration(configuration, overwrites)
    token = CURRENT_CONFIGURATION.set(new_configuration)
    try:
        yield new_configuration
    finally:
        CURRENT_CONFIGURATION.reset(token)


# Map the new field names to their legacy names.
LEGACY_NAME_MAPPING = {
    "maximum_declared_stream_length": "MAX_DECLARED_STREAM_LENGTH",
    "array_based_stream_maximum_output_length": "MAX_ARRAY_BASED_STREAM_OUTPUT_LENGTH",
    "jbig2_maximum_output_length": "JBIG2_MAX_OUTPUT_LENGTH",
    "lzw_maximum_output_length": "LZW_MAX_OUTPUT_LENGTH",
    "run_length_maximum_output_length": "RUN_LENGTH_MAX_OUTPUT_LENGTH",
    "zlib_maximum_output_length": "ZLIB_MAX_OUTPUT_LENGTH",
    "zlib_maximum_recovery_input_length": "ZLIB_MAX_RECOVERY_INPUT_LENGTH",
    "flate_maximum_columns": "FLATE_MAX_COLUMNS",
    "flate_maximum_row_length": "FLATE_MAX_ROW_LENGTH",
    "image_maximum_buffer_size": "FLATE_MAX_BUFFER_SIZE",
    "xmp_maximum_input_length": "XMP_MAX_INPUT_LENGTH",
    "xmp_maximum_element_count": "XMP_MAX_ELEMENT_COUNT",
    "jbig2dec_binary": "JBIG2DEC_BINARY",
    "page_merge_box": "MERGE_CROP_BOX",
}

# Record which legacy overwrites have already emitted a warning in the current process/session.
WARNED_LEGACY_OVERWRITES: set[str] = set()


def apply_legacy_configuration() -> Configuration:
    """
    Overwrite the current configuration with the legacy configuration if it has been changed.

    Returns:
        The new configuration which has been applied.
    """
    configuration = get_configuration()
    if configuration.disable_legacy_handling:
        return configuration

    from pypdf._page import MERGE_CROP_BOX  # noqa: PLC0415
    from pypdf.filters import (  # noqa: PLC0415
        FLATE_MAX_BUFFER_SIZE,
        FLATE_MAX_COLUMNS,
        FLATE_MAX_ROW_LENGTH,
        JBIG2_MAX_OUTPUT_LENGTH,
        JBIG2DEC_BINARY,
        LZW_MAX_OUTPUT_LENGTH,
        MAX_ARRAY_BASED_STREAM_OUTPUT_LENGTH,
        MAX_DECLARED_STREAM_LENGTH,
        RUN_LENGTH_MAX_OUTPUT_LENGTH,
        ZLIB_MAX_OUTPUT_LENGTH,
        ZLIB_MAX_RECOVERY_INPUT_LENGTH,
    )
    from pypdf.xmp import XMP_MAX_ELEMENT_COUNT, XMP_MAX_INPUT_LENGTH  # noqa: PLC0415

    legacy_values = {
        "MAX_DECLARED_STREAM_LENGTH": MAX_DECLARED_STREAM_LENGTH,
        "MAX_ARRAY_BASED_STREAM_OUTPUT_LENGTH": MAX_ARRAY_BASED_STREAM_OUTPUT_LENGTH,
        "JBIG2_MAX_OUTPUT_LENGTH": JBIG2_MAX_OUTPUT_LENGTH,
        "LZW_MAX_OUTPUT_LENGTH": LZW_MAX_OUTPUT_LENGTH,
        "RUN_LENGTH_MAX_OUTPUT_LENGTH": RUN_LENGTH_MAX_OUTPUT_LENGTH,
        "ZLIB_MAX_OUTPUT_LENGTH": ZLIB_MAX_OUTPUT_LENGTH,
        "ZLIB_MAX_RECOVERY_INPUT_LENGTH": ZLIB_MAX_RECOVERY_INPUT_LENGTH,
        "FLATE_MAX_COLUMNS": FLATE_MAX_COLUMNS,
        "FLATE_MAX_ROW_LENGTH": FLATE_MAX_ROW_LENGTH,
        "FLATE_MAX_BUFFER_SIZE": FLATE_MAX_BUFFER_SIZE,
        "XMP_MAX_INPUT_LENGTH": XMP_MAX_INPUT_LENGTH,
        "XMP_MAX_ELEMENT_COUNT": XMP_MAX_ELEMENT_COUNT,
        "JBIG2DEC_BINARY": JBIG2DEC_BINARY,
        "MERGE_CROP_BOX": MERGE_CROP_BOX,
    }
    overwrites: dict[str, Union[int, str, None]] = {}

    for field_name, legacy_name in LEGACY_NAME_MAPPING.items():
        legacy_value = legacy_values[legacy_name]

        if legacy_value != getattr(DEFAULT_CONFIGURATION, field_name):
            if legacy_name not in WARNED_LEGACY_OVERWRITES:
                from pypdf._utils import deprecate_with_replacement  # noqa: PLC0415

                deprecate_with_replacement(
                    old_name=legacy_name,
                    new_name=f"Configuration.{field_name}",
                    removed_in="7.0.0",
                )
                WARNED_LEGACY_OVERWRITES.add(legacy_name)

            overwrites[field_name] = legacy_value

    if not overwrites:
        return configuration
    return overwrite_configuration(**overwrites)  # type: ignore[arg-type]
