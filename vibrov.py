#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import os, sys, argparse, configparser, struct, threading, queue, time
from cobs import cobs
import serial
try:
    import readline
except:
    pass
import numpy as np
import matplotlib.pyplot as plt

def print_hex(data, fid = sys.stdout):
	for i in range(0, len(data)):
		print('%02X'%data[i],end=' ',file=fid)
	print('',file=fid)

def cls():
	print('\033[2J\033[0;0H',end='')

def update_line(hl, ydata):
	hl.set_ydata(ydata)
	plt.draw()

def send_cmd(ser, code, timeout):
	cmd_fmt = '<B3BI'
	cmd_struct = {
		'code'		: code,
		'rsvd0'		: 0x00,
		'rsvd1'		: 0x00,
		'rsvd2'		: 0x00,
		'timeout'	: int(timeout*1000)
	}
	cmd = struct.pack(cmd_fmt, *cmd_struct.values())
	data_to_send = bytearray(cobs.encode(cmd))
	data_to_send.append(0x00)
	ser.write(bytes(data_to_send))
	

def cobs_syncronize(ser, term):
	while not term.is_set():
		c = ser.read(1)
		if c:
			if c == b'\x00':
				break

def rx_thread(ser, rx_queue, term, frame_size, output = None):
	if(output != None):
		fid = open(output, 'wb')
	cobs_syncronize(ser, term)
	while not term.is_set():
		line = bytearray()
		line = ser.read(frame_size*6+2)
		while not term.is_set():
			if line[-1] == 0:
				break
			line += ser.read(1)
		try:
			data = cobs.decode(line[:-1])
		except:
			cobs_syncronize(ser, term)
		if len(data) == frame_size*6:
			if(output != None):
				fid.write(bytes(data))
				fid.flush()
			rx_queue.put(data)
	if(output != None):
		fid.close()

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
	
	parser = argparse.ArgumentParser('vibrov', description = "vibration sensor viewer and logger utility")
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
		ser = serial.Serial(args.port, args.baud, timeout = 1)
	except serial.SerialException:
		print('Error: Port %s not found!'%args.port, file=sys.stderr)
		sys.exit(-1)
	except ValueError:
		print('Error: Incorrect serial port parameters!', file=sys.stderr)
		sys.exit(-1)
	
	cmd_code = 0x01
	
	if args.stop:
		send_cmd(ser, 0x00, 0)
		ser.close()
		sys.exit()
	
	send_cmd(ser, 0x01, args.timeout)
	
	rx_queue = queue.Queue()
	term = threading.Event()
	reception_thread = threading.Thread(target=rx_thread, args=(ser, rx_queue, term, args.frame_size, args.output))
	reception_thread.start()
	if args.draw:
		drawing_thread = threading.Thread(target=draw_thread, args=(rx_queue, term, args.frame_size))
		drawing_thread.start()
	try:
		time.sleep(args.timeout)
	except KeyboardInterrupt:
		pass
		
	term.set()
	reception_thread.join()
	send_cmd(ser, 0x00, 0)
	if args.draw:
		drawing_thread.join()
	ser.close()
