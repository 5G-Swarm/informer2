# -*- coding: utf-8 -*-
from typing import Tuple
import cv2
import numpy as np
import json

def encode_img(img, isGrey=False) -> bytes:
    if isGrey:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_AREA)
    ret, jpeg=cv2.imencode('.jpg', img)
    data = jpeg.tobytes()
    return data

def decode_img(data : bytes) -> np.ndarray:
    nparr = np.fromstring(data, np.uint8)
    img = cv2.imdecode(nparr,  cv2.IMREAD_COLOR)
    return img

def encode_dict(data : dict) -> bytes:
    data = json.dumps(data).encode()
    return data

def decode_dict(data : bytes) -> dict:
    return json.loads(data)
class Message():
    def __init__(self, data):
        self.__data = data

    def encode(self) -> Tuple[bool , bytes]:
        res = bytes()
        ok = False

        if isinstance(self.__data, list) or isinstance(self.__data, tuple):
            self.__data = np.array(self.__data).astype(np.float32)

        if isinstance(self.__data, str):
            res = self.__data.encode()
            ok = True
        elif isinstance(self.__data, bytes):
            res = self.__data
            ok = True
        elif isinstance(self.__data, dict):
            res = encode_dict(self.__data)
            ok = True
        elif isinstance(self.__data, np.ndarray):
            if self.__data.dtype == np.dtype('uint8'):
                res = encode_img(self.__data)
                ok = True
            else:
                res = self.__data.tobytes()
                ok = True
        else:
            print('Unknown encoding type:', type(self.__data))
        return ok, res

    """
    TODO
    """
    def decode(self, data_type):
        res = None
        ok = False
        if data_type == 'str':
            res = self.__data.decode()
            ok = True
        elif data_type == 'bytes':
            res = self.__data
            ok = True
        elif data_type == 'dict':
            res = decode_dict(self.__data)
            ok = True
        elif data_type == 'img':
                res = decode_img(self.__data)
                ok = True
        elif data_type == 'array':
            res = np.frombuffer(self.__data, np.float32)
            ok = True
        else:
            print('Unknown encoding type:', type(self.__data))
        return ok, res
    