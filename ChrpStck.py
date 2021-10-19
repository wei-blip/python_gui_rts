from builtins import print

import requests
import json


class ChirpStack:

    def __init__(self, url, username, password):
        self.__url = url
        self.__header = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        self.__log_req = {"password": password, "email": username}
        self.__jwt_token = ""
        self.is_logged = False
        tmp = requests.post(self.__url + '/api/internal/login', json=self.__log_req, headers=self.__header)
        if 200 == tmp.status_code:
            self.__token = json.loads(tmp.content)['jwt']
            self.__header = {'Accept': 'application/json', 'Grpc-Metadata-Authorization': 'Bearer ' + self.__token}
            self.is_logged = True

    def dev_eui_is_registered(self, dev_eui):
        ret = False
        resp = requests.get(f'{self.__url}/api/devices/{dev_eui}', data={}, headers=self.__header)
        if resp.status_code == 200:
            ret = True
        return ret

    def reg_dev(self, dev_eui, dev_name, dev_profile_name, things_board_token):
        data = {"device": {
            "applicationID": "1",
            "description": "Dev reg by python script",
            "devEUI": dev_eui,
            "deviceProfileID": self.get_device_profile_id(dev_profile_name),
            "name": dev_name,
            "referenceAltitude": 0,
            "skipFCntCheck": True,
            "tags": {},
            "variables": {"ThingsBoardAccessToken": things_board_token}
        }
        }
        post = requests.post(f'{self.__url}/api/devices', json=data, headers=self.__header)
        return 200 == post.status_code

    def get_device_profile_id(self, profile_name: str) -> str:
        resp = requests.get(self.__url + f'/api/device-profiles', headers=self.__header)
        ans = ''
        if resp.status_code == 200:
            total_count = json.loads(resp.content)['totalCount']
            resp = requests.get(self.__url + f'/api/device-profiles?limit={total_count}&offset={0}',
                                headers=self.__header)
            if resp.status_code == 200:
                total_count = json.loads(resp.content)['totalCount']
                result = json.loads(resp.content)['result']
                for i in range(int(total_count)):
                    if result[i]['name'] == profile_name:
                        ans = result[i]['id']
        return ans

    def get_device_info(self, dev_eui: str):
        resp = requests.get(f'{self.__url}/api/devices/{dev_eui}', headers=self.__header)
        ans = ''
        if resp.status_code == 200:
            ans = json.loads(resp.content)
        return ans

    def get_devices(self, limit=100):
        resp = requests.get(f'{self.__url}/api/devices?limit={int(limit)}', headers=self.__header)
        ans = ''
        if resp.status_code == 200:
            ans = json.loads(resp.content)
        return ans

    def create_deice_keys(self, dev_eui: str, nwk_key: str, app_key: str, gen_app_key: str):
        data = {"deviceKeys": {
            "devEUI": dev_eui,
            "nwkKey": nwk_key,
            "appKey": app_key,
            "genAppKey": gen_app_key,
        }
        }
        post = requests.post(self.__url + f'/api/devices/{dev_eui}/keys', json=data, headers=self.__header)
        return 200 == post.status_code

# GetKeys returns the device-keys for the given DevEUI
# curl -X GET --header 'Accept: application/json' --header 'Grpc-Metadata-Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhcyIsImV4cCI6MTYyOTA0MDEzMCwiaWQiOjEsImlzcyI6ImFzIiwibmJmIjoxNjI4OTUzNzMwLCJzdWIiOiJ1c2VyIiwidXNlcm5hbWUiOiJhZG1pbiJ9.NcHOzYpDzF5KAJuMuNjVwSqlw5igB4dQCiVMRn6a0ls' 'https://cs.rts-iot.ru/api/devices/0b50523456508f34/keys'
# {
#   "deviceKeys": {
#     "devEUI": "0b50523456508f34",
#     "nwkKey": "2b7e151628aed2a6abf7158809cf4f3c",
#     "appKey": "00000000000000000000000000000000",
#     "genAppKey": "00000000000000000000000000000000"
#   }
# }

# UpdateKeys updates the device-keys.
# curl -X PUT --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'Grpc-Metadata-Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhcyIsImV4cCI6MTYyOTA0MDEzMCwiaWQiOjEsImlzcyI6ImFzIiwibmJmIjoxNjI4OTUzNzMwLCJzdWIiOiJ1c2VyIiwidXNlcm5hbWUiOiJhZG1pbiJ9.NcHOzYpDzF5KAJuMuNjVwSqlw5igB4dQCiVMRn6a0ls' -d '{ \
#    "deviceKeys": { \
#      "devEUI": "0b50523456508f34", \
#      "nwkKey": "2b7e151628aed2a6abf7158809cf4f3c", \
#      "appKey": "00000000000000000000000000000000", \
#      "genAppKey": "00000000000000000000000000000000" \
#    } \
#  }' 'https://cs.rts-iot.ru/api/devices/0b50523456508f34/keys'

# curl -X GET --header 'Accept: application/json' --header 'Grpc-Metadata-Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhcyIsImV4cCI6MTYyODI2MzM4NCwiaWQiOjEsImlzcyI6ImFzIiwibmJmIjoxNjI4MTc2OTg0LCJzdWIiOiJ1c2VyIiwidXNlcm5hbWUiOiJhZG1pbiJ9.rXpJUOKafmEPdO6kN0XljG2F8Vw70YAsyC3XSPzstOk' 'https://cs.rts-iot.ru/api/devices/1050524d1d506c4d'


