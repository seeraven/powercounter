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
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional, Tuple, Union, get_args, get_origin

from .sml_types import FieldType

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
LOGGER = logging.getLogger()


# -----------------------------------------------------------------------------
# Types
# -----------------------------------------------------------------------------
TimeType = Union[int, datetime]
# Elements: Name, Status, Time, Unit, Scaler, Value, ValueSignature
ListEntryType = Tuple[str, Optional[int], TimeType, str, int, int, bytes]
SmlMessageType = Union["SmlMessageOpenResponse", "SmlMessageCloseResponse", "SmlMessageGetListResponse"]


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def _convert_time(time_field: FieldType) -> Optional[TimeType]:
    """Convert the SML_Time field to an integer (seconds) or a datetime.

    Args:
        time_field (list): The time field (a list of two items).
    Return:
        Returns either an integer representing the number of seconds or
        a datetime to represent a timestamp. None is returned if there
        was an error interpreting the data.
    """
    if isinstance(time_field, list):
        if len(time_field) == 2 and isinstance(time_field[0], int):
            if time_field[0] == 1 and isinstance(time_field[1], int):
                return int(time_field[1])
            if time_field[0] == 2 and isinstance(time_field[1], int):
                return datetime.fromtimestamp(time_field[1])
            if (
                time_field[0] == 3
                and isinstance(time_field[1], list)
                and len(time_field[1]) == 3
                and isinstance(time_field[1][0], int)
            ):
                return datetime.fromtimestamp(time_field[1][0])
            LOGGER.error("Can't convert time field with time type nr %d!", time_field[0])
        else:
            LOGGER.error("Can't convert time field with time type field type %s (expected int)!", type(time_field[0]))
    elif isinstance(time_field, int):
        return time_field
    else:
        LOGGER.error("Can't convert time field of type %s!", type(time_field))
    return None


# -----------------------------------------------------------------------------
# Helper Functions for Messages in Dataclasses
# -----------------------------------------------------------------------------
def _is_sml_optional_none(field: FieldType) -> bool:
    """Check the given (optional) field whether it is None.

    Args:
        field (FieldType): The optional field.
    Return:
        Returns True if the optional field is marked as None.
    """
    return isinstance(field, bytes) and len(field) == 0


def _get_matching_msg_types(dataclass_type):
    """Determine the compatible types of the message fields for a given dataclass type.

    Args:
        dataclass_type (type) - The type in the dataclass.
    Returns:
        Returns a set of python types of the message field that are
        compatible with the dataclass_type.
    """
    if dataclass_type is Any:
        return {bool, bytes, int, list}
    if dataclass_type is str:
        return {bytes}
    if get_origin(dataclass_type) is None:
        return {dataclass_type}
    if get_origin(dataclass_type) is list:
        return {list}
    if get_origin(dataclass_type) is Union:
        ret_set = set()
        sub_types = list(get_args(dataclass_type))
        if all(time_subtype in sub_types for time_subtype in get_args(TimeType)):
            ret_set.update({int, list})
            for time_subtype in get_args(TimeType):
                sub_types.remove(time_subtype)
        for sub_type in sub_types:
            if sub_type is type(None):
                ret_set.add(bytes)
            else:
                ret_set.update(_get_matching_msg_types(sub_type))
        return ret_set
    LOGGER.error("Can't determine matching message type for dataclass type %s!", get_origin(dataclass_type))
    return set()


def _input_matches_fields(cls, data: FieldType) -> bool:
    """Check the input to match the dataclass definition.

    Args:
        cls (class)      - The dataclass.
        data (FieldType) - The input data.
    Returns:
        Returns True if the input matches.
    """
    if isinstance(data, list):
        if len(data) == len(cls.__dataclass_fields__):
            mismatches = []
            for idx, field_obj in enumerate(cls.__dataclass_fields__.values()):
                matching_types = _get_matching_msg_types(field_obj.type)
                if type(data[idx]) not in matching_types:
                    mismatches.append(
                        f"Data field {field_obj.name:<20} (#{idx}) has type {str(type(data[idx])):<20} "
                        f"but spec expects one of {matching_types}"
                    )
            if mismatches:
                LOGGER.error(
                    "Data for %s does not match field definition. The following mismatches were identified:",
                    cls.__name__,
                )
                for mismatch in mismatches:
                    LOGGER.error(" - %s", mismatch)
                return False
            return True
        LOGGER.error(
            "Data for %s must be encoded as a list of %d elements, but data consists of %d elements.",
            cls.__name__,
            len(cls.__dataclass_fields__),
            len(data),
        )
    else:
        LOGGER.error("Data for %s must be of type list, but the given input type was %s.", cls.__name__, type(data))
    return False


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------
@dataclass
class SmlRawMessageData:
    """Raw message data extracted from an SML file."""

    transaction_id: bytes
    group_number: int
    abort_on_error: int
    message_body: List[FieldType]
    crc16: Union[int, bytes]
    end_of_sml_msg: Any  # Spec requires bytes type (of length 0), but often used for other data

    @staticmethod
    def from_field_list(message: FieldType) -> Optional["SmlRawMessageData"]:
        """Convert the given list of fields into a SmlRawMessageData object.

        Args:
            message (list): List of fields as extracted by the SmlFile object.
        Returns:
            Returns a new SmlRawMessageData object or None if the fields do not match.
        """
        if _input_matches_fields(SmlRawMessageData, message):
            return SmlRawMessageData(
                message[0], message[1], message[2], message[3], message[4], message[5]  # type: ignore
            )

        return None


