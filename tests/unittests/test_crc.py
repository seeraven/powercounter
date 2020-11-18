# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of powercounter (https://github.com/seeraven/powercounter)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
#
"""Unit tests of the power_counter.crc module."""


# -----------------------------------------------------------------------------
# Module Import
# -----------------------------------------------------------------------------
from unittest import TestCase

import power_counter.crc


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class CrcTest(TestCase):
    """Test the :function:`power_counter.crc.crc16_x25` function."""

    def test_empty(self):
        """power_counter.crc.crc16_x25: Empty buffer."""
        buffer = b''
        self.assertEqual(power_counter.crc.crc16_x25(buffer), 0)

    def test_single(self):
        """power_counter.crc.crc16_x25: Single entry buffer."""
        buffer = b'a'
        self.assertEqual(power_counter.crc.crc16_x25(buffer), 0x82F7)

    def test_multiple(self):
        """power_counter.crc.crc16_x25: Multiple entry buffer."""
        buffer = b'123456789'
        self.assertEqual(power_counter.crc.crc16_x25(buffer), 0x906E)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
