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
        self.topic = args.mqtt_topic
        self.client = mqtt.Client("powercounter")
        self.client.username_pw_set(args.mqtt_username, args.mqtt_password)
        self.client.connect(args.mqtt_host, args.mqtt_port)
        self.client.loop_start()

    def close(self):
        """Close the connection."""
        self.client.disconnect()
        self.client.loop_stop()

    def publish(self, value):
        """Publish a new value.

        Args:
            value (float): Value to publish.
        """
        self.client.publish(self.topic, value)


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