if __name__ == "__main__":

    rs24 = ChirpStack('https://cs.rts-iot.ru', 'admin', r'ztujj,zpfntkmyjdcgjvy.')
    res = rs24.get_device_profile_id('vts_dev')
    print(res)
    # aa = rs24.get_devices()
    # for i in range(int(aa['totalCount'])):
    #     if 'ThingsBoardAccessToken' in rs24.get_device_info(aa['result'][i]['devEUI'])['device']['variables']:
    #         print(aa['result'][i]['name'],
    #               rs24.get_device_info(aa['result'][i]['devEUI'])['device']['variables']['ThingsBoardAccessToken'])
    #     else:
    #         print(aa['result'][i]['name'])

    a = rs24.create_deice_keys(dev_eui='0102030405060708',
                           nwk_key='2b7e151628aed2a6abf7158809cf4f3c',
                           app_key='00000000000000000000000000000000',
                           gen_app_key='00000000000000000000000000000000')
    print(a)

    # devEUI = "1050524d1d50704d"
    # result = rs24.dev_eui_is_registered(devEUI)
    # print(result)
    # rs24.reg_dev(devEUI, "del_me_second", "vpNJIm0Yhmwf4IqVdCsw")
# {'device': {'applicationID': '1', 'description': 'Dev reg by python script', 'devEUI': '1050524d1d50704d', 'deviceProfileID': 'e8d7b86d-6a18-4001-871c-61ab2e635101', 'name': '06.xxxx.0001', 'referenceAltitude': 0, 'skipFCntCheck': True, 'tags': {}, 'variables': {'ThingsBoardAccessToken': 'UhP1hMR4qbyuUw60DicG'}}}

# url = 'http://rs24.tw1.su/api/device-profiles/e8d7b86d-6a18-4001-871c-61ab2e635101'
# resp_header = {'Accept': 'application/json', 'Grpc-Metadata-Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJjaGlycHN0YWNrLWFwcGxpY2F0aW9uLXNlcnZlciIsImV4cCI6MTU5ODQ1NTg2NCwiaXNzIjoiY2hpcnBzdGFjay1hcHBsaWNhdGlvbi1zZXJ2ZXIiLCJuYmYiOjE1OTgzNjk0NjQsInN1YiI6InVzZXIiLCJ1c2VybmFtZSI6ImFkbWluIn0.Y0WQkEMeA5V-za0bmjA-T9JE39FcseBwMsvof50SmmE'}
# resp = requests.get(url, params={}, headers=resp_header)
# # if 200 == resp.status_code:
# #     print(resp.content)

# resp_header = {'Accept': 'application/json', 'Grpc-Metadata-Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJjaGlycHN0YWNrLWFwcGxpY2F0aW9uLXNlcnZlciIsImV4cCI6MTU5ODQ1NTg2NCwiaXNzIjoiY2hpcnBzdGFjay1hcHBsaWNhdGlvbi1zZXJ2ZXIiLCJuYmYiOjE1OTgzNjk0NjQsInN1YiI6InVzZXIiLCJ1c2VybmFtZSI6ImFkbWluIn0.Y0WQkEMeA5V-za0bmjA-T9JE39FcseBwMsvof50SmmE'}
# url = 'http://rs24.tw1.su/api/devices'

# devEUI = "0102030405060709"
# data = {
#   "device": {
#     "applicationID": "1",
#     "description": "Dev reg by python script",
#     "devEUI": devEUI,
#     "deviceProfileID": "e8d7b86d-6a18-4001-871c-61ab2e635101",
#     "name": "del_me_second",
#     "referenceAltitude": 0,
#     "skipFCntCheck": True,
#     "tags": {},
#     "variables": {"ThingsBoardAccessToken": "vpNJIm0Yhmwf4IqVdCsw"}
#   }
# }
# # aaa = json.dumps(data)
# post = requests.post(url, json=data, headers=resp_header)
# print(post.content)
# # # print(aaa)

# curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'Grpc-Metadata-Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJjaGlycHN0YWNrLWFwcGxpY2F0aW9uLXNlcnZlciIsImV4cCI6MTU5ODQ1NTg2NCwiaXNzIjoiY2hpcnBzdGFjay1hcHBsaWNhdGlvbi1zZXJ2ZXIiLCJuYmYiOjE1OTgzNjk0NjQsInN1YiI6InVzZXIiLCJ1c2VybmFtZSI6ImFkbWluIn0.Y0WQkEMeA5V-za0bmjA-T9JE39FcseBwMsvof50SmmE' -d '{ \ 
#    "deviceKeys": { \ 
#      "devEUI": "0102030405060709", \ 
#      "nwkKey": "01020304050607080910111213141516" \ 
#    } \ 
#  }' 'http://rs24.tw1.su/api/devices/0102030405060709/keys'


# import names

# for _ in range(0,10):
#     print(names.get_first_name(gender='male'))

# import grpc
# import os
# import sys
# from chirpstack_api.as_pb.external import api

# if __name__ == '__main__':
#   # Create the client for the "internal" service
#   channel = grpc.insecure_channel('rs24.tw1.su:80')
#   stub = api.InternalServiceStub(channel)

#   # Create and build the login request message
#   loginRequest = api.LoginRequest()
#   loginRequest.password = 'admin'
#   loginRequest.email = 'admin'

#   # Send the login request
#   token = stub.Login(loginRequest)

#   # Build the metadata list, settting the authorization from the JWT
#   # obtained from loggin in.
#   metadata= [('authorization', token.jwt)]
#   print(metadata)

# This metadata can now be passed for requests to APIs that require
# authorization
