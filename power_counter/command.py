# -*- coding: utf-8 -*-
"""
Module handling the command line interface of the powercounter application.

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

import serial

from .capture import capture, get_serial
from .sml_file import SmlFile
from .sml_file_extractor import SmlFileExtractor


# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
DESCRIPTION = """
PowerCounter
============

Python based application to analyze the data of a electricity meter sent over
an infrared LED using an USB UART adapter. The extracted data is sent via MQTT.
"""


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def get_parser():
    """Get the argument parser for the :code:`powercounter` command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-d", "--device",
                        help="The serial port device to open. Default: %(default)s.",
                        action="store",
                        default="/dev/ttyUSB0")
    parser.add_argument("-c", "--capture",
                        metavar="DATAFILE",
                        help="Capture raw data from the serial port and store it "
                        "in the given file.",
                        action="store",
                        default=None)
    parser.add_argument("-i", "--input-file",
                        metavar="DATAFILE",
                        help="Instead of using a serial port, read the data from "
                        "the specified data file (previously captured using the -c option).",
                        action="store",
                        default=None)
    parser.add_argument("--mqtt-host",
                        help="MQTT host. [Default: %(default)s]",
                        action="store",
                        default="192.168.1.70")
    parser.add_argument("--mqtt-port",
                        help="MQTT port. [Default: %(default)s]",
                        action="store",
                        type=int,
                        default=1883)
    parser.add_argument("--mqtt-username",
                        help="MQTT username. [Default: %(default)s]",
                        action="store",
                        default="mqtt")
    parser.add_argument("--mqtt-password",
                        help="MQTT password. [Default: %(default)s]",
                        action="store",
                        default="mqtt")
    parser.add_argument("--mqtt-topic",
                        help="MQTT topic. [Default: %(default)s]",
                        action="store",
                        default="counters/power")
    return parser


def power_counter():
    """Execute the main function if called as :code:`powercounter`.

    Return:
        Returns True on success, otherwise False.
    """
    parser = get_parser()
    args = parser.parse_args()
    success = True

    if args.capture:
        success = capture(args)
    else:
        if args.input_file:
            try:
                input_fh = open(args.input_file, 'rb')
            except OSError:
                print("ERROR: Can't open input file %s!" % args.input_file)
                return False
        else:
            try:
                input_fh = get_serial(args)
            except serial.serialutil.SerialException:
                print("ERROR: Can't open serial device %s!" % args.device)
                return False

        extractor = SmlFileExtractor()
        while True:
            buffer = input_fh.read(128)
            if not buffer and args.input_file:
                break
            files = extractor.add_bytes(buffer)
            for file_data in files:
                print("INFO: Extracted a new file of %d bytes:" % len(file_data))
                sml_file = SmlFile(file_data)
                print("      Extracted %d messages:" % len(sml_file.messages))
                for message in sml_file.messages:
                    print(message)

        input_fh.close()

    return success


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
