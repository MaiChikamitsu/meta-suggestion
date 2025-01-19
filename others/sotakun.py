from google.protobuf.json_format import MessageToDict
import json
import socket
import time


IP = "192.168.1.77"
PORT = 9980


serv_address = (IP, PORT)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


default_posture = {
   "Waist_Y": 0,
   "RShoulder_P": -900,
   "RElbow_P": 0,
   "LShoulder_P": 900,
   "LElbow_P": 0,
   "Head_Y": 0,
   "Head_P": 0,
   "Head_R": 0
}


pos = default_posture.copy()
message = json.dumps(pos)
sock.sendto(message.encode("utf-8"), serv_address)
print("XXX:motion 1")


motion_sequence = [
      {"Waist_Y": 0, "RShoulder_P": 900, "RElbow_P": 0, "LShoulder_P": 900, "LElbow_P": 0, "Head_Y": 0, "Head_P": 0, "Head_R": 900},  
      {"Waist_Y": 0, "RShoulder_P": 900, "RElbow_P": 0, "LShoulder_P": -900, "LElbow_P": 0, "Head_Y": 0, "Head_P": 0, "Head_R": 900},
    ]
    # 一連の動作をサーバーに送信
for position in motion_sequence:
   pos = default_posture.copy()  # 初期姿勢をコピー
   pos.update(position)          # 動作の位置を更新
   message = json.dumps(pos)     # JSONに変換
   sock.sendto(message.encode("utf-8"), serv_address)  # サーバーに送信

print("XXX:motion 2")

pos = default_posture.copy()
message = json.dumps(pos)
sock.sendto(message.encode("utf-8"), serv_address)
print("XXX:motion 3")
