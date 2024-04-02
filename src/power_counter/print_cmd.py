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
import logging

from .serial_ifc import get_input_file_or_serial
from .sml_message_processor import process

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger()


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
    input_fh = get_input_file_or_serial(args)
    if input_fh is None:
        return False

    def sml_file_cb(file_data, sml_file):
        if args.verbose:
            print(f"INFO: Extracted a new file of {len(file_data)} bytes:")
            print(f"      Extracted {len(sml_file.messages)} messages:")
            for message in sml_file.messages:
                print(message)

    def obis_data_cb(obj_name, value, unit):
        print(f"{obj_name}: {value:.3f} {unit}")

    process(args, input_fh, sml_file_cb, obis_data_cb)

    input_fh.close()
    return True


def add_print_parser(subparsers):
    """Add the subparser for the print command.

    Args:
        subparsers (obj): The subparsers object used to generate the subparsers.
    """
    LOGGER.debug("Adding parser for subcommand 'print'.")
    print_parser = subparsers.add_parser(
        "print", description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter
    )
    print_parser.set_defaults(func=print_cmd)
