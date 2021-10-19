#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import os, sys, argparse, configparser, struct, threading, queue, time
import serial_cobs_proto
import serial, serial.tools.list_ports, serial.threaded
from rs_0006_0_icp_pb2 import *
import serial

from cobs import cobs
from google.protobuf.json_format import MessageToDict, ParseDict, MessageToJson, Parse
try:
    import readline
except:
    pass
import numpy as np
import matplotlib.pyplot as plt

rx_queue = []
fid = []

def print_hex(data, fid = sys.stdout):
	for i in range(0, len(data)):
		print('%02X'%data[i],end=' ',file=fid)
	print('',file=fid)

def cls():
	print('\033[2J\033[0;0H',end='')

def update_line(hl, ydata):
	hl.set_ydata(ydata)
	plt.draw()

class ProtoCOBSCat(serial_cobs_proto.ProtoCOBSDict):
	
	def handle_msg(self, msg):
		if len(msg.raw.raw) != 0:
			if(fid != None):
				fid.write(bytes(msg.raw.raw))
				fid.flush()
#			print(len(msg.raw.raw))
#			print_hex(msg.raw.raw)
#			sys.stdout.flush()
			rx_queue.put(msg.raw.raw)
		else:
			self.handle_msg_dict(MessageToDict(msg))
	
	def handle_msg_dict(self, data):
		print('\033[95m', end='')
		print(data)
		print('\033[92m', end='')
		sys.stdout.flush()

def draw_thread(rx_queue, term, frame_size):
	hlx, = plt.plot(np.arange(frame_size)/3.200, np.random.sample(frame_size)*2-1,label='x')
	hly, = plt.plot(np.arange(frame_size)/3.200, np.random.sample(frame_size)*2-1,label='y')
	hlz, = plt.plot(np.arange(frame_size)/3.200, np.random.sample(frame_size)*2-1,label='z')
	plt.ylim(-1.2, 1.4)
	plt.xlim(0, frame_size/3.200)
	plt.grid()
	plt.xlabel('t, мс')
	plt.ylabel('Ускорение, g')
	plt.legend(loc='upper center', ncol=3)
	plt.ion()
	plt.show()
	while not term.is_set():
		try:
			data = rx_queue.get(timeout = 1)
			while not rx_queue.empty():
				data = rx_queue.get(timeout = 1)
		except queue.Empty:
			continue
		try:
			data_np = np.frombuffer(data, dtype=np.int16)
			update_line(hlx, data_np[0::3]*0.004)
			update_line(hly, data_np[1::3]*0.004)
			update_line(hlz, data_np[2::3]*0.004)
			plt.gcf().canvas.flush_events()
		except:
			continue
	plt.close()
	

if __name__ == "__main__":
	settings = configparser.ConfigParser()
	settings.read('settings.conf')
	
	parser = argparse.ArgumentParser('protovib', description = "vibration sensor viewer and logger utility")
	parser.add_argument('-p', '--port', default=settings.get('serial','port'), help='serial port name')
	parser.add_argument('-b', '--baud', type=int, default=int(settings.get('serial','baudrate')), help='serial port baudrate')
	parser.add_argument('-f', '--frame_size', type=int, default=int(settings.get('logger','frame_size')), help='frame size (xyz samples)')
	parser.add_argument('-t', '--timeout', type=float, default=float(settings.get('logger','timeout')), help='logger timeout (s)')
	parser.add_argument('-o', '--output', help='output binary file')
	parser.add_argument('-d', '--draw', action='store_true', help='draw time plots')
	parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
	parser.add_argument('-s', '--stop', action='store_true', help='send "stop logging" command')
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
	
	thread = serial.threaded.ReaderThread(ser, ProtoCOBSCat)
	thread.start()
	(transport, protocol) = thread.connect()
	protocol.set_msg_class(resp())
	
	rx_queue = queue.Queue()
	term = threading.Event()
	
	if args.output != None:
		fid = open(args.output, 'wb')
	
#	protocol.write_msg_dict({'devinfo':{}}, req())
	protocol.write_msg_dict({'raw_start':{}}, req())
	
#	time.sleep(1)
	
	if args.draw:
		drawing_thread = threading.Thread(target=draw_thread, args=(rx_queue, term, args.frame_size))
		drawing_thread.start()
	try:
		time.sleep(args.timeout)
	except KeyboardInterrupt:
		pass
	
	protocol.write_msg_dict({'raw_stop':{}}, req())
	
	time.sleep(2)
	
	term.set()
	
	if args.draw:
		drawing_thread.join()
	thread.close()
	ser.close()
	if args.output != None:
		fid.close()
