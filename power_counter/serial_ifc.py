# -*- coding: utf-8 -*-
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
import serial


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def get_serial(args):
    """Get a serial.Serial() object.

    Args:
        args (obj) - The arguments object.

    Return:
        Returns an instance of the serial port object or None if the serial
        device could not be opened.
    """
    try:
        handle = serial.Serial(port=args.device,
                               baudrate=9600,
                               parity=serial.PARITY_NONE,
                               stopbits=serial.STOPBITS_ONE,
                               bytesize=serial.EIGHTBITS,
                               timeout=None)
        handle.reset_input_buffer()
        handle.reset_output_buffer()
    except serial.serialutil.SerialException:
        print("ERROR: Can't open serial device %s!" % args.device)
        handle = None

    return handle


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
