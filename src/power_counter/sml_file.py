"""
SML file representation.

Copyright:
    2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of powercounter (https://github.com/seeraven/powercounter)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""

# -----------------------------------------------------------------------------
# Module Imports
# -----------------------------------------------------------------------------
import logging
from typing import List, Tuple

from .crc import crc16_x25
from .sml_message import SmlMessageType, SmlRawMessageData, get_message
from .sml_types import FieldType

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger()


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
TYPE_OCTET_STRING = 0x00
TYPE_BOOLEAN = 0x40
TYPE_INTEGER = 0x50
TYPE_UNSIGNED = 0x60
TYPE_LIST = 0x70


# -----------------------------------------------------------------------------
# Byte Sequences
# -----------------------------------------------------------------------------
ESCAPE_SEQUENCE = b"\x1b\x1b\x1b\x1b"


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------
# pylint: disable=too-few-public-methods
class SmlFile:
    """Representation of an SML-file."""

    def __init__(self, data: bytes) -> None:
        """Construct a new SmlFile object."""
        LOGGER.debug("Initializing SmlFile class on %d bytes buffer to extract the raw messages.", len(data))
        self.data = data.replace(ESCAPE_SEQUENCE + ESCAPE_SEQUENCE, ESCAPE_SEQUENCE)
        self.messages: List[SmlMessageType] = []
        self._check_crc()
        if self.valid_crc:
            self._extract_messages()

    def _check_crc(self) -> None:
        """Check the CRC of the data."""
        calculated_crc = crc16_x25(self.data[:-2])
        provided_crc = (self.data[-2] << 8) | self.data[-1]
        self.valid_crc = calculated_crc == provided_crc

        if not self.valid_crc:
            LOGGER.error(
                "SML File has invalid CRC! Calculated: 0x%04x, Provided: 0x%04x!", calculated_crc, provided_crc
            )

    def _get_next_field(self, read_index: int, debug_log_indent: int = 0) -> Tuple[int, FieldType]:
        """Extract the next field and return it.

        Args:
            read_index (int): The first byte to analyze in the data buffer.

        Return:
            Returns the tuple (next_read_index, data) with data converted to
            the corresponding python data type.
        """
        type_field = self.data[read_index] & 0x70
        length_field = self.data[read_index] & 0x0F
        while self.data[read_index] & 0x80:
            read_index += 1
            length_field = (length_field << 4) | (self.data[read_index] & 0x0F)

        if length_field == 0:
            length_field = 1

        next_read_index = read_index + length_field
        data_index = read_index + 1
        if type_field == TYPE_OCTET_STRING:
            LOGGER.debug("%sFound octet string field of length %d bytes.", " " * debug_log_indent, length_field)
            return (next_read_index, self.data[data_index:next_read_index])
        if type_field == TYPE_BOOLEAN:
            LOGGER.debug("%sFound binary field (1 byte).", " " * debug_log_indent)
            return (next_read_index, self.data[data_index] != 0x00)
        if type_field == TYPE_INTEGER:
            LOGGER.debug("%sFound signed integer field of %d bytes.", " " * debug_log_indent, length_field)
            return (
                next_read_index,
                int.from_bytes(self.data[data_index:next_read_index], byteorder="big", signed=True),
            )
        if type_field == TYPE_UNSIGNED:
            LOGGER.debug("%sFound unsigned integer field of %d bytes.", " " * debug_log_indent, length_field)
            return (
                next_read_index,
                int.from_bytes(self.data[data_index:next_read_index], byteorder="big", signed=False),
            )
        if type_field == TYPE_LIST:
            LOGGER.debug("%sFound list of %d fields.", " " * debug_log_indent, length_field)
            next_read_index = data_index
            data = []
            for _ in range(length_field):
                next_read_index, field_data = self._get_next_field(
                    next_read_index, debug_log_indent=debug_log_indent + 2
                )
                data.append(field_data)
            LOGGER.debug("%sDone extracting list of %d fields.", " " * debug_log_indent, length_field)
            return (next_read_index, data)

        LOGGER.error("%sUnknown type field 0x%x at index %d!", " " * debug_log_indent, type_field, read_index)
        return (next_read_index, None)

    def _extract_messages(self) -> None:
        """Extract the SML-messages from the data."""
        LOGGER.debug("Extracting the messages from the SML File.")
        read_index = 8  # Skip escape sequence and version
        end_index = len(self.data) - 8

        while read_index < end_index:
            start_index = read_index
            read_index, message = self._get_next_field(read_index)
            LOGGER.debug("Extracted fields from buffer index %d to %d.", start_index, read_index)
            sml_message = SmlRawMessageData.from_field_list(message)
            if sml_message:
                if sml_message.crc16:
                    crc_end_index = read_index - 4
                    calculated_crc = crc16_x25(self.data[start_index:crc_end_index])
                    if calculated_crc != sml_message.crc16:
                        LOGGER.error(
                            "Calculated message CRC is 0x%04x, but provided is 0x%04x!",
                            calculated_crc,
                            sml_message.crc16,
                        )
                        continue
                else:
                    LOGGER.warning("No message CRC provided!")
                message_obj = get_message(sml_message)
                if message_obj:
                    self.messages.append(message_obj)
