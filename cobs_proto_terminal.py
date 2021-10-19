#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import sys, argparse, time
import serial, serial.tools.list_ports, serial.threaded
from rs_0006_0_icp_pb2 import *
from cobs import cobs
import serial_cobs_proto

try:
    import readline
except:
    pass

debug = False


def print_hex(data, fid=sys.stdout):
    for i in range(0, len(data)):
        print('%02X' % data[i], end=' ', file=fid)
    print('', file=fid)


class ProtoCOBSCat(serial_cobs_proto.ProtoCOBSJSON):

    def handle_packet(self, packet):
        if debug:
            print('\033[96m', end='')
            print_hex(packet + self.TERMINATOR)
            print('\033[92m', end='')
            sys.stdout.flush()
        self.handle_cobs(cobs.decode(packet))

    def handle_cobs(self, data):
        if debug:
            print('\033[95m', end='')
            print_hex(data)
            print('\033[92m', end='')
            sys.stdout.flush()
        self.in_msg.ParseFromString(data)
        self.handle_msg(self.in_msg)

    def write_cobs(self, data):
        if debug:
            print('\033[92m', end='')
            print_hex(data)
            print('\033[92m', end='')
            sys.stdout.flush()
        packet = cobs.encode(data) + self.TERMINATOR
        self.transport.write(packet)
        if debug:
            print('\033[93m', end='')
            print_hex(packet)
            print('\033[92m', end='')
            sys.stdout.flush()

    def handle_msg_json(self, data):
        print('\033[95m', end='')
        print(data)
        print('\033[92m', end='')
        sys.stdout.flush()


def something(ser):
    thread = serial.threaded.ReaderThread(ser, ProtoCOBSCat)  # ?
    thread.start()

    (transport, protocol) = thread.connect()

    protocol.set_msg_class(exch())

    try:
        while True:
            data = '{"req":{"devinfo":{}}}'
            protocol.write_msg_json(data, exch())
    except KeyboardInterrupt:
        pass

    thread.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser('cobs_terminal', description="serial terminal with COBS")  # create new object parser with description = "serial terminal with COBS"
    # create new variable: port, -b, -d, -l
    parser.add_argument('port', nargs='?', help='serial port')
    parser.add_argument('-b', '--baud', type=int, default=115200, help='serial port baudrate')
    parser.add_argument('-d', '--debug', action='store_true', help='show raw data')
    parser.add_argument('-l', '--list', action='store_true', help='list of available serial ports')

    args = parser.parse_args()  # in args variable gets the result of parsing command line arguments

    if args.list:
        for element in list(serial.tools.list_ports.comports()):
            print(element)
        sys.exit()

    try:
        # init serial port: port_number=args.port, baudrate = args.baud, timeout = 1 sec
        ser = serial.serial_for_url(args.port, args.baud, timeout=1)
    except serial.SerialException:
        print('\033[91mError: Port %s not found!' % args.port, file=sys.stderr)
        sys.exit(-1)
    except ValueError:
        print('\033[91mError: Incorrect serial port parameters!', file=sys.stderr)
        sys.exit(-1)

    debug = args.debug

    print('\033[2J\033[0;0H', end='')
    sys.stdout.flush()

    thread = serial.threaded.ReaderThread(ser, ProtoCOBSCat)  # ?
    thread.start()

    (transport, protocol) = thread.connect()

    protocol.set_msg_class(exch())

    try:
        while True:
            data = input('\033[92m')
            protocol.write_msg_json(data, exch())
    except KeyboardInterrupt:
        pass

    thread.close()
    ser.close()
