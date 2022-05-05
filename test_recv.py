import cv2
from time import sleep
import numpy as np

from informer import Informer
from proto.python_out import cmd_msgs_pb2

global_img_dict = {}
def parse_img(message, robot_id):
    global global_img_dict
    print("Get img size:",len(message), 'from id', robot_id)
    nparr = np.frombuffer(message, np.uint8)
    global_img_dict[robot_id] = cv2.imdecode(nparr,  cv2.IMREAD_COLOR)

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

ifm_list = [
    Server(
    config = 'config_recv.yaml',
    robot_id = item
    )
    for item in range(20)
]
# ifm = Server(
#     config = 'config_recv.yaml',
#     robot_id = 16
#     )
    
for cnt in range(9999999):
    if cnt % 20 == 0:
        cmd = get_cmd()
        ifm_list[5].send_cmd(cmd)
        # for key in ifm.conn_dict.keys():
        #     print(key, ifm.conn_dict[key]['status'])
        # print(ifm.working_dict.keys(), ifm.starting_dict.keys())
    for key in global_img_dict.keys():
        cv2.imshow('Image_'+str(key), global_img_dict[key])
    cv2.waitKey(5)
    # if global_img is not None:
    #     cv2.imshow('Image',global_img)
    #     cv2.waitKey(1)

    sleep(0.01)