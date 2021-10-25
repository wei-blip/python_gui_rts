from google.protobuf.json_format import MessageToDict, ParseDict, MessageToJson, Parse
from rs_0006_0_icp_pb2 import *
from cobs import cobs


class JSONProtobufProtoTx:
    def __init__(self):
        self.TERMINATOR = b'\0'
        self.transport = None  # transport is a socket

    def write_cobs(self, data):
        packet = cobs.encode(data) + self.TERMINATOR
        self.transport.send(packet)

    def write_msg_json(self, data, msg):
        jsn = Parse(data, msg)
        self.write_msg(jsn)

    def write_msg(self, msg):
        self.write_cobs(msg.SerializeToString())


class JSONProtobufProtoRx:
    def __init__(self):
        self.in_msg = None  # in_msg is a Protobuf message
        self.output_data = None  # output_data is data from device

    def handle_msg_json(self, data):
        self.output_data = data

    def handle_msg(self, msg):
        self.handle_msg_json(MessageToJson(msg, including_default_value_fields=True))

    def handle_cobs(self, data):
        self.in_msg.ParseFromString(data)
        self.handle_msg(self.in_msg)

    def handle_packet(self, packet):
        self.handle_cobs(cobs.decode(packet))


class JSONProtobufProto(JSONProtobufProtoTx, JSONProtobufProtoRx):
    def __init__(self):
        super().__init__()
