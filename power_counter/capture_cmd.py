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
import argparse
import atexit

from .serial_ifc import get_serial


# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
DESCRIPTION = """
PowerCounter 'capture' command
==============================

Capture from the serial port and save the output in a file without any further
processing.

Example:
    powercounter -d /dev/ttyUSB1 capture test.dat
"""


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def capture(args):
    """Handle the capture command of powercounter.

    Args:
        args (obj) - The command line arguments.

    Return:
        Returns True on success, otherwise False.
    """
    print("Saving data into file %s. Press Ctrl-C to stop." % args.output_file)

    # Open serial port
    serial_dev = get_serial(args)
    if serial_dev is None:
        return False
    atexit.register(serial_dev.close)

    # Open output file
    try:
        output_fh = open(args.output_file, 'wb')
    except OSError:
        print("ERROR: Can't open output file %s!" % args.output_file)
        return False
    atexit.register(output_fh.close)

    num_bytes = 0
    while True:
        try:
            byte_buffer = serial_dev.read(64)
            output_fh.write(byte_buffer)
            num_bytes += len(byte_buffer)
            print("Read %d bytes...\r" % num_bytes)
        except KeyboardInterrupt:
            print("\n\nFinishing capture.")
            break

    return True


def add_capture_parser(subparsers):
    """Add the subparser for the capture command.

    Args:
        subparsers (obj): The subparsers object used to generate the subparsers.
    """
    capture_parser = subparsers.add_parser('capture',
                                           description=DESCRIPTION,
                                           formatter_class=argparse.RawTextHelpFormatter)
    capture_parser.add_argument("output_file",
                                metavar="OUTPUT_FILE",
                                help="The output file to store the raw data.",
                                action="store",
                                default=None)
    capture_parser.set_defaults(func=capture)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
