# -*- coding: utf-8 -*-
from typing import Tuple
import cv2
import numpy as np

def encode_img(img):
    pass

def encode_img(img, isGrey=False) -> bytes:
    if isGrey:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_AREA)
    ret, jpeg=cv2.imencode('.jpg', img)
    data = jpeg.tobytes()
    return data

def decode_img(data):
    nparr = np.fromstring(data, np.uint8)
    img = cv2.imdecode(nparr,  cv2.IMREAD_COLOR)
    # img = cv2.imdecode(data)
    return img

class Message():
    def __init__(self, data):
        self.__data = data

    def encode(self) -> Tuple[bool , bytes]:
        res = bytes()
        ok = False
        if isinstance(self.__data, str):
            res = self.__data.encode()
            ok = True
        elif isinstance(self.__data, bytes):
            res = self.__data
            ok = True
        elif isinstance(self.__data, dict):
            pass
        elif isinstance(self.__data, np.ndarray):
            if self.__data.dtype == np.dtype('uint8'):
                res = encode_img(self.__data)
                ok = True
            else:
                print('Unknown encoding numpy type:', self.__data.dtype)
        else:
            print('Unknown encoding type:', type(self.__data))
        return ok, res
    