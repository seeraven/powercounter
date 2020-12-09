# -*- coding: utf-8 -*-
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
import glob
from unittest import TestCase

import power_counter.sml_file
import power_counter.sml_file_extractor


# -----------------------------------------------------------------------------
# Test Class
# -----------------------------------------------------------------------------
class SmlFileTest(TestCase):
    """Test the :class:`power_counter.sml_file.SmlFileExtractor` class."""

    def test_on_files(self):
        """power_counter.sml_file.SmlFileExtractor: Data from libsml-testing files."""
        for filename in glob.glob("../libsml-testing/*.bin"):
            print("Processing file %s" % filename)
            extractor = power_counter.sml_file_extractor.SmlFileExtractor()
            data = open(filename, 'rb').read()
            files = extractor.add_bytes(data)
            for file_data in files:
                sml_file = power_counter.sml_file.SmlFile(file_data)
                if sml_file.valid_crc:
                    self.assertTrue(sml_file.messages, msg="Testing content of file %s" % filename)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
