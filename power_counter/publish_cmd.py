# -*- coding: utf-8 -*-
"""
Module handling the mqtt publish command of the powercounter application.

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

from .mqtt_ifc import MqttInterface
from .serial_ifc import get_serial
from .sml_message_processor import process


# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
DESCRIPTION = """
PowerCounter 'publish' command
==============================

Capture from the serial port (or input file) and publish the extracted data
as mqtt messages.

Example:
    powercounter -d /dev/ttyUSB1 publish
"""


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def publish(args):
    """Handle the publish command of powercounter.

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

    mqtt = MqttInterface(args)

    def obis_data_cb(obj_name, value, unit):
        print("%s: %.3f %s" % (obj_name, value, unit))

    process(args, input_fh, None, obis_data_cb)

    mqtt.close()
    input_fh.close()
    return True


def add_publish_parser(subparsers):
    """Add the subparser for the publish command.

    Args:
        subparsers (obj): The subparsers object used to generate the subparsers.
    """
    publish_parser = subparsers.add_parser('publish',
                                           description=DESCRIPTION,
                                           formatter_class=argparse.RawTextHelpFormatter)
    publish_parser.add_argument("--mqtt-host",
                                help="MQTT host. [Default: %(default)s]",
                                action="store",
                                default="192.168.1.70")
    publish_parser.add_argument("--mqtt-port",
                                help="MQTT port. [Default: %(default)s]",
                                action="store",
                                type=int,
                                default=1883)
    publish_parser.add_argument("--mqtt-username",
                                help="MQTT username. [Default: %(default)s]",
                                action="store",
                                default="mqtt")
    publish_parser.add_argument("--mqtt-password",
                                help="MQTT password. [Default: %(default)s]",
                                action="store",
                                default="mqtt")
    publish_parser.add_argument("--mqtt-topic",
                                help="MQTT topic. [Default: %(default)s]",
                                action="store",
                                default="counters/power")
    publish_parser.set_defaults(func=publish)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
