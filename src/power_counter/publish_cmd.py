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
import logging
from typing import Any

from .mqtt_ifc import MqttInterface
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
def publish(args: Any) -> bool:
    """Handle the publish command of powercounter.

    Args:
        args (obj) - The command line arguments.

    Return:
        Returns True on success, otherwise False.
    """
    input_fh = get_input_file_or_serial(args)
    if input_fh is None:
        return False

    mqtt = MqttInterface(args)

    def obis_data_cb(obj_name, value, unit):
        mqtt.publish(obj_name, value)

    process(args, input_fh, None, obis_data_cb)

    mqtt.close()
    input_fh.close()
    return True


def add_publish_parser(subparsers: Any) -> None:
    """Add the subparser for the publish command.

    Args:
        subparsers (obj): The subparsers object used to generate the subparsers.
    """
    LOGGER.debug("Adding parser for subcommand 'publish'.")
    publish_parser = subparsers.add_parser(
        "publish", description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter
    )
    publish_parser.add_argument(
        "--mqtt-host", help="MQTT host. [Default: %(default)s]", action="store", default="192.168.1.70"
    )
    publish_parser.add_argument(
        "--mqtt-port", help="MQTT port. [Default: %(default)s]", action="store", type=int, default=1883
    )
    publish_parser.add_argument(
        "--mqtt-username", help="MQTT username. [Default: %(default)s]", action="store", default="mqtt"
    )
    publish_parser.add_argument(
        "--mqtt-password", help="MQTT password. [Default: %(default)s]", action="store", default="mqtt"
    )
    publish_parser.add_argument(
        "--mqtt-topics",
        help="Comma separated list of OBIS IDs and the " "corresponding MQTT topic. [Default: %(default)s]",
        action="store",
        default="1-0:1.8.0*255=power/total,1-0:16.7.0*255=power/rate,1-0:2.8.0*255=power/feed-total",
    )
    publish_parser.set_defaults(func=publish)
