import serial
import sys
import time

port  = '/dev/ttyS5'

try:
    ser = serial.Serial(port, 115200, timeout=1)
except serial.SerialException:
    print('\033[91mError: Port %s not found!' % port, file=sys.stderr)
    sys.exit(-1)
except ValueError:
    print('\033[91mError: Incorrect serial port parameters!', file=sys.stderr)
    sys.exit(-1)

ser.write(b'd')
time.sleep(0.1)
a = ser.readline()
a = float(str(a.rstrip().lstrip().decode('utf-8')))
print(a)

ser.close()