from time import sleep
from informer import Informer

import cv2

ifm = Informer(
    config = 'config.yaml',
    )

video_reader = cv2.VideoCapture('video.mp4')
img = cv2.imread('img.jpg')

success, img = video_reader.read()
while success:
    # img = cv2.resize(img, (640, 480), interpolation = cv2.INTER_AREA)
    ifm.send_img(img)
    # sleep(1/30)
    success, img = video_reader.read()

video_reader.release()