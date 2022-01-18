import cv2
from time import sleep
from informer import Informer



ifm = Informer(
    config = 'config_recv.yaml',
    )
    
for _ in range(100):
    img = ifm.recv_img()
    cv2.imshow('URL2Image',img)
    cv2.waitKey(5)