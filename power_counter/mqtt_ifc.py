# -*- coding: utf-8 -*-
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
import time

import paho.mqtt.client as mqtt


# -----------------------------------------------------------------------------
# Class Definitions
# -----------------------------------------------------------------------------
class MqttInterface:
    """This class represents the MQTT interface to send the current values."""

    def __init__(self, args):
        """Construct a new MqttInterface object.

        Args:
            args (obj): The arguments object.
        """
        self.topics = {}
        for item in args.mqtt_topics.split(','):
            if item.count('=') == 1:
                obis, topic = item.split('=')
                self.topics[obis] = topic
            else:
                print("ERROR: Ignoring MQTT item %s. "
                      "Please use <OBIS ID>=<MQTT Topic> items!" % item)

        self.client = mqtt.Client("powercounter")
        self.client.username_pw_set(args.mqtt_username, args.mqtt_password)
        self.client.connect_async(args.mqtt_host, args.mqtt_port)
        self.client.loop_start()

        # To allow the client to connect to the broker
        time.sleep(1)

    def close(self):
        """Close the connection."""
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, obis_id, value):
        """Publish a new value.

        Args:
            obis_id (str): The OBIS ID as a string, e.g., "1-0:1.8.0*255".
            value (float): Value to publish.
        """
        if obis_id in self.topics:
            ret = self.client.publish(self.topics[obis_id], value)
            if ret.rc == mqtt.MQTT_ERR_NO_CONN:
                print("ERROR: MQTT Client is not connected!")
            elif ret.rc == mqtt.MQTT_ERR_QUEUE_SIZE:
                print("ERROR: MQTT Client queue size exceeded!")


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
