"""Lempel-Ziv-Welch (LZW) adaptive compression method."""

from typing import List


class LzwCodec:
    """Lempel-Ziv-Welch (LZW) adaptive compression codec."""

    CLEAR_TABLE_MARKER = 256  # Special code to indicate table reset
    EOD_MARKER = 257  # End-of-data marker
    MAX_CODE_WIDTH = 12  # Codes can range from 9 to 12 bits

    def __init__(self) -> None:
        """Initialize codec and reset the compression table."""
        self.clear_table()

    def clear_table(self) -> None:
        """Reset the encoding table to initial state with single-byte sequences."""
        self.table = {bytes([i]): i for i in range(256)}
        self.next_code = self.EOD_MARKER + 1

    def encode(self, data: bytes) -> bytes:
        """
        Encode data using the LZW compression algorithm.

        Taken from PDF 1.7 specs, "7.4.4.2 Details of LZW Encoding".
        """
        max_table_size = 1 << self.MAX_CODE_WIDTH  # 4096 entries when fully expanded
        result_codes = []

        # The encoder shall begin by issuing a clear-table code
        result_codes.append(self.CLEAR_TABLE_MARKER)

        current_sequence = b""
        for byte in data:
            next_sequence = current_sequence + bytes([byte])

            if next_sequence in self.table:
                # Extend current sequence if already in the table
                current_sequence = next_sequence
            else:
                # Output code for the current sequence
                result_codes.append(self.table[current_sequence])

                # If the table is full, emit a clear-table command
                if len(self.table) >= max_table_size:
                    result_codes.append(self.CLEAR_TABLE_MARKER)
                    self.clear_table()
                else:
                    # Add the new sequence to the table
                    self.table[next_sequence] = self.next_code
                    self.next_code += 1

                # Reset to the new character
                current_sequence = bytes([byte])

        # Ensure everything actually is encoded
        if current_sequence:
            result_codes.append(self.table[current_sequence])

        result_codes.append(self.EOD_MARKER)

        return self.pack_codes_into_bytes(result_codes)

    def pack_codes_into_bytes(self, result_codes: List[int]) -> bytes:
        """
        Convert the list of result codes into a continuous byte stream, with codes packed as per the current bit-width.
        The bit-width starts at 9 bits and expands as needed.
        """
        bits_per_code = 9  # Initially, the code length shall be 9 bits
        max_code = 1 << bits_per_code  # 512
        buffer = 0  # Temporary storage for bits to be packed into bytes
        bits_in_buffer = 0  # Number of bits currently in the buffer
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

            # After a clear-table marker, reset to 9-bit codes
            if code == self.CLEAR_TABLE_MARKER:
                bits_per_code = 9
                max_code = 1 << bits_per_code
                continue

            # Expand the code width if the next code exceeds the current range
            if code >= max_code - 1 and bits_per_code < self.MAX_CODE_WIDTH:
                bits_per_code += 1
                max_code <<= 1  # Double the range for the new bit-width

        # Flush any remaining bits in the buffer
        if bits_in_buffer > 0:
            output.append((buffer << (8 - bits_in_buffer)) & 0xFF)

        return bytes(output)
