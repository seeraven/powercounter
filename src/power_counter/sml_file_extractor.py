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
# Module Import
# -----------------------------------------------------------------------------
import logging
from typing import List, Optional

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger()


# -----------------------------------------------------------------------------
# States
# -----------------------------------------------------------------------------
WAIT_FOR_START = 0
WAIT_FOR_END = 1


# -----------------------------------------------------------------------------
# Byte Sequences
# -----------------------------------------------------------------------------
ESCAPE_SEQUENCE = b"\x1b\x1b\x1b\x1b"
VERSION_SEQUENCE = b"\x01\x01\x01\x01"
END_START = b"\x1a"


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def find_at_four_bytes(buffer: bytes, sequence: bytes, start: Optional[int]) -> int:
    """Find a sequence starting only at multiple of 4 bytes."""
    idx = buffer.find(sequence, start)
    offset = idx % 4
    while (offset != 0) and (idx >= 0):
        idx = buffer.find(sequence, idx + (4 - offset))  # start at next 4 bytes
        offset = idx % 4
    return idx


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------
# pylint: disable=too-few-public-methods
class SmlFileExtractor:
    """Extractor for SML-Files from byte stream."""

    def __init__(self):
        """Construct a new SmlFileExtractor worker."""
        LOGGER.debug("Initialize SmlFileExtractor worker.")
        self.state = WAIT_FOR_START
        self.buffer = b""

    def add_bytes(self, new_bytes: bytes) -> List[bytes]:
        """Add the given bytes to the internal buffer and check for complete SML-files.

        Args:
            new_bytes (bytes): The bytes to add.

        Return:
            Returns a list of extracted SML files. This list might be empty.
        """
        LOGGER.debug("Adding %d bytes to the internal buffer.", len(new_bytes))
        self.buffer += new_bytes
        sml_files: List[bytes] = []
        sml_extracted = True

        while sml_extracted:
            sml_extracted = False

            if self.state == WAIT_FOR_START:
                start_index = self.buffer.find(ESCAPE_SEQUENCE + VERSION_SEQUENCE)
                if start_index >= 0:
                    self.buffer = self.buffer[start_index:]
                    self.state = WAIT_FOR_END
                    LOGGER.debug(
                        "Found start of a message at index %d. Shrinking buffer to start with the start marker.",
                        start_index,
                    )

            if self.state == WAIT_FOR_END:
                cand_idx = find_at_four_bytes(self.buffer, ESCAPE_SEQUENCE, 8)
                # Ensure the full end marker is part of the buffer
                while (cand_idx >= 0) and ((cand_idx + 8) <= len(self.buffer)):
                    if self.buffer[cand_idx:].startswith(ESCAPE_SEQUENCE + ESCAPE_SEQUENCE):
                        LOGGER.debug("Skipping double escape sequence found at index %d.", cand_idx)
                        cand_idx = self.buffer.find(ESCAPE_SEQUENCE, cand_idx + 8)
                        continue
                    if self.buffer[cand_idx:].startswith(ESCAPE_SEQUENCE + END_START):
                        LOGGER.debug(
                            "End marker found at index %d. Extracting message of %d bytes.", cand_idx, cand_idx + 8
                        )
                        after_end_idx = cand_idx + 8
                        sml_files.append(self.buffer[:after_end_idx])
                        self.buffer = self.buffer[after_end_idx:]
                        self.state = WAIT_FOR_START
                        sml_extracted = True
                        break
                    if self.buffer[cand_idx:].startswith(ESCAPE_SEQUENCE + VERSION_SEQUENCE):
                        LOGGER.error("Expected end marker but found message start marker at index %d!", cand_idx)
                        self.buffer = self.buffer[cand_idx:]
                        cand_idx = find_at_four_bytes(self.buffer, ESCAPE_SEQUENCE, 8)
                        continue

                    LOGGER.error(
                        "Found escape sequence at index %d that is not followed "
                        "by another escape sequence, an end marker or a start marker!",
                        cand_idx,
                    )
                    cand_idx = find_at_four_bytes(self.buffer, ESCAPE_SEQUENCE, cand_idx + 4)

        LOGGER.debug(
            "Returning %d SML messages encoded as bytes. %d bytes remain in the internal buffer.",
            len(sml_files),
            len(self.buffer),
        )
        return sml_files
