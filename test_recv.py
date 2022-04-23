import cv2
from time import sleep
import numpy as np

from informer import Informer
from proto.python_out import cmd_msgs_pb2

global_img = None
def parse_img(message):
    global global_img
    # print("Get img size:",len(message))
    nparr = np.frombuffer(message, np.uint8)
    global_img = cv2.imdecode(nparr,  cv2.IMREAD_COLOR)

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
    
for cnt in range(9999999):
    if cnt % 20 == 0:
        cmd = get_cmd()
        ifm.send_cmd(cmd)
        # for key in ifm.conn_dict.keys():
        #     print(key, ifm.conn_dict[key]['status'])
        # print(ifm.working_dict.keys(), ifm.starting_dict.keys())

    if global_img is not None:
        cv2.imshow('Image',global_img)
        cv2.waitKey(1)

    sleep(0.01)