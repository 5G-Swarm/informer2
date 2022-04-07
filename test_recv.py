import cv2
from time import sleep
import numpy as np

from informer import Informer

def parse_img(message):
    print("Get img size:",len(message))
    nparr = np.frombuffer(message, np.uint8)
    img = cv2.imdecode(nparr,  cv2.IMREAD_COLOR)
    cv2.imshow('Image',img)
    cv2.waitKey(1)

class Server(Informer):
    def img_recv(self):
        self.recv('img', parse_img)

ifm = Server(
    config = 'config_recv.yaml',
    )
    
while True:
    sleep(1)