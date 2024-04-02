#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of powercounter (https://github.com/seeraven/powercounter)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the power_counter.sml_file module."""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
from pathlib import Path
from unittest import TestCase

import power_counter.sml_file
import power_counter.sml_file_extractor
from power_counter.crc import crc16_x25

# ----------------------------------------------------------------------------
#  LIBSML-TESTING DIRECTORY
# ----------------------------------------------------------------------------
LIBSML_TESTING_DIR = Path(__file__).parent.parent / "libsml-testing"


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class SmlFileTest(TestCase):
    """Test the :class:`power_counter.sml_file.SmlFileExtractor` class."""

    def test_crc(self) -> None:
        """power_counter.sml_file.SmlFileExtractor: CRC calculation."""
        data = bytes([1, 2, 3, 4, 5, 6, 7, 8])
        crc = crc16_x25(data)
        data_with_correct_crc = data + bytes([(crc >> 8) & 0xFF, crc & 0xFF])
        data_with_incorrect_crc = data + bytes([crc & 0xFF, (crc << 8) & 0xFF])
        self.assertTrue(power_counter.sml_file.SmlFile(data_with_correct_crc).valid_crc, msg="Correct CRC")
        self.assertFalse(power_counter.sml_file.SmlFile(data_with_incorrect_crc).valid_crc, msg="Incorrect CRC")

    def test_octet_string(self) -> None:
        """power_counter.sml_file.SmlFileExtractor: Octet string extraction."""
        data = bytes([0x02, 0xAA, 0x00, 0x00])
        file = power_counter.sml_file.SmlFile(data)
        next_idx, field = file._get_next_field(0)  # pylint: disable=protected-access
        self.assertEqual(next_idx, 2)
        self.assertEqual(type(field), bytes)

    def test_bool(self) -> None:
        """power_counter.sml_file.SmlFileExtractor: Bool extraction."""
        data = bytes([0x42, 0x01, 0x00, 0x00])
        file = power_counter.sml_file.SmlFile(data)
        next_idx, field = file._get_next_field(0)  # pylint: disable=protected-access
        self.assertEqual(next_idx, 2)
        self.assertEqual(type(field), bool)

    def test_int8(self) -> None:
        """power_counter.sml_file.SmlFileExtractor: Int8 extraction."""
        data = bytes([0x52, 0xF6, 0x00, 0x00])
        file = power_counter.sml_file.SmlFile(data)
        next_idx, field = file._get_next_field(0)  # pylint: disable=protected-access
        self.assertEqual(next_idx, 2)
        self.assertEqual(type(field), int)
        self.assertEqual(field, -10)

    def test_int16(self) -> None:
        """power_counter.sml_file.SmlFileExtractor: Int8 extraction."""
        data = bytes([0x53, 0xFB, 0x2E, 0x00, 0x00])
        file = power_counter.sml_file.SmlFile(data)
        next_idx, field = file._get_next_field(0)  # pylint: disable=protected-access
        self.assertEqual(next_idx, 3)
        self.assertEqual(type(field), int)
        self.assertEqual(field, -1234)

    def test_int32(self) -> None:
        """power_counter.sml_file.SmlFileExtractor: Int8 extraction."""
        data = bytes([0x55, 0xF8, 0xA4, 0x32, 0xEB, 0x00, 0x00])
        file = power_counter.sml_file.SmlFile(data)
        next_idx, field = file._get_next_field(0)  # pylint: disable=protected-access
        self.assertEqual(next_idx, 5)
        self.assertEqual(type(field), int)
        self.assertEqual(field, -123456789)

    def test_int64(self) -> None:
        """power_counter.sml_file.SmlFileExtractor: Int8 extraction."""
        data = bytes([0x59, 0xFF, 0xFF, 0x8F, 0xB7, 0x79, 0xF2, 0x50, 0xC0, 0x00, 0x00])
        file = power_counter.sml_file.SmlFile(data)
        next_idx, field = file._get_next_field(0)  # pylint: disable=protected-access
        self.assertEqual(next_idx, 9)
        self.assertEqual(type(field), int)
        self.assertEqual(field, -123456789000000)

    def test_uint8(self) -> None:
        """power_counter.sml_file.SmlFileExtractor: Int8 extraction."""
        data = bytes([0x62, 0xF6, 0x00, 0x00])
        file = power_counter.sml_file.SmlFile(data)
        next_idx, field = file._get_next_field(0)  # pylint: disable=protected-access
        self.assertEqual(next_idx, 2)
        self.assertEqual(type(field), int)
        self.assertEqual(field, 0xF6)

    def test_uint16(self) -> None:
        """power_counter.sml_file.SmlFileExtractor: Int8 extraction."""
        data = bytes([0x63, 0xFB, 0x2E, 0x00, 0x00])
        file = power_counter.sml_file.SmlFile(data)
        next_idx, field = file._get_next_field(0)  # pylint: disable=protected-access
        self.assertEqual(next_idx, 3)
        self.assertEqual(type(field), int)
        self.assertEqual(field, 0xFB2E)

    def test_uint32(self) -> None:
        """power_counter.sml_file.SmlFileExtractor: Int8 extraction."""
        data = bytes([0x65, 0xF8, 0xA4, 0x32, 0xEB, 0x00, 0x00])
        file = power_counter.sml_file.SmlFile(data)
        next_idx, field = file._get_next_field(0)  # pylint: disable=protected-access
        self.assertEqual(next_idx, 5)
        self.assertEqual(type(field), int)
        self.assertEqual(field, 0xF8A432EB)

    def test_uint64(self) -> None:
        """power_counter.sml_file.SmlFileExtractor: Int8 extraction."""
        data = bytes([0x69, 0xFF, 0xFF, 0x8F, 0xB7, 0x79, 0xF2, 0x50, 0xC0, 0x00, 0x00])
        file = power_counter.sml_file.SmlFile(data)
        next_idx, field = file._get_next_field(0)  # pylint: disable=protected-access
        self.assertEqual(next_idx, 9)
        self.assertEqual(type(field), int)
        self.assertEqual(field, 0xFFFF8FB779F250C0)

    def test_unknown(self) -> None:
        """power_counter.sml_file.SmlFileExtractor: Unknown type."""
        data = bytes([0x12, 0x01, 0x00, 0x00])
        file = power_counter.sml_file.SmlFile(data)
        next_idx, field = file._get_next_field(0)  # pylint: disable=protected-access
        self.assertEqual(next_idx, 2)
        self.assertIsNone(field)

    def test_on_files(self) -> None:
        """power_counter.sml_file.SmlFileExtractor: Data from libsml-testing files."""
        for filename in LIBSML_TESTING_DIR.glob("*.bin"):
            print(f"Processing file {filename}")
            extractor = power_counter.sml_file_extractor.SmlFileExtractor()
            with open(filename, "rb") as file_handle:
                data = file_handle.read()
            files = extractor.add_bytes(data)
            for file_data in files:
                sml_file = power_counter.sml_file.SmlFile(file_data)
                if sml_file.valid_crc:
                    self.assertTrue(sml_file.messages, msg=f"Testing content of file {filename}")
