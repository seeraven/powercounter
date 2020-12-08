# -*- coding: utf-8 -*-
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
from .crc import crc16_x25
from .sml_message import get_message

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
ESCAPE_SEQUENCE = b'\x1b\x1b\x1b\x1b'


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------
# pylint: disable=too-few-public-methods
class SmlFile:
    """Representation of an SML-file."""

    def __init__(self, data):
        """Construct a new SmlFile object."""
        self.data = data.replace(ESCAPE_SEQUENCE + ESCAPE_SEQUENCE,
                                 ESCAPE_SEQUENCE)
        self.messages = []
        self._check_crc()
        if self.valid_crc:
            self._extract_messages()

    def _check_crc(self):
        """Check the CRC of the data."""
        self.calculated_crc = crc16_x25(self.data[:-2])
        self.provided_crc = (self.data[-2] << 8) | self.data[-1]
        self.valid_crc = self.calculated_crc == self.provided_crc

        if not self.valid_crc:
            print("ERROR: SML-file has invalid CRC (Calculated: 0x%04x, Provided: 0x%04x)" %
                  (self.calculated_crc, self.provided_crc))

    def _get_next_field(self, read_index):
        """Extract the next field and return it.

        Args:
            read_index (int): The first byte to analyze in the data buffer.

        Return:
            Returns the tuple (next_read_index, data) with data converted to
            the corresponding python data type.
        """
        type_field = self.data[read_index] & 0x70
        length_field = self.data[read_index] & 0x0f
        while self.data[read_index] & 0x80:
            read_index += 1
            length_field = (length_field << 4) | (self.data[read_index] & 0x0f)

        if length_field == 0:
            length_field = 1

        next_read_index = read_index + length_field
        if type_field == TYPE_OCTET_STRING:
            data = self.data[read_index + 1:read_index + length_field]
        elif type_field == TYPE_BOOLEAN:
            data = self.data[read_index + 1] != 0x00
        elif type_field == TYPE_INTEGER:
            data = int.from_bytes(self.data[read_index + 1:read_index + length_field],
                                  byteorder='big', signed=True)
        elif type_field == TYPE_UNSIGNED:
            data = int.from_bytes(self.data[read_index + 1:read_index + length_field],
                                  byteorder='big', signed=False)
        elif type_field == TYPE_LIST:
            next_read_index = read_index + 1
            data = []
            for _ in range(length_field):
                next_read_index, field_data = self._get_next_field(next_read_index)
                data.append(field_data)
        else:
            print("ERROR: Unknown type field 0x%x at index %d!" % (type_field, read_index))
            data = None

        return (next_read_index, data)

    def _extract_messages(self):
        """Extract the SML-messages from the data."""
        read_index = 8  # Skip escape sequence and version
        end_index = len(self.data) - 8

        while read_index < end_index:
            start_index = read_index
            read_index, message = self._get_next_field(read_index)
            if message and len(message) == 6:
                calculated_crc = crc16_x25(self.data[start_index:read_index-4])
                if calculated_crc != message[4]:
                    print("ERROR: Calculated message CRC is 0x%04x, but provided is 0x%04x!" %
                          (calculated_crc, message[4]))
                else:
                    message_obj = get_message(message)
                    if message_obj:
                        self.messages.append(message_obj)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
