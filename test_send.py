from time import sleep
from informer import Informer
from proto.python_out import cmd_msgs_pb2
import cv2


def execute_cmd(cmd):
    print(cmd.v, cmd.w)

def parse_cmd(message):
    cmd = cmd_msgs_pb2.Cmd()
    cmd.ParseFromString(message)
    execute_cmd(cmd)

class Client(Informer):
    def send_img(self, message):
        self.send(message, 'img')

    def cmd_recv(self):
        self.recv('cmd', parse_cmd)

ifm = Client(
    config = 'config.yaml',
    )

def callback_img(img):
    # img = cv2.resize(img, (320*4, 4*240))
    ret, jpeg = cv2.imencode('.jpg', img)
    data = jpeg.tobytes()
    ifm.send_img(data)
    # print('send !')

video_reader = cv2.VideoCapture('video.mp4')
img = cv2.imread('img.jpg')

success, img = video_reader.read()
while success:
    callback_img(img)
    success, img = video_reader.read()

video_reader.release()