import requests
import json

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
class ChirpStack:

    def __init__ (self, url, username, password):
        self.__url = url
        self.__header = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        self.__log_req = {"password": password, "username": username}
        self.__jwt_token = ""
        tmp = requests.post(self.__url + '/api/internal/login', json=self.__log_req, headers= self.__header)
        if 200 == tmp.status_code:
            self.__token = json.loads(tmp.content)['jwt']
            self.__header = {'Accept': 'application/json', 'Grpc-Metadata-Authorization': 'Bearer ' + self.__token}
    
    def devEUI_is_registered(self, devEUI):
        resp = requests.get(self.__url + '/api/devices/' + devEUI, data={}, headers=self.__header)
        if resp.status_code == 200:
            return True
        return False
    
    def reg_dev(self, dev_eui, dev_name, things_board_token):
        data = {"device": {
                    "applicationID": "1",
                    "description": "Dev reg by python script",
                    "devEUI": dev_eui,
                    "deviceProfileID": "e8d7b86d-6a18-4001-871c-61ab2e635101",
                    "name": dev_name,
                    "referenceAltitude": 0,
                    "skipFCntCheck": True,
                    "tags": {},
                    "variables": {"ThingsBoardAccessToken": things_board_token }
                    }
                }
        print(data)
    
if __name__ == "__main__":

    rs24 = ChirpStack('http://rs24.tw1.su', 'admin', 'admin')

    result = rs24.devEUI_is_registered("0102030405060709")
    print(result)

    devEUI = "0102030405060709"
    rs24.reg_dev(devEUI, "del_me_second", "vpNJIm0Yhmwf4IqVdCsw")

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
