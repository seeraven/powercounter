PowerCounter
============

Synopsis
--------

powercounter [-h|--help] [-d DEVICE] [-c DATAFILE] [-i DATAFILE] [--mqtt-host MQTT_HOST] [--mqtt-port MQTT_PORT] [--mqtt-username MQTT_USERNAME] [--mqtt-password MQTT_PASSWORD] [--mqtt-topic MQTT_TOPIC]


Description
-----------

Python based application to analyze the data of a electricity meter sent over
an infrared LED using an USB UART adapter. The extracted data is sent via MQTT.


Options of PowerCounter
-----------------------

-h, --help                          Show the general help.
-d DEVICE, --device DEVICE          The serial port device to open. Default: :code:`/dev/ttyUSB0`.
-c DATAFILE, --capture DATAFILE     Capture raw data from the serial port and store it in the given file.
-i DATAFILE, --input-file DATAFILE  Instead of using a serial port, read the data from the specified data
                                    file (previously captured using the :code:`-c` option).
--mqtt-host MQTT_HOST               MQTT host. [Default: :code:`192.168.1.70`]
--mqtt-port MQTT_PORT               MQTT port. [Default: :code:`1883`]
--mqtt-username MQTT_USERNAME       MQTT username. [Default: :code:`mqtt`]
--mqtt-password MQTT_PASSWORD       MQTT password. [Default: :code:`mqtt`]
--mqtt-topic MQTT_TOPIC             MQTT topic. [Default: :code:`counters/power`]


License
-------

powercounter (https://github.com/seeraven/powercounter) is released under the
"BSD 3-Clause License". Please see the LICENSE file that is included as part of this package.
