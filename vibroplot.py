#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

'''
function intFromBytesLE(x) {
    var val = 0;
    for (var i = x.length-1; i >= 0; --i) {        
        val = (val << 8) + x[i];
    }
    return val;
}
// Decode decodes an array of bytes into an object.
//  - fPort contains the LoRaWAN fPort number
//  - bytes is an array of bytes, e.g. [225, 230, 255, 0]
// The function must return an object, e.g. {"temperature": 22.5}
function Decode(fPort, bytes) {
  if(fPort == 2) {
    var X = intFromBytesLE(bytes.slice(0,4))/65536.0;
    var Y = intFromBytesLE(bytes.slice(4,8))/65536.0;
    var Z = intFromBytesLE(bytes.slice(8,12))/65536.0;
    var temp = intFromBytesLE(bytes.slice(12,14))/16.0;
    var Total = Math.sqrt(X*X+Y*Y+Z*Z);
    return {"vibration_mmps":{"axes":[X,Y,Z],"total":Total},"temperature": temp};
  };
  return {};
}
'''

import paho.mqtt.client as mqtt
import json, time, math
import os, sys, argparse, configparser, struct, threading, queue, time
import numpy as np
import matplotlib.pyplot as plt

def draw_thread(rx_queue, term):
	i = 0
	time = []
	temp = []
	vibe_x = []
	vibe_y = []
	vibe_z = []
	vibe_total = []
	fig = plt.figure()
	ax = fig.add_subplot(211)
	hlx, = ax.plot(0, 0, marker = '.', label='x')
	hly, = ax.plot(0, 0, marker = '.', label='y')
	hlz, = ax.plot(0, 0, marker = '.', label='z')
	hlv, = ax.plot(0, 0, marker = '.', label='abs')
	ay = fig.add_subplot(212)
	hlt, = ay.plot(0, 0, marker = '.', label='temperature')
	ax.grid()
	ay.grid()
	ax.set_ylabel('VRMS, мм/с')
	ax.legend(loc='upper left', ncol=1)
	ay.set_xlabel('N')
	ay.set_ylabel('Температура, °C')
	plt.ion()
	fig.show()
	while not term.is_set():
		try:
			(xyz, vt, t) = rx_queue.get(timeout = 0.01)
			while not rx_queue.empty():
				(xyz, vt, t) = rx_queue.get(timeout = 1)
		except queue.Empty:
			fig.canvas.flush_events()
			continue
		try:
			vibe_x.append(xyz[0])
			vibe_y.append(xyz[1])
			vibe_z.append(xyz[2])
			vibe_total.append(vt)
			time.append(i)
			hlv.set_xdata(time)
			hlx.set_xdata(time)
			hly.set_xdata(time)
			hlz.set_xdata(time)
			hlv.set_ydata(vibe_total)
			hlx.set_ydata(vibe_x)
			hly.set_ydata(vibe_y)
			hlz.set_ydata(vibe_z)
			ax.set_xlim(0, i)
			ax.set_ylim(0, math.ceil(max(vibe_total)))
			temp.append(t)
			hlt.set_xdata(time)
			hlt.set_ydata(temp)
			ay.set_xlim(0, i)
			ay.set_ylim(math.floor(min(temp)), math.ceil(max(temp)))
			fig.canvas.draw()
			fig.canvas.flush_events()
			i+=1
		except:
			continue
	fig.close()

topic=''

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
	print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
	client.subscribe(topic)  # Subscribe to the topic, receive any messages published on it	

def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
	print("Message received-> " + msg.topic + "\n" + str(msg.payload) + "\n")  # Print a received msg
	js = json.loads(msg.payload)['object']
	t = js['temperature']
	xyz = js['vibration_mmps']['xyz']
	vt = js['vibration_mmps']['abs']
	rx_queue.put((xyz, vt, t))

if __name__ == "__main__":
	settings = configparser.ConfigParser()
	settings.read('settings_vibroplot.conf')
	
	parser = argparse.ArgumentParser('vibroplot', description = "vibration sensor plotter")
	parser.add_argument('-a', '--address', default=settings.get('mqtt','host'), help='IoT server address')
	parser.add_argument('-p', '--port', type=int, default=settings.get('mqtt','port'), help='IoT server port')
	parser.add_argument('-t', '--topic', default=settings.get('mqtt','topic'), help='MQTT topic')
	
	args = parser.parse_args()
	topic = args.topic
	
	rx_queue = queue.Queue()
	term = threading.Event()
	
	drawing_thread = threading.Thread(target=draw_thread, args=(rx_queue, term))
	drawing_thread.start()
	
	client = mqtt.Client("iottest")  # Create instance of client with client ID “digi_mqtt_test”
	client.on_connect = on_connect  # Define callback function for successful connection
	client.on_message = on_message  # Define callback function for receipt of a message
	client.connect(args.address, args.port)
	client.loop_forever()  # Start networking daemon
	
	term.set()
	drawing_thread.join()
