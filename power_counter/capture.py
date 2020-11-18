# -*- coding: utf-8 -*-
"""
Module handling the capture to file part of the powercounter application.

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

import serial


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def get_serial(args):
    """Get a serial.Serial() object.

    Args:
        args (obj) - The arguments object.

    Return:
        Returns an instance of the serial port object.
    """
    handle = serial.Serial(port=args.device,
                           baudrate=9600,
                           parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_ONE,
                           bytesize=serial.EIGHTBITS,
                           timeout=None)
    handle.reset_input_buffer()
    handle.reset_output_buffer()
    return handle


def capture(args):
    """Handle the capture function of powercounter.

    Args:
        args (obj) - The command line arguments.

    Return:
        Returns True on success, otherwise False.
    """
    print("Saving data into file %s. Press Ctrl-C to stop." % args.capture)

    # Open serial port
    try:
        serial_dev = get_serial(args)
    except serial.serialutil.SerialException:
        print("ERROR: Can't open serial device %s!" % args.device)
        return False
    atexit.register(serial_dev.close)

    # Open output file
    try:
        output_fh = open(args.capture, 'wb')
    except OSError:
        print("ERROR: Can't open output file %s!" % args.capture)
        return False
    atexit.register(output_fh.close)

    num_bytes = 0
    while True:
        byte_buffer = serial_dev.read(64)
        output_fh.write(byte_buffer)
        num_bytes += len(byte_buffer)
        print("Read %d bytes...\r" % num_bytes)

    return True


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
