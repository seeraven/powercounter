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
import logging
from typing import Any, BinaryIO, Callable, Optional, Union

import serial

from .sml_file import SmlFile
from .sml_file_extractor import SmlFileExtractor
from .sml_message import SmlMessageGetListResponse

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger()


# -----------------------------------------------------------------------------
# Types
# -----------------------------------------------------------------------------
SmlFileCallbackType = Callable[[bytes, SmlFile], None]
ObisDataCallbackType = Callable[[str, float, str], None]


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def process_sml_file(
    file_data: bytes, sml_file_cb: Optional[SmlFileCallbackType], obis_data_cb: Optional[ObisDataCallbackType]
) -> None:
    """Process a SML file and call the callbacks.

    Args:
        file_data (bytes): The raw data of the SML file.
        sml_file_cb:       Callback function taking the arguments (file_data, sml_file).
        obis_data_cb:      Callback function taking the arguments (obj_name, value, unit).
    """
    sml_file = SmlFile(file_data)
    if sml_file_cb:
        sml_file_cb(file_data, sml_file)

    # pylint: disable=too-many-nested-blocks
    if obis_data_cb:
        for message in sml_file.messages:
            if isinstance(message, SmlMessageGetListResponse):
                for item in message.list_entries:
                    if item.unit in ["Wh", "W"]:
                        if item.scaler is not None:
                            scaled_value = float(item.value) * pow(10, item.scaler)
                        else:
                            scaled_value = float(item.value)
                        obis_data_cb(item.obj_name, scaled_value, item.unit)


def process(
    args: Any,
    input_fh: Union[BinaryIO, serial.Serial],
    sml_file_cb: Optional[SmlFileCallbackType] = None,
    obis_data_cb: Optional[ObisDataCallbackType] = None,
):
    """Read from an input file handle and process all SML files by calling the callbacks.

    Args:
        args (obj):        The command line arguments.
        input_fh (obj):    The input file handle.
        sml_file_cb:       Callback function taking the arguments (file_data, sml_file).
        obis_data_cb:      Callback function taking the arguments (obj_name, value, unit).
    """
    LOGGER.debug("Starting processing the Sml data stream.")
    extractor = SmlFileExtractor()
    while True:
        buffer = input_fh.read(128)
        if not buffer and args.input_file:
            break
        files = extractor.add_bytes(buffer)
        for file_data in files:
            process_sml_file(file_data, sml_file_cb, obis_data_cb)
