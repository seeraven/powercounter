# -*- coding: utf-8 -*-
"""
Module handling the print command of the powercounter application.

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
from .sml_message_processor import process


# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
DESCRIPTION = """
PowerCounter 'print' command
============================

Capture from the serial port (or input file) and parse the data to print it
on stdout.

Example:
    powercounter -d /dev/ttyUSB1 print
"""


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def print_cmd(args):
    """Handle the print command of powercounter.

    Args:
        args (obj) - The command line arguments.

    Return:
        Returns True on success, otherwise False.
    """
    if args.input_file:
        try:
            input_fh = open(args.input_file, 'rb')
        except OSError:
            print("ERROR: Can't open input file %s!" % args.input_file)
            input_fh = None
    else:
        input_fh = get_serial(args)

    if input_fh is None:
        return False

    atexit.register(input_fh.close)

    def sml_file_cb(file_data, sml_file):
        if args.verbose:
            print("INFO: Extracted a new file of %d bytes:" % len(file_data))
            print("      Extracted %d messages:" % len(sml_file.messages))
            for message in sml_file.messages:
                print(message)

    def obis_data_cb(obj_name, value, unit):
        print("%s: %.3f %s" % (obj_name, value, unit))

    process(args, input_fh, sml_file_cb, obis_data_cb)

    input_fh.close()
    return True


def add_print_parser(subparsers):
    """Add the subparser for the print command.

    Args:
        subparsers (obj): The subparsers object used to generate the subparsers.
    """
    print_parser = subparsers.add_parser('print',
                                         description=DESCRIPTION,
                                         formatter_class=argparse.RawTextHelpFormatter)
    print_parser.add_argument("-v", "--verbose",
                              help="Print the extracted SML data in addition to "
                              "the extracted OBIS data.",
                              action="store_true",
                              default=False)
    print_parser.set_defaults(func=print_cmd)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
