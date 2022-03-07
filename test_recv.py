import cv2
from time import sleep
from informer import Informer



ifm = Informer(
    config = 'config_recv.yaml',
    )
    
while True:
    img = ifm.recv_img()
    if img is None:
        continue
    cv2.imshow('Image',img)
    cv2.waitKey(5)