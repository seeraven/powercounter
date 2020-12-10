# -*- coding: utf-8 -*-
"""
SML message representation.

Copyright:
    2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>

    All rights reserved.

    This file is part of powercounter (https://github.com/seeraven/powercounter)
    and is released under the "BSD 3-Clause License". Please see the ``LICENSE`` file
    that is included as part of this package.
"""


# -----------------------------------------------------------------------------
# Module Imports
# -----------------------------------------------------------------------------
from datetime import datetime


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------
# pylint: disable=too-few-public-methods
class SmlMessage:
    """General representation of an SML-message."""

    def __init__(self, data):
        """Construct a new SML-message object."""
        self.transaction_id = data[0]
        self.group_number = data[1]
        self.abort_on_error = data[2]
        self.message_body = data[3]
        self.crc16 = data[4]
        self.end_of_sml_msg = data[5]

    @staticmethod
    def _convert_time(time_data):
        """Convert the given time_data list to a time stamp.

        Args:
            time_data (list): A list of 2 elements.
        Return:
            Returns the python datetime timestamp.
        """
        if isinstance(time_data, list) and len(time_data) == 2:
            if time_data[0] == 1:
                return int(time_data[1])
            if time_data[0] == 2:
                return datetime.fromtimestamp(time_data[1])
            if time_data[0] == 3:
                return datetime.fromtimestamp(time_data[1][0])
        return None

    def __str__(self):
        """Return the string representation of this object."""
        ret = "SML-Message: "
        ret += "TransactionId=%s, " % self.transaction_id
        ret += "GroupNr=%s, " % self.group_number
        ret += "AbortOnError=%s, " % self.abort_on_error
        ret += "Message type=0x%08x, " % self.message_body[0]
        ret += "CRC16=0x%04x" % self.crc16
        return ret


class SmlMessageOpenResponse(SmlMessage):
    """Representation of the open response message."""

    def __init__(self, data):
        """Construct a new SmlMessageOpenResponse object."""
        super().__init__(data)

        if self.message_body[1][0]:
            self.codepage = self.message_body[1][0].decode(encoding='iso-8859-15',
                                                           errors='ignore')
        else:
            self.codepage = 'iso-8859-15'
        self.client_id = self.message_body[1][1]
        self.req_file_id = self.message_body[1][2]
        self.server_id = self.message_body[1][3]
        self.ref_time = self._convert_time(self.message_body[1][4])
        if self.message_body[1][5]:
            self.sml_version = self.message_body[1][5]
        else:
            self.sml_version = 1

    def __str__(self):
        """Return the string representation of this object."""
        ret = "SML-Message OpenResponse: "
        ret += "Codepage=%s, " % self.codepage
        ret += "ClientId=%s, " % self.client_id
        ret += "ReqFileId=%s, " % self.req_file_id
        ret += "ServerId=%s, " % self.server_id
        ret += "RefTime=%s, " % self.ref_time
        ret += "SmlVersion=%d" % self.sml_version
        return ret


class SmlMessageCloseResponse(SmlMessage):
    """Representation of the close response message."""

    def __init__(self, data):
        """Construct a new SmlMessageCloseResponse object."""
        super().__init__(data)

        if self.message_body[1][0]:
            self.global_signature = self.message_body[1][0]
        else:
            self.global_signature = None

    def __str__(self):
        """Return the string representation of this object."""
        ret = "SML-Message CloseResponse: "
        ret += "GlobalSignature=%s" % self.global_signature
        return ret


class SmlMessageGetListResponse(SmlMessage):
    """Representation of the close response message."""

    def __init__(self, data):
        """Construct a new SmlMessageGetListResponse object."""
        super().__init__(data)

        if self.message_body[1][0]:
            self.client_id = self.message_body[1][0]
        else:
            self.client_id = None
        self.server_id = self.message_body[1][1]
        if self.message_body[1][2]:
            self.list_name = self.message_body[1][2]
        else:
            self.list_name = None
        self.act_sensor_time = self._convert_time(self.message_body[1][3])

        self.list_entries = []
        for item in self.message_body[1][4]:
            if not isinstance(item, list):
                continue

            obj_name = item[0]
            if len(obj_name) == 6:
                obj_name = "%d-%d:%d.%d.%d*%d" % (obj_name[0],
                                                  obj_name[1],
                                                  obj_name[2],
                                                  obj_name[3],
                                                  obj_name[4],
                                                  obj_name[5])
            status = item[1] if item[1] else 0
            val_time = self._convert_time(item[2])
            if val_time is None:
                val_time = self.act_sensor_time
            unit = None
            if item[3] == 30:
                unit = "Wh"
            elif item[3] == 27:
                unit = "W"
            elif item[3]:
                unit = int(item[3])
            scaler = item[4] if item[4] else 0
            value = item[5]
            value_signature = item[6]
            self.list_entries.append([obj_name, status, val_time, unit, scaler,
                                      value, value_signature])

        if self.message_body[1][5]:
            self.list_signature = self.message_body[1][5]
        else:
            self.list_signature = None
        self.act_gateway_time = self._convert_time(self.message_body[1][6])

    def __str__(self):
        """Return the string representation of this object."""
        ret = "SML-Message GetListResponse: "
        ret += "ClientId=%s, " % self.client_id
        ret += "ServerId=%s, " % self.server_id
        ret += "ListName=%s, " % self.list_name
        ret += "ActSensorTime=%s, " % self.act_sensor_time
        ret += "ListSignature=%s, " % self.list_signature
        ret += "ActGatewayTime=%s" % self.act_gateway_time
        for item in self.list_entries:
            ret += "\n"
            ret += " - ObjName=%s, " % item[0]
            ret += "Status=0x%x, " % item[1]
            ret += "ValTime=%s, " % item[2]
            ret += "Unit=%s, " % item[3]
            ret += "Scaler=10^%d, " % item[4]
            ret += "Value=%s, " % item[5]
            ret += "ValueSignature=%s" % item[6]
        return ret


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def get_message(data):
    """Get a new SmlMessage object or None if the message type is unknown.

    Args:
        data (list): A list of 6 elements extracted by the SmlFile class.

    Return:
        Returns the corresponding SmlMessage object or None if the message
        type is unknown/unsupported.
    """
    if (len(data) == 6) and (len(data[3]) == 2):
        message_type = data[3][0]
        if message_type == 0x00000101:
            return SmlMessageOpenResponse(data)
        if message_type == 0x00000201:
            return SmlMessageCloseResponse(data)
        if message_type == 0x00000701:
            return SmlMessageGetListResponse(data)
    return None


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
