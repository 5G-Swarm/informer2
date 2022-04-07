from time import sleep
from informer import Informer

import cv2

class Client(Informer):
    def send_img(self, message):
        self.send(message, 'img')

ifm = Client(
    config = 'config.yaml',
    )

def callback_img(img):
    # img = cv2.resize(img, (320*4, 4*240))
    ret, jpeg = cv2.imencode('.jpg', img)
    data = jpeg.tobytes()
    ifm.send_img(data)
    print('send !')

video_reader = cv2.VideoCapture('video.mp4')
img = cv2.imread('img.jpg')

success, img = video_reader.read()
while success:
    callback_img(img)
    success, img = video_reader.read()

video_reader.release()