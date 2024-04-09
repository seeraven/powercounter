"""
Module encapsulating the serial port handling.

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
import atexit
import logging
from typing import Any, BinaryIO, Optional, Union

import serial

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger()


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def get_serial(args: Any, close_on_exit: bool = True) -> Optional[serial.Serial]:
    """Get a serial.Serial() object.

    Args:
        args (obj)           - The arguments object.
        close_on_exit (bool) - If set to True, the serial handle is closed
                               automatically on exit.

    Return:
        Returns an instance of the serial port object or None if the serial
        device could not be opened.
    """
    try:
        LOGGER.debug("Opening serial port %s at baud rate 9600 and 8N1.", args.device)
        handle = serial.Serial(
            port=args.device,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=None,
        )
        handle.reset_input_buffer()
        handle.reset_output_buffer()
        LOGGER.debug("Serial port opened.")
    except serial.serialutil.SerialException:
        LOGGER.critical("Can't open serial device %s!", args.device)
        handle = None

    if close_on_exit and handle:
        LOGGER.debug("Registering at exit handler to close the serial port in the end.")
        atexit.register(handle.close)

    return handle


def get_input_file_or_serial(args: Any, close_on_exit: bool = True) -> Optional[Union[BinaryIO, serial.Serial]]:
    """Get a file handle or a serial.Serial() object.

    Args:
        args (obj)           - The arguments object.
        close_on_exit (bool) - If set to True, the file or serial file handle is
                               closed automatically on exit.

    Return:
        Returns an instance of the serial port object or None if the serial
        device could not be opened.
    """
    if args.input_file:
        try:
            LOGGER.debug("Opening specified input file %s.", args.input_file)
            # pylint: disable=consider-using-with
            input_fh = open(args.input_file, "rb")

            if close_on_exit:
                LOGGER.debug("Registering at exit handler to close the file in the end.")
                atexit.register(input_fh.close)
        except OSError:
            LOGGER.critical("Can't open input file %s!", args.input_file)
            input_fh = None
    else:
        input_fh = get_serial(args, close_on_exit=close_on_exit)

    return input_fh
