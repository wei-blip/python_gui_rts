#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import sys, argparse, time
import serial, serial.tools.list_ports, serial.threaded
import serial_cobs

hex_fmt = False


def print_hex(data, fid = sys.stdout):
	for i in range(0, len(data)):
		print('%02X'%data[i],end=' ',file=fid)
	print('',file=fid)


class SerialCOBSCat(serial_cobs.COBSPacketizer):

	def handle_cobs(self, data):
		if hex_fmt:
			print_hex(data)
		else:
			sys.stdout.buffer.write(data+b'\r\n')
		sys.stdout.flush()


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser('cobs_cat', description = "cat serial COBS framed data")
	parser.add_argument('port', nargs='?', help='serial port')
	parser.add_argument('-b', '--baud', type=int, default=115200, help='serial port baudrate')
	parser.add_argument('-f', '--fmt', type=str, default='raw', help='data format (raw|hex), default: raw')
	parser.add_argument('-l', '--list', action='store_true', help='list of available serial ports')
	
	args = parser.parse_args()
	
	if args.list:
		for element in list(serial.tools.list_ports.comports()):
			print(element)
		sys.exit()
	
	try:
		ser = serial.serial_for_url(args.port, args.baud, timeout = 1)
	except serial.SerialException:
		print('Error: Port %s not found!'%args.port, file=sys.stderr)
		sys.exit(-1)
	except ValueError:
		print('Error: Incorrect serial port parameters!', file=sys.stderr)
		sys.exit(-1)
	
	if args.fmt == 'hex':
		hex_fmt = True
	elif args.fmt == 'raw':
		hex_fmt = False
	else:
		print('Error: Incorrect data format!', file=sys.stderr)
		sys.exit(-1)
	
	protocol = serial.threaded.ReaderThread(ser, SerialCOBSCat)
	protocol.start()
		
	try:
		while True:
#			sys.stdout.flush()
			time.sleep(0.5)
	except KeyboardInterrupt:
		pass
	
	protocol.close()
	ser.close()