@dataclass
class SmlMessageOpenResponse:
    """Representation of the open response message."""

    codepage: Optional[str]
    client_id: Optional[bytes]
    req_file_id: bytes
    server_id: bytes
    ref_time: Optional[TimeType]
    sml_version: Union[int, bytes]  # Spec requires int, but some implementations use bytes

    def __str__(self) -> str:
        """Return the string representation of this object."""
        ret = "SML-Message OpenResponse: "
        if self.codepage is not None:
            ret += f"Codepage={self.codepage}, "
        if self.client_id is not None:
            ret += f"ClientId={self.client_id!r}, "
        ret += f"ReqFileId={self.req_file_id!r}, "
        ret += f"ServerId={self.server_id!r}, "
        if self.ref_time is not None:
            ret += f"RefTime={self.ref_time}, "
        ret += f"SmlVersion={self.sml_version!r}"
        return ret

    @staticmethod
    def from_raw_message(message: SmlRawMessageData) -> Optional["SmlMessageOpenResponse"]:
        """Convert the given SmlRawMessageData into a SmlMessageOpenResponse object.

        Args:
            message (SmlRawMessageData): Raw message object.
        Returns:
            Returns a new SmlMessageOpenResponse object or None if the fields do not match.
        """
        if _input_matches_fields(SmlMessageOpenResponse, message.message_body[1]):
            fields = message.message_body[1]
            assert isinstance(fields, list)
            if fields[0]:
                assert isinstance(fields[0], bytes)
                codepage = fields[0].decode(encoding="iso-8859-15", errors="ignore")
            else:
                codepage = "iso-8859-15"
            # Note: Type checking already done in _input_matches_fields!
            return SmlMessageOpenResponse(
                codepage=codepage,
                client_id=None if _is_sml_optional_none(fields[1]) else fields[1],  # type: ignore
                req_file_id=fields[2],  # type: ignore
                server_id=fields[3],  # type: ignore
                ref_time=None if _is_sml_optional_none(fields[4]) else _convert_time(fields[4]),  # type: ignore
                sml_version=1 if _is_sml_optional_none(fields[5]) else int(fields[5]),  # type: ignore
            )
        return None


@dataclass
class SmlMessageCloseResponse:
    """Representation of the close response message."""

    global_signature: Optional[bytes]

    def __str__(self) -> str:
        """Return the string representation of this object."""
        ret = "SML-Message CloseResponse: "
        if self.global_signature is not None:
            ret += f"GlobalSignature={self.global_signature!r}"
        return ret

    @staticmethod
    def from_raw_message(message: SmlRawMessageData) -> Optional["SmlMessageCloseResponse"]:
        """Convert the given SmlRawMessageData into a SmlMessageCloseResponse object.

        Args:
            message (SmlRawMessageData): Raw message object.
        Returns:
            Returns a new SmlMessageCloseResponse object or None if the fields do not match.
        """
        if _input_matches_fields(SmlMessageCloseResponse, message.message_body[1]):
            fields = message.message_body[1]
            return SmlMessageCloseResponse(
                global_signature=None if _is_sml_optional_none(fields[0]) else fields[0]  # type: ignore
            )

        return None


