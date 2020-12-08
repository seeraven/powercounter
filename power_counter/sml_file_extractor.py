# -*- coding: utf-8 -*-
"""
SML file extractor.

Copyright:
    2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of powercounter (https://github.com/seeraven/powercounter)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""


# -----------------------------------------------------------------------------
# States
# -----------------------------------------------------------------------------
WAIT_FOR_START = 0
WAIT_FOR_END = 1


# -----------------------------------------------------------------------------
# Byte Sequences
# -----------------------------------------------------------------------------
ESCAPE_SEQUENCE = b'\x1b\x1b\x1b\x1b'
VERSION_SEQUENCE = b'\x01\x01\x01\x01'
END_START = b'\x1a'


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------
# pylint: disable=too-few-public-methods
class SmlFileExtractor:
    """Extractor for SML-Files from byte stream."""

    def __init__(self):
        """Construct a new SmlFileExtractor worker."""
        self.state = WAIT_FOR_START
        self.buffer = b''

    def add_bytes(self, new_bytes):
        """Add the given bytes to the internal buffer and check for complete SML-files.

        Args:
            new_bytes (bytes): The bytes to add.

        Return:
            Returns a list of extracted SML files. This list might be empty.
        """
        self.buffer += new_bytes
        sml_files = []
        sml_extracted = True

        while sml_extracted:
            sml_extracted = False

            if self.state == WAIT_FOR_START:
                if ESCAPE_SEQUENCE + VERSION_SEQUENCE in self.buffer:
                    self.buffer = self.buffer[self.buffer.find(ESCAPE_SEQUENCE + VERSION_SEQUENCE):]
                    self.state = WAIT_FOR_END

            if self.state == WAIT_FOR_END:
                cand_idx = self.buffer.find(ESCAPE_SEQUENCE + END_START)
                while (cand_idx > 4) and ((cand_idx + 8) <= len(self.buffer)):
                    if self.buffer[cand_idx-4:cand_idx] == ESCAPE_SEQUENCE:
                        cand_idx = self.buffer.find(ESCAPE_SEQUENCE + END_START, cand_idx + 4)
                        continue

                    sml_files.append(self.buffer[:cand_idx + 8])
                    self.buffer = self.buffer[cand_idx + 8:]
                    self.state = WAIT_FOR_START
                    sml_extracted = True
                    break

        return sml_files


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
