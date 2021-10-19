import json
import queue
import sys
from random import randrange

from cobs import cobs
from google.protobuf.json_format import Parse

import serial_cobs_proto
from rs_0006_0_icp_pb2 import exch

def print_hex(data, fid=sys.stdout):
    for i in range(0, len(data)):
        print('%02X' % data[i], end=' ', file=fid)
    print('', file=fid)

class DVT19(serial_cobs_proto.ProtoCOBSJSON): # TODO:: need to rename the class and move to a separate file

    def __init__(self, debug=False):
        super(DVT19, self).__init__()
        self.__que = queue.Queue()
        self.__debug=debug

    def handle_packet(self, packet):
        if self.__debug:
            print('\033[96m', end='')
            print_hex(packet + self.TERMINATOR)
            print('\033[92m', end='')
            sys.stdout.flush()
        self.handle_cobs(cobs.decode(packet))

    def handle_cobs(self, data):
        if self.__debug:
            print('\033[95m', end='')
            print_hex(data)
            print('\033[92m', end='')
            sys.stdout.flush()
        self.in_msg.ParseFromString(data)
        self.handle_msg(self.in_msg)

    def write_cobs(self, data):
        if self.__debug:
            print('\033[92m', end='')
            print_hex(data)
            print('\033[92m', end='')
            sys.stdout.flush()
        packet = cobs.encode(data) + self.TERMINATOR
        self.transport.write(packet)
        if self.__debug:
            print('\033[93m', end='')
            print_hex(packet)
            print('\033[92m', end='')
            sys.stdout.flush()

    def handle_msg_json(self, data):
        if self.__debug:
            print('\033[95m', end='')
            print(data)
            print('\033[92m', end='')
        self.__que.put(data)
        sys.stdout.flush()

    def get_queue(self):
        return self.__que

    def get_rf_line_param(self, attempts=25):
        self.set_msg_class(exch())
        n_err = 0
        fei = 0
        rssi = 0
        snr = 0
        req = f'{{"req":{{"devinfo":{{}}}},"transit":true}}'
        for _ in range(0,attempts):
            tmp = self.__multiple_requests_on_failure(req, max_attempts=1, timeout=1)
            if tmp != None:
                fei = fei + tmp.fei
                snr = snr + tmp.snr
                rssi = rssi + tmp.rssi
            else:
                n_err = n_err + 1
        return dict(fei=fei / attempts, rssi=rssi / attempts, snr=snr / attempts, per=n_err / attempts * 100)

    def __multiple_requests_on_failure(self, req, max_attempts=5, timeout=1):
        """ the data request function from DVT sensor, if from sensor don't get the answer
            then after a timeout request will be sent again
            :req            - request data in json format
            :max_attempts   - maximum attempts get data
            :timeout        - time waiting for an answer from the sensor in seconds
            :return         - protobuf object
        """
        self.set_msg_class(exch())
        n = 0
        while n < max_attempts:
            req_id = randrange(0, 2 ** 32 - 1)
            tmp = json.loads(req)
            tmp['req']['req_id'] = req_id
            req = json.dumps(tmp)
            self.write_msg_json(req, exch())
            try:
                data = self.__que.get(block=True, timeout=timeout)
                msg = Parse(data, exch())
                if msg.resp.resp_id == req_id:
                    return msg.resp
            except queue.Empty:
                n = n + 1
        return None

    def get_devinfo(self, max_attempts=5, from_uut=False, timeout=1):
        req = f'{{"req":{{"devinfo":{{}}}},"transit":{str(from_uut).lower()}}}'
        tmp = self.__multiple_requests_on_failure(req, max_attempts=max_attempts, timeout=timeout)
        if tmp is not None:
            return tmp
        else:
            return None

    def get_join_key(self, max_attempts=5, from_uut=False):
        req = f'{{"req":{{"join_key":{{}}}},"transit":{str(from_uut).lower()}}}'
        tmp = self.__multiple_requests_on_failure(req, max_attempts=max_attempts)
        if tmp != None:
            return tmp.join_key
        else:
            return None

    def get_mcu_adc(self, max_attempts=5, from_uut=False):
        req = f'{{"req":{{"mcu_adc":{{}}}},"transit":{str(from_uut).lower()}}}'
        tmp = self.__multiple_requests_on_failure(req, max_attempts=max_attempts)
        if tmp != None:
            return tmp.mcu_adc
        else:
            return None

    def get_temperature(self, max_attempts=5, from_uut=False):
        req = f'{{"req":{{"ds18b20":{{}}}},"transit":{str(from_uut).lower()}}}'
        tmp = self.__multiple_requests_on_failure(req, max_attempts=max_attempts, timeout=2)
        if tmp != None:
            return tmp.ds18b20
        else:
            return None

    def get_vibro(self, max_attempts=5, from_uut=False):
        req = f'{{"req":{{"vibro":{{}}}},"transit":{str(from_uut).lower()}}}'
        tmp = self.__multiple_requests_on_failure(req, max_attempts=max_attempts, timeout=8)
        if tmp != None:
            return tmp.vibro.vrms
        else:
            return None

    def get_adxl345(self, max_attempts=5, from_uut=False):
        req = f'{{"req":{{"adxl345":{{}}}},"transit":{str(from_uut).lower()}}}'
        tmp = self.__multiple_requests_on_failure(req, max_attempts=max_attempts)
        if tmp != None:
            return tmp.adxl345.acc_g
        else:
            return None

    def set_cw_mode(self, freq=868000000, pwr_dbm=0, duration=2):
        req = f'{{"req": {{"cw": {{"cmd": "CW_ON", "cw_param": {{"freq": {freq}, "pwr_dbm": {pwr_dbm}, "duration": {duration} }}}}}}, "transit": true}}'
        self.set_msg_class(exch())
        self.write_msg_json(req, exch())

    def cmd_reboot(self, swap=False, to_uut=False):
        req = f'{{"req":{{"reboot":{{"swap": {str(swap).lower()} }}}},"transit": {str(to_uut).lower()} }}'
        self.set_msg_class(exch())
        tmp = self.__multiple_requests_on_failure(req, max_attempts=1)
        return tmp
