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
import logging
import time
from typing import Any, Dict

from .capture_cmd import add_capture_parser
from .print_cmd import add_print_parser
from .publish_cmd import add_publish_parser

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger()


# -----------------------------------------------------------------------------
# Module Variables
# -----------------------------------------------------------------------------
DESCRIPTION = """
PowerCounter
============

Python based application to analyze the data of a electricity meter sent over
an infrared LED using an USB UART adapter. The extracted data is sent via MQTT.

This command provides the following subcommands:
  - "capture" to capture raw data from the serial port and save it in a file.
    This helps development and debugging this application.
  - "print" to parse the data from the serial port or a previously recorded
    file and print the results on stdout.
  - "publish" to parse the data from the serial port or a previously recorded
    file and publish the mqtt messages.

See the help of the individual subcommands for more information and the
command line options.
"""


# -----------------------------------------------------------------------------
# Logging Filter Class
# -----------------------------------------------------------------------------
# pylint: disable=too-few-public-methods
class LoggingSuppressionFilter(logging.Filter):
    """Filter warnings and errors to suppress duplicate warnings for a given amount of time."""

    def __init__(self, suppression_time: float) -> None:
        super().__init__()
        self._suppression_time = suppression_time
        self._msg_data: Dict[str, Any] = {}

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter function.

        Args:
            record - The log record.
        Return:
            Returns True if the record should be logged or False if it should be ignored.
        """
        if record.levelno in [logging.WARNING, logging.ERROR]:
            if record.msg in self._msg_data:
                if time.time() < self._msg_data[record.msg]["until"]:
                    self._msg_data[record.msg]["num_suppressed"] += 1
                    return False
                newmsg = record.msg
                if self._msg_data[record.msg]["num_suppressed"] > 0:
                    newmsg += f" (suppressed {self._msg_data[record.msg]['num_suppressed']} times before)"
                self._msg_data[record.msg]["until"] = time.time() + self._suppression_time
                self._msg_data[record.msg]["num_suppressed"] = 0
                record.msg = newmsg
            else:
                self._msg_data[record.msg] = {"until": time.time() + self._suppression_time, "num_suppressed": 0}
        return True


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def get_parser() -> argparse.ArgumentParser:
    """Get the argument parser for the :code:`powercounter` command."""
    parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers()

    # Options for all commands
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Increase the verbosity by setting the logging level to DEBUG.",
    )
    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        default=False,
        help="Decrease the verbosity by setting the logging level to CRITICAL.",
    )
    parser.add_argument(
        "--suppress-time",
        default=60,
        type=float,
        help="Suppress duplicate warnings or errors for the given amount of seconds. Default: %(default)s",
    )
    parser.add_argument(
        "-d",
        "--device",
        help="The serial port device to open. Default: %(default)s.",
        action="store",
        default="/dev/ttyUSB0",
    )
    parser.add_argument(
        "-i",
        "--input-file",
        metavar="DATAFILE",
        help="Instead of using a serial port, read the data from "
        "the specified data file (previously captured using the -c option).",
        action="store",
        default=None,
    )

    # Add commands
    add_capture_parser(subparsers)
    add_print_parser(subparsers)
    add_publish_parser(subparsers)

    return parser


def _initialize_logging(args: Any) -> None:
    """Initialize the logging module."""
    log_format = "%(asctime)s [%(levelname)s]: %(message)s"
    log_level = logging.INFO
    if args.silent:
        log_level = logging.CRITICAL
    elif args.verbose:
        log_level = logging.DEBUG
    logging.basicConfig(format=log_format, level=log_level)

    if args.suppress_time > 0:
        LOGGER.addFilter(LoggingSuppressionFilter(args.suppress_time))


def power_counter() -> bool:
    """Execute the main function if called as :code:`powercounter`.

    Return:
        Returns True on success, otherwise False.
    """
    parser = get_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        _initialize_logging(args)
        return args.func(args)

    parser.error("Please specify a subcommand!")
    return False
