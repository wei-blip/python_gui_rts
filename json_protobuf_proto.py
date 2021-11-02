from google.protobuf.json_format import MessageToDict, ParseDict, MessageToJson, Parse
from rs_0006_0_icp_pb2 import *
from cobs import cobs
import json


class JSONProtobufProto:
    def __init__(self):
        super().__init__()

        # Receive attribute begin
        self.in_msg = exch()  # in_msg is a Protobuf message
        self.json_string = '{}'  # output_data is data from device
        self.free = False
        # Receive attribute end

        # Transmit attribute begin
        self.TERMINATOR = b'\0'
        self.transport = None  # transport is a socket
        # Transmit attribute end

    # Receive methods begin
    def handle_msg_json(self, data):
        self.json_string = data
        self.free = True

    def handle_msg(self, msg):
        self.handle_msg_json(MessageToJson(msg, including_default_value_fields=True))

    def handle_cobs(self, data):
        self.in_msg.ParseFromString(data)
        self.handle_msg(self.in_msg)

    def handle_packet(self, packet):
        self.handle_cobs(cobs.decode(packet))
    # Receive methods end

    # Transmit methods begin
    def write_cobs(self, data):
        packet = cobs.encode(data) + self.TERMINATOR
        self.transport.send(packet)

    def write_msg_json(self, data, msg):
        jsn = Parse(data, msg)
        self.write_msg(jsn)

    def write_msg(self, msg):
        self.write_cobs(msg.SerializeToString())
    # Transmit methods end


