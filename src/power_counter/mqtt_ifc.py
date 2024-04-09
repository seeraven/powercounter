"""
Module providing the mqtt interface of the powercounter application.

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
import logging
import time
from typing import Any

import paho.mqtt.client as mqtt

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger()


# -----------------------------------------------------------------------------
# Class Definitions
# -----------------------------------------------------------------------------
class MqttInterface:
    """This class represents the MQTT interface to send the current values."""

    def __init__(self, args: Any) -> None:
        """Construct a new MqttInterface object.

        Args:
            args (obj): The arguments object.
        """
        LOGGER.debug("Parsing topic definition string %s.", args.mqtt_topics)
        self.topics = {}
        for item in args.mqtt_topics.split(","):
            if item.count("=") == 1:
                obis, topic = item.split("=")
                self.topics[obis] = topic
                LOGGER.debug("Found OBIS ID %s mapped to MQTT topic %s.", obis, topic)
            else:
                LOGGER.error("Ignoring MQTT item %s. Please use <OBIS ID>=<MQTT Topic> items!", item)

        LOGGER.debug("Create MQTT client and connect to MQTT server %s:%d.", args.mqtt_host, args.mqtt_port)
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="powercounter")
        self.client.username_pw_set(args.mqtt_username, args.mqtt_password)
        self.client.connect_async(args.mqtt_host, args.mqtt_port)
        self.client.loop_start()

        # To allow the client to connect to the broker
        LOGGER.debug("Waiting 1 second to give the client time to connect to the broker.")
        time.sleep(1)

    def close(self) -> None:
        """Close the connection."""
        LOGGER.debug("Close MQTT client.")
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, obis_id: str, value: float) -> None:
        """Publish a new value.

        Args:
            obis_id (str): The OBIS ID as a string, e.g., "1-0:1.8.0*255".
            value (float): Value to publish.
        """
        if obis_id in self.topics:
            LOGGER.debug("Publishing OBIS ID %s on topic %s with value %f.", obis_id, self.topics[obis_id], value)
            ret = self.client.publish(self.topics[obis_id], value)
            if ret.rc == mqtt.MQTT_ERR_NO_CONN:
                LOGGER.error("MQTT client is not connected!")
            elif ret.rc == mqtt.MQTT_ERR_QUEUE_SIZE:
                LOGGER.error("MQTT client queue size exceeded!")