@dataclass
class SmlListEntry:
    """Element of the SmlMessageGetListResponse message."""

    obj_name: str
    status: Optional[int]
    val_time: Optional[TimeType]
    unit_raw: Optional[int]
    scaler: Optional[int]
    value: Union[int, bytes]
    value_signature: Optional[bytes]

    def __str__(self) -> str:
        """Return the string representation of this object."""
        ret = f"ObjName={self.obj_name}, "
        if self.status is not None:
            ret += f"Status=0x{self.status:x}, "
        if self.val_time is not None:
            ret += f"ValTime={self.val_time}, "
        if self.unit is not None:
            ret += f"Unit={self.unit}, "
        if self.scaler is not None:
            ret += f"Scaler={self.scaler}, "
        ret += f"Value={self.value!r}"
        if self.value_signature is not None:
            ret += f", ValueSignature={self.value_signature!r}"
        return ret

    @property
    def unit(self) -> Optional[str]:
        """Return the unit as a string."""
        if self.unit_raw is None:
            return None
        if self.unit_raw == 30:
            return "Wh"
        if self.unit_raw == 27:
            return "W"
        return str(self.unit_raw)

    @staticmethod
    def from_fields(list_item: FieldType) -> Optional["SmlListEntry"]:
        """Convert the given list of fields into a SmlListEntry object.

        Args:
            list_item (FieldType): List of fields as extracted by the SmlFile object.
        Returns:
            Returns a new SmlListEntry object or None if the fields do not match.
        """
        if _input_matches_fields(SmlListEntry, list_item):
            if len(list_item[0]) == 6:  # type: ignore
                obj = list_item[0]  # type: ignore
                obj_name = f"{obj[0]}-{obj[1]}:{obj[2]}.{obj[3]}.{obj[4]}*{obj[5]}"  # type: ignore
            else:
                obj_name = str(list_item[0])  # type: ignore
            return SmlListEntry(
                obj_name=obj_name,
                status=None if _is_sml_optional_none(list_item[1]) else list_item[1],  # type: ignore
                val_time=(None if _is_sml_optional_none(list_item[2]) else _convert_time(list_item[2])),  # type: ignore
                unit_raw=None if _is_sml_optional_none(list_item[3]) else list_item[3],  # type: ignore
                scaler=None if _is_sml_optional_none(list_item[4]) else list_item[4],  # type: ignore
                value=list_item[5],  # type: ignore
                value_signature=None if _is_sml_optional_none(list_item[6]) else list_item[6],  # type: ignore
            )
        return None


@dataclass
class SmlMessageGetListResponse:
    """Representation of the close response message."""

    client_id: Optional[bytes]
    server_id: bytes
    list_name: Optional[bytes]
    act_sensor_time: Optional[TimeType]
    list_entries: List[SmlListEntry]
    list_signature: Optional[bytes]
    act_gateway_time: Optional[TimeType]

    def __str__(self) -> str:
        """Return the string representation of this object."""
        ret = "SML-Message GetListResponse: "
        if self.client_id is not None:
            ret += f"ClientId={self.client_id!r}, "
        ret += f"ServerId={self.server_id!r}, "
        if self.list_name is not None:
            ret += f"ListName={self.list_name!r}, "
        if self.act_sensor_time is not None:
            ret += f"ActSensorTime={self.act_sensor_time}, "
        if self.list_signature is not None:
            ret += f"ListSignature={self.list_signature!r}, "
        if self.act_gateway_time is not None:
            ret += f"ActGatewayTime={self.act_gateway_time}"
        for item in self.list_entries:
            ret += "\n" + str(item)
        return ret

    # pylint: disable=too-many-branches
    @staticmethod
    def from_raw_message(message: SmlRawMessageData) -> Optional["SmlMessageGetListResponse"]:
        """Convert the given SmlRawMessageData into a SmlMessageGetListResponse object.

        Args:
            message (SmlRawMessageData): Raw message object.
        Returns:
            Returns a new SmlMessageGetListResponse object or None if the fields do not match.
        """
        if _input_matches_fields(SmlMessageGetListResponse, message.message_body[1]):
            fields = message.message_body[1]
            list_entries = []
            for item in fields[4]:  # type: ignore
                list_entry = SmlListEntry.from_fields(item)
                if list_entry:
                    list_entries.append(list_entry)
            return SmlMessageGetListResponse(
                client_id=None if _is_sml_optional_none(fields[0]) else fields[0],  # type: ignore
                server_id=fields[1],  # type: ignore
                list_name=None if _is_sml_optional_none(fields[2]) else fields[2],  # type: ignore
                act_sensor_time=None if _is_sml_optional_none(fields[3]) else _convert_time(fields[3]),  # type: ignore
                list_entries=list_entries,
                list_signature=None if _is_sml_optional_none(fields[5]) else fields[5],  # type: ignore
                act_gateway_time=None if _is_sml_optional_none(fields[6]) else _convert_time(fields[6]),  # type: ignore
            )
        return None


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def get_message(raw_message: SmlRawMessageData) -> Optional[SmlMessageType]:
    """Get a new SmlMessage object or None if the message type is unknown.

    Args:
        raw_message (SmlRawMessageData): An extracted raw SML message data object.

    Return:
        Returns the corresponding SmlMessage object or None if the message
        type is unknown/unsupported.
    """
    if len(raw_message.message_body) > 1:
        message_type = raw_message.message_body[0]
        if message_type == 0x00000101:
            return SmlMessageOpenResponse.from_raw_message(raw_message)
        if message_type == 0x00000201:
            return SmlMessageCloseResponse.from_raw_message(raw_message)
        if message_type == 0x00000701:
            return SmlMessageGetListResponse.from_raw_message(raw_message)
    return None
