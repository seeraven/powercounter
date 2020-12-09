# -*- coding: utf-8 -*-
"""
Module providing a processor function used in different commands.

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
from .sml_file import SmlFile
from .sml_file_extractor import SmlFileExtractor
from .sml_message import SmlMessageGetListResponse


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def process_sml_file(file_data, sml_file_cb, obis_data_cb):
    """Process a SML file and call the callbacks.

    Args:
        file_data (bytes): The raw data of the SML file.
        sml_file_cb:       Callback function taking the arguments (file_data, sml_file).
        obis_data_cb:      Callback function taking the arguments (obj_name, value, unit).
    """
    sml_file = SmlFile(file_data)
    if sml_file_cb:
        sml_file_cb(file_data, sml_file)

    if obis_data_cb:
        for message in sml_file.messages:
            if isinstance(message, SmlMessageGetListResponse):
                for obj_name, _, _, unit, scaler, value, _ in message.list_entries:
                    if unit in ['Wh', 'W']:
                        scaled_value = float(value) * pow(10, scaler)
                        obis_data_cb(obj_name, scaled_value, unit)


def process(args, input_fh, sml_file_cb=None, obis_data_cb=None):
    """Read from an input file handle and process all SML files by calling the callbacks.

    Args:
        args (obj):        The command line arguments.
        input_fh (obj):    The input file handle.
        sml_file_cb:       Callback function taking the arguments (file_data, sml_file).
        obis_data_cb:      Callback function taking the arguments (obj_name, value, unit).
    """
    extractor = SmlFileExtractor()
    while True:
        buffer = input_fh.read(128)
        if not buffer and args.input_file:
            break
        files = extractor.add_bytes(buffer)
        for file_data in files:
            process_sml_file(file_data, sml_file_cb, obis_data_cb)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
