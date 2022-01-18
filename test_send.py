from time import sleep
from informer import Informer

import cv2



ifm = Informer(
    config = 'config.yaml',
    )
    

img = cv2.imread('img.jpg')

for _ in range(100):
    ifm.send_img(img)
    sleep(1)