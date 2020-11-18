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
    _ = parser.parse_args()
    success = True

    return success


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
