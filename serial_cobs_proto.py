#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from serial_cobs import COBSPacketizer
from google.protobuf.message import Message
from google.protobuf.json_format import MessageToDict, ParseDict, MessageToJson, Parse

from random import randrange
import json


class ProtoCOBS(COBSPacketizer):
    """
	Read and write COBS framed protobuf packets from/to serial port.
	"""

    in_msg = None

    def set_msg_class(self, msg):
        self.in_msg = msg

    def handle_cobs(self, data):
        self.in_msg.ParseFromString(data)
        self.handle_msg(self.in_msg)

    def handle_msg(self, msg):
        """Process messages - to be overridden by subclassing"""
        raise NotImplementedError('please implement functionality in handle_msg')

    def write_msg(self, msg):
        self.write_cobs(msg.SerializeToString())


class ProtoCOBSDict(ProtoCOBS):
    """
	Read and write COBS framed protobuf packets from/to serial port using dict.
	"""

    def handle_msg(self, msg):
        self.handle_msg_dict(MessageToDict(msg))

    def handle_msg_dict(self, data):
        """Process message dict - to be overridden by subclassing"""
        raise NotImplementedError('please implement functionality in handle_msg_dict')

    def write_msg_dict(self, data, msg):
        self.write_msg(ParseDict(data, msg))


class ProtoCOBSJSON(ProtoCOBS):
    """
	Read and write COBS framed protobuf packets from/to serial port using JSON.
	"""

    def handle_msg(self, msg):
        self.handle_msg_json(MessageToJson(msg, including_default_value_fields=True))

    def handle_msg_json(self, data):
        """Process message JSON - to be overridden by subclassing"""
        raise NotImplementedError('please implement functionality in handle_msg_dict')

    def write_msg_json(self, data, msg):
        jsn = Parse(data, msg)
        self.write_msg(jsn)
