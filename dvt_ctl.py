#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import db
import sys
import argparse
import time
import serial.tools.list_ports
import serial.threaded

import DVT19
import copy
import configparser

from ChrpStck import ChirpStack
from RTS_Things import RTS_Things

if __name__ == "__main__":

    parser = argparse.ArgumentParser('dvt_ctl', description="DVT19 instrumentation")
    parser.add_argument('uut_sn', nargs='?', help='UUT DVT19 serial number')
    parser.add_argument('-f', '--config-filename', default='dvt_ctl.ini', help='configuration filename')
    parser.add_argument('-c', '--comment', default='', help='DB comment')
    args = parser.parse_args()
    cfg = configparser.ConfigParser()
    cfg.read(args.config_filename)

    print(cfg['ChirpStack']['nwk_key'])
    if args.uut_sn is None:
        print('UUT serial number is required.')
        print(f'usage: {parser.prog}.py {{serial}}')
        quit()

#    print(args.uut_sn)
#    quit()

    try:
        ser = serial.serial_for_url(cfg['DVT19']['port'], cfg['DVT19']['baud'], timeout=1)
    except serial.SerialException:
        print('\033[91mError: Port %s not found!' % cfg['DVT19']['port'], file=sys.stderr)
        for element in list(serial.tools.list_ports.comports()):
            print(element)
        sys.exit(-1)
    except ValueError:
        print('\033[91mError: Incorrect serial port parameters!', file=sys.stderr)
        sys.exit(-1)

    ser.reset_input_buffer()
    ser.reset_output_buffer()

    with_power_meas = False
    if cfg['PWR_meter']['enable'] == 'yes':
        pwrm_ser = serial.Serial()
        pwrm_ser.port = cfg['PWR_meter']['port']
        pwrm_ser.baud = 115200
        pwrm_ser.timeout = 1
        with_power_meas = True
        try:
            pwrm_ser.open()
        except serial.SerialException:
            print('\033[91mError: Port %s not found!' % pwrm_ser.port, file=sys.stderr)
            for element in list(serial.tools.list_ports.comports()):
                print(element)
            sys.exit(-1)
        except ValueError:
            print('\033[91mError: Incorrect serial port parameters!', file=sys.stderr)
            sys.exit(-1)

    things_board = RTS_Things(cfg['ThingsBoard']['url'], cfg['ThingsBoard']['username'],
                              password=cfg['ThingsBoard']['password'])
    if not things_board.is_logged:
        print("ThingsBoard connection error!")
        quit()
    if things_board.get_device_id_by_name(args.uut_sn) is not None:
        print(f'devise {args.uut_sn} already exists in ThingsBoard. Exit!')
 #       quit()

    chirp_stack = ChirpStack(cfg['ChirpStack']['url'], cfg['ChirpStack']['username'],
                             password=cfg['ChirpStack']['password'])
    if not chirp_stack.is_logged:
        print("ChirpStack connection error!")
        quit()

    print('\033[2J\033[0;0H', end='')
    sys.stdout.flush()

    thread = serial.threaded.ReaderThread(ser, DVT19.DVT19)
    thread.start()

    (transport, test_system) = thread.connect()
    uut_test_data = {'sn': args.uut_sn,
                     'join_key': None, 'dev_eui': None,  # security data
                     'fw_ver': None, 'dev_type': None,  # fw, hw versions
                     'fei': None, 'snr': None, 'rssi': None, 'per': None,  # rf line param
                     'vcc': None, 'adc_t': None,  # DVT sensor measurement data
                     'ds18b20_t': None,  # DVT sensor measurement data
                     'vibro_x': None, 'vibro_y': None, 'vibro_z': None,  # DVT sensor measurement data
                     'acc_x': None, 'acc_y': None, 'acc_z': None,  # DVT sensor measurement data
                     'pwr_meas': None  # RF Power Meter measurement data
                     }
    ref_test_data = copy.deepcopy(uut_test_data)
    test_data = {'uut': uut_test_data, 'ref': ref_test_data}

    for sens_role in test_data:
        print(f"Get device info from {sens_role}....", end='')
        start_time = time.time()
        tmp = test_system.get_devinfo(from_uut=(sens_role == 'uut'))
        if tmp is not None:
            test_data[sens_role]['dev_eui'] = tmp.devinfo.dev_eui.hex()
            test_data[sens_role]['fw_ver'] = tmp.devinfo.version
            test_data[sens_role]['dev_type'] = tmp.devinfo.family
            print(f"OK [{int((time.time() - start_time) * 1000)} ms]")
        else:
            print(f"FAIL [{int((time.time() - start_time) * 1000)} ms]")

        print(f"Get ADC data from {sens_role}....", end='')
        start_time = time.time()
        tmp = test_system.get_mcu_adc(from_uut=(sens_role == 'uut'))
        if tmp is not None:
            test_data[sens_role]['vcc'] = tmp.battery_voltage
            test_data[sens_role]['adc_t'] = tmp.mcu_temperature
            print(f"OK [{int((time.time() - start_time) * 1000)} ms]")
        else:
            print(f"FAIL [{int((time.time() - start_time) * 1000)} ms]")

        print(f"Get temperature sensor from {sens_role}....", end='')
        start_time = time.time()
        tmp = test_system.get_temperature(from_uut=(sens_role == 'uut'))
        if tmp is not None:
            test_data[sens_role]['ds18b20_t'] = tmp.temp
            print(f"OK [{int((time.time() - start_time) * 1000)} ms]")
        else:
            print(f"FAIL [{int((time.time() - start_time) * 1000)} ms]")

        print(f"Get accelerometer sensor from {sens_role}....", end='')
        start_time = time.time()
        tmp = test_system.get_adxl345(from_uut=(sens_role == 'uut'))
        if tmp is not None:
            test_data[sens_role]['acc_x'] = tmp.x
            test_data[sens_role]['acc_y'] = tmp.y
            test_data[sens_role]['acc_z'] = tmp.z
            print(f"OK [{int((time.time() - start_time) * 1000)} ms]")
        else:
            print(f"FAIL [{int((time.time() - start_time) * 1000)} ms]")

        print(f"Get vibration data from {sens_role}....", end='')
        start_time = time.time()
        tmp = test_system.get_vibro(from_uut=(sens_role == 'uut'))
        if tmp is not None:
            test_data['uut']['vibro_x'] = tmp.x
            test_data['uut']['vibro_y'] = tmp.y
            test_data['uut']['vibro_z'] = tmp.z
            print(f"OK [{int((time.time() - start_time) * 1000)} ms]")
        else:
            print(f"FAIL [{int((time.time() - start_time) * 1000)} ms]")

        print(f"Get join key from {sens_role.upper()}....", end='')
        start_time = time.time()
        tmp = test_system.get_join_key(from_uut=(sens_role == 'uut'))
        if tmp is not None:
            test_data[sens_role]['join_key'] = tmp.join_key.hex()
            print(f"OK [{int((time.time() - start_time) * 1000)} ms]")
        else:
            print(f"FAIL [{int((time.time() - start_time) * 1000)} ms]")

    print("Get RF line parameters....", end='')
    start_time = time.time()
    tmp = test_system.get_rf_line_param(50)
    if tmp is not None:
        uut_test_data['per'] = tmp['per']
        uut_test_data['fei'] = tmp['fei']
        uut_test_data['snr'] = tmp['snr']
        uut_test_data['rssi'] = tmp['rssi']
        print(f"OK [{int((time.time() - start_time) * 1000)} ms]")
    else:
        print(f"FAIL [{int((time.time() - start_time) * 1000)} ms]")

    if with_power_meas:
        test_system.set_cw_mode(pwr_dbm=4)
        time.sleep(1)
        pwrm_ser.write(b'd')
        time.sleep(0.1)
        a = pwrm_ser.readline()
        uut_test_data['pwr_meas'] = float(str(a.rstrip().lstrip().decode('utf-8')))  # TODO:: need to do error handling

    print('\033[92m', end='')
    print(f"+------------+----------------------------------+----------------------------------+")
    print(f"| {'param':10} | {'UUT device data':32} | {'reference device data':32} |")
    print(f"+------------+----------------------------------+----------------------------------+")
    for i in ref_test_data:
        print(f"| {i:10} | {str(uut_test_data[i]):32} | {str(ref_test_data[i]):32} |")
    print(f"+------------+----------------------------------+----------------------------------+")

    test_data['uut']['sn'] = args.uut_sn
    test_data['ref']['sn'] = cfg['DVT19']['ref_sn']
    db = db.SqLiteDb('rts.sq')
    db.create_tables()
    comment_str = args.comment
    if comment_str == '':
        comment_str = input("Enter DB comment:\n")
    db.put_data_into_db(test_data, comment_str)

    dev_name = str(test_data['uut']['sn'])
    thng_token = things_board.put_device(dev_name, "АГК")

    chirp_stack.reg_dev(test_data['uut']['dev_eui'], dev_name, 'vts_dev', thng_token)
    chirp_stack.create_deice_keys(dev_eui=test_data['uut']['dev_eui'], nwk_key=cfg['ChirpStack']['nwk_key'],
                                  app_key=cfg['ChirpStack']['app_key'], gen_app_key=cfg['ChirpStack']['gen_app_key'])

    thread.close()
    # assert isinstance(ser.close, object)
    ser.close()
    if with_power_meas:
        pwrm_ser.close()
