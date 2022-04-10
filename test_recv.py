import cv2
from time import sleep
import numpy as np

from informer import Informer
from proto.python_out import cmd_msgs_pb2

def parse_img(message):
    # print("Get img size:",len(message))
    nparr = np.frombuffer(message, np.uint8)
    img = cv2.imdecode(nparr,  cv2.IMREAD_COLOR)
    cv2.imshow('Image',img)
    cv2.waitKey(1)

class Server(Informer):
    def img_recv(self):
        self.recv('img', parse_img)

    def send_cmd(self, message):
        self.send(message, 'cmd')

def get_cmd():
    cmd = cmd_msgs_pb2.Cmd()
    cmd.v = 1.0
    cmd.w = 1.0
    sent_data = cmd.SerializeToString()
    return sent_data


ifm = Server(
    config = 'config_recv.yaml',
    )
    
while True:
    cmd = get_cmd()
    ifm.send_cmd(cmd)
    sleep(1)