import json
from google.protobuf import json_format
from rs_0006_0_icp_pb2 import *

json_srt = '''{
  "resp": {
    "devinfo": {
      "devEui": "BQD6/xTy6w0=",
      "family": "RS.0006-0",
      "version": 2
    },
    "respId": 123456789,
    "fei": -32917,
    "snr": 5,
    "rssi": -48
  }
}'''

# print(json_srt)
aa = json_format.Parse(json_srt, exch())
print(aa.resp.devinfo.dev_eui.hex())
print(type(aa.resp.devinfo.version))
# print(bytes([aa.resp.devinfo.version]).hex())
bb = (aa.resp.devinfo.version).to_bytes(4, byteorder="big").hex()
print(len(bb))
print(bb[:4] + "." + bb[4:])