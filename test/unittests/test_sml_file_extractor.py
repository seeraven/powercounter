#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of powercounter (https://github.com/seeraven/powercounter)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the power_counter.sml_file_extractor module."""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
from pathlib import Path
from unittest import TestCase

import power_counter.sml_file_extractor

# ----------------------------------------------------------------------------
#  LIBSML-TESTING DIRECTORY
# ----------------------------------------------------------------------------
LIBSML_TESTING_DIR = Path(__file__).parent.parent / "libsml-testing"


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class SmlFileExtractorTest(TestCase):
    """Test the :class:`power_counter.sml_file_extractor.SmlFileExtractor` class."""

    def test_usage(self) -> None:
        """power_counter.sml_file_extractor.SmlFileExtractor: Standard usage."""
        extractor = power_counter.sml_file_extractor.SmlFileExtractor()

        sml_file_start = b"\x1b\x1b\x1b\x1b"  # escape sequence
        sml_file_start += b"\x01\x01\x01\x01"  # version 1
        sml_file_content = b"\x76\x01\x01\x01"  # some stuff
        sml_file_end = b"\x1b\x1b\x1b\x1b"  # escape sequence
        sml_file_end += b"\x1a\x01\x02\x03"  # end of message

        self.assertFalse(extractor.add_bytes(sml_file_start))
        self.assertFalse(extractor.add_bytes(sml_file_content))

        files = extractor.add_bytes(sml_file_end)
        self.assertTrue(files)
        self.assertEqual(sml_file_start + sml_file_content + sml_file_end, files[0])

        # Ensure that the next call uses an empty buffer
        self.assertFalse(extractor.add_bytes(b""))

    def test_multiple(self) -> None:
        """power_counter.sml_file_extractor.SmlFileExtractor: Multiple files in one byte stream."""
        extractor = power_counter.sml_file_extractor.SmlFileExtractor()

        sml_file_start = b"\x1b\x1b\x1b\x1b"  # escape sequence
        sml_file_start += b"\x01\x01\x01\x01"  # version 1
        sml_file_content_1 = b"\x76\x01\x01\x01"  # some stuff
        sml_file_content_2 = b"\x76\x02\x02\x02"  # some stuff
        sml_file_end = b"\x1b\x1b\x1b\x1b"  # escape sequence
        sml_file_end += b"\x1a\x01\x02\x03"  # end of message

        files = extractor.add_bytes(
            sml_file_start + sml_file_content_1 + sml_file_end + sml_file_start + sml_file_content_2 + sml_file_end
        )
        self.assertEqual(2, len(files))
        self.assertEqual(sml_file_start + sml_file_content_1 + sml_file_end, files[0])
        self.assertEqual(sml_file_start + sml_file_content_2 + sml_file_end, files[1])

    def test_escape(self) -> None:
        """power_counter.sml_file_extractor.SmlFileExtractor: Correct end on escaped data."""
        extractor = power_counter.sml_file_extractor.SmlFileExtractor()

        sml_file_start = b"\x1b\x1b\x1b\x1b"  # escape sequence
        sml_file_start += b"\x01\x01\x01\x01"  # version 1
        sml_file_content = b"\x1b\x1b\x1b\x1b"  # escape sequence
        sml_file_content += b"\x1b\x1b\x1b\x1b"  # data (not the end)
        sml_file_content += b"\x1a\x01\x02\x03"  # data (not the end)
        # Note that the content ends with at least one 0x00 so there is no
        # possiblity to have an escape sequence right before that.
        sml_file_end = b"\x1b\x1b\x1b\x1b"  # escape sequence
        sml_file_end += b"\x1a\x01\x02\x03"  # end of message

        sml_file = sml_file_start + sml_file_content + sml_file_end

        files = extractor.add_bytes(sml_file)
        self.assertTrue(files)
        self.assertEqual(sml_file, files[0])

    def test_on_files(self) -> None:
        """power_counter.sml_file_extractor.SmlFileExtractor: Data from libsml-testing files."""
        for filename in LIBSML_TESTING_DIR.glob("*.bin"):
            extractor = power_counter.sml_file_extractor.SmlFileExtractor()
            with open(filename, "rb") as file_handle:
                data = file_handle.read()
            files = extractor.add_bytes(data)
            if filename.name in ["DZG_DVS-7420.2V.G2_mtr1_error.bin"]:
                self.assertFalse(files, msg=f"Testing content of file {filename}")
            else:
                self.assertTrue(files, msg=f"Testing content of file {filename}")
