"""Lempel-Ziv-Welch (LZW) adaptive compression method."""

from typing import List

CLEAR_TABLE_MARKER = 256
EOD_MARKER = 257

# Data encoded using the LZW compression method shall consist of
# a sequence of codes that are 9 to 12 bits long
MAX_CODE_WIDTH = 12


def lzw_encode(data: bytes) -> bytes:
    """
    Encode byte data with LZW compression.

    Taken from PDF 1.7 specs, "7.4.4.2 Details of LZW Encoding".
    """
    max_table_size = 1 << MAX_CODE_WIDTH  # 4096

    # the 258 fixed codes
    table = {bytes([i]): i for i in range(256)}

    next_code = 258
    result_codes = []

    # The encoder shall begin by issuing a clear-table code
    result_codes.append(CLEAR_TABLE_MARKER)

    string = b""
    for int_character in data:
        character = bytes([int_character])
        if string + character in table:
            # Accumulate a sequence of one or more input characters
            # matching a sequence already present in the table.
            # For maximum compression, the encoder looks for the longest
            # such sequence.
            string += character
        else:
            # Emit the code corresponding to that sequence.
            result_codes.append(table[string])

            # Before adding a new entry, check if the table is full
            if len(table) >= max_table_size:
                # Table is full, emit clear-table code and reset
                result_codes.append(CLEAR_TABLE_MARKER)
                table = {bytes([i]): i for i in range(256)}
                next_code = 258
                # bits_per_code will be reset in pack_codes_into_bytes
            else:
                # Add new sequence to the table
                table[string + character] = next_code
                next_code += 1

            string = character

    # Ensure everything actually is encoded
    if string:
        result_codes.append(table[string])

    result_codes.append(EOD_MARKER)

    return pack_codes_into_bytes(result_codes)


def pack_codes_into_bytes(result_codes: List[int]) -> bytes:
    """Convert the result code list into bytes."""
    bits_per_code = 9  # Initially, the code length shall be 9 bits
    max_code = 1 << bits_per_code  # 512
    buffer = 0
    bits_in_buffer = 0
    output = []

    for code in result_codes:
        buffer = (buffer << bits_per_code) | code
        bits_in_buffer += bits_per_code

        # Codes shall be packed into a continuous bit stream, high-order bit
        # first. This stream shall then be divided into bytes, high-order bit
        # first.
        while bits_in_buffer >= 8:
            bits_in_buffer -= 8
            output.append((buffer >> bits_in_buffer) & 0xFF)

        # Handle bits_per_code reset after clear-table code
        if code == CLEAR_TABLE_MARKER:
            bits_per_code = 9
            max_code = 1 << bits_per_code
            continue

        # Whenever both the encoder and the decoder independently (but
        # synchronously) realize that the current code length is no longer
        # sufficient to represent the number of entries in the table, they shall
        # increase the number of bits per code by 1.
        if code >= max_code - 1 and bits_per_code < MAX_CODE_WIDTH:
            bits_per_code += 1
            max_code <<= 1

    # Flush the buffer
    if bits_in_buffer > 0:
        output.append((buffer << (8 - bits_in_buffer)) & 0xFF)

    return bytes(output)
