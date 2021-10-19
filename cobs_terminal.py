#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import sys, argparse, time
import serial, serial.tools.list_ports, serial.threaded
from cobs import cobs
import serial_cobs
try:
    import readline
except:
    pass

debug = False
hex_fmt = False

def print_hex(data, fid = sys.stdout):
	for i in range(0, len(data)):
		print('%02X'%data[i],end=' ',file=fid)
	print('',file=fid)

class SerialCOBSCat(serial_cobs.COBSPacketizer):
	
	def handle_packet(self, packet):
		if debug:
			sys.stdout.write('\033[96m')
			print_hex(packet + self.TERMINATOR)
			sys.stdout.write('\033[92m')
			sys.stdout.flush()
		self.handle_cobs(cobs.decode(packet))
	
	def handle_cobs(self, data):
		sys.stdout.buffer.write(bytes('\033[95m'.encode()))
		if hex_fmt:
			print_hex(data)
		else:
			sys.stdout.buffer.write(data+b'\r\n')
		sys.stdout.buffer.write(bytes('\033[92m'.encode()))
		sys.stdout.flush()
	
	def write_cobs(self, data):
		packet = cobs.encode(data) + self.TERMINATOR
		self.transport.write(packet)
		if debug:
			sys.stdout.write('\033[93m')
			print_hex(packet)
			sys.stdout.write('\033[92m')
			sys.stdout.flush()

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser('cobs_terminal', description = "serial terminal with COBS")
	parser.add_argument('port', nargs='?', help='serial port')
	parser.add_argument('-b', '--baud', type=int, default=115200, help='serial port baudrate')
	parser.add_argument('-f', '--fmt', type=str, default='raw', help='data format (raw|hex), default: raw')
	parser.add_argument('-d', '--debug', action='store_true', help='show raw data')
	parser.add_argument('-l', '--list', action='store_true', help='list of available serial ports')
	
	args = parser.parse_args()
	
	if args.list:
		for element in list(serial.tools.list_ports.comports()):
			print(element)
		sys.exit()
	
	try:
		ser = serial.serial_for_url(args.port, args.baud, timeout = 1)
	except serial.SerialException:
		print('\033[91mError: Port %s not found!'%args.port, file=sys.stderr)
		sys.exit(-1)
	except ValueError:
		print('\033[91mError: Incorrect serial port parameters!', file=sys.stderr)
		sys.exit(-1)
	
	if args.fmt == 'hex':
		hex_fmt = True
	elif args.fmt == 'raw':
		hex_fmt = False
	else:
		print('\033[91mError: Incorrect data format!', file=sys.stderr)
		sys.exit(-1)
	
	debug = args.debug
	
	print('\033[2J\033[0;0H',end='')
	sys.stdout.flush()

	thread = serial.threaded.ReaderThread(ser, SerialCOBSCat)
	thread.start()
	
	(transport, protocol) = thread.connect()
	
	try:
		while True:
			data = input('\033[92m')
			if hex_fmt:
				try:
					data_raw = bytes.fromhex(data.rstrip().replace(' ', ''))
				except ValueError:
					print('\033[91mValueError: non-hexadecimal number found', file=sys.stderr)
					continue
				protocol.write_cobs(data_raw)
			else:
				protocol.write_cobs(data.encode())
	except KeyboardInterrupt:
		pass
	
	thread.close()
	ser.close()
