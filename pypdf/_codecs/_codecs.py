"""
This module is for codecs only.

While the codec implementation can contain details of the PDF specification,
the module should not do any PDF parsing.
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class Codec(ABC):
    """Abstract base class for all codecs."""

    @abstractmethod
    def encode(self, data: bytes) -> bytes:
        """
        Encode the input data.

        Args:
            data: Data to encode.

        Returns:
            Encoded data.
        """

    @abstractmethod
    def decode(self, data: bytes) -> bytes:
        """
        Decode the input data.

        Args:
            data: Data to decode.

        Returns:
            Decoded data.
        """


class LzwCodec(Codec):
    """Lempel-Ziv-Welch (LZW) adaptive compression codec."""

    CLEAR_TABLE_MARKER = 256  # Special code to indicate table reset
    EOD_MARKER = 257  # End-of-data marker
    INITIAL_BITS_PER_CODE = 9  # Initial code bit width
    MAX_BITS_PER_CODE = 12  # Maximum code bit width

    def _initialize_encoding_table(self) -> None:
        """Initialize the encoding table and state to initial conditions."""
        self.table: Dict[bytes, int] = {bytes([i]): i for i in range(256)}
        self.next_code = self.EOD_MARKER + 1
        self.bits_per_code = self.INITIAL_BITS_PER_CODE
        self.max_code_value = (1 << self.bits_per_code) - 1

    def _increase_next_code(self) -> None:
        """Update bits_per_code and max_code_value if necessary."""
        self.next_code += 1
        if (
            self.next_code > self.max_code_value
            and self.bits_per_code < self.MAX_BITS_PER_CODE
        ):
            self.bits_per_code += 1
            self.max_code_value = (1 << self.bits_per_code) - 1

    def encode(self, data: bytes) -> bytes:
        """
        Encode data using the LZW compression algorithm.

        Taken from PDF 1.7 specs, "7.4.4.2 Details of LZW Encoding".
        """
        result_codes: List[int] = []

        # The encoder shall begin by issuing a clear-table code
        result_codes.append(self.CLEAR_TABLE_MARKER)
        self._initialize_encoding_table()

        current_sequence = b""
        for byte in data:
            next_sequence = current_sequence + bytes([byte])

            if next_sequence in self.table:
                # Extend current sequence if already in the table
                current_sequence = next_sequence
            else:
                # Output code for the current sequence
                result_codes.append(self.table[current_sequence])

                # Add the new sequence to the table if there's room
                if self.next_code <= (1 << self.MAX_BITS_PER_CODE) - 1:
                    self.table[next_sequence] = self.next_code
                    self._increase_next_code()
                else:
                    # If the table is full, emit a clear-table command
                    result_codes.append(self.CLEAR_TABLE_MARKER)
                    self._initialize_encoding_table()

                # Start new sequence
                current_sequence = bytes([byte])

        # Ensure everything actually is encoded
        if current_sequence:
            result_codes.append(self.table[current_sequence])
        result_codes.append(self.EOD_MARKER)

        return self._pack_codes_into_bytes(result_codes)

    def _pack_codes_into_bytes(self, codes: List[int]) -> bytes:
        """
        Convert the list of result codes into a continuous byte stream, with codes packed as per the code bit-width.
        The bit-width starts at 9 bits and expands as needed.
        """
        self._initialize_encoding_table()
        buffer = 0
        bits_in_buffer = 0
        output = bytearray()

        for code in codes:
            buffer = (buffer << self.bits_per_code) | code
            bits_in_buffer += self.bits_per_code

            # Codes shall be packed into a continuous bit stream, high-order bit
            # first. This stream shall then be divided into bytes, high-order bit
            # first.
            while bits_in_buffer >= 8:
                bits_in_buffer -= 8
                output.append((buffer >> bits_in_buffer) & 0xFF)

            if code == self.CLEAR_TABLE_MARKER:
                self._initialize_encoding_table()
            elif code == self.EOD_MARKER:
                continue
            else:
                self._increase_next_code()

        # Flush any remaining bits in the buffer
        if bits_in_buffer > 0:
            output.append((buffer << (8 - bits_in_buffer)) & 0xFF)

        return bytes(output)

    def decode(self, data: bytes) -> bytes:
        """Decode data using LZW."""
        from ..filters import LZWDecode

        return LZWDecode.Decoder(data).decode()
