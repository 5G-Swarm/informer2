# -*- coding: utf-8 -*-
import os
import yaml
from enum import Enum

class SocketStatus(Enum):
    INIT = 1
    UNCONN = 2
    HANDSHAKED = 3
    # RECVING = 4
    # SENDING = 5

def load_yaml(file_path) -> dict:
    with open(file_path, 'r', encoding="utf-8") as file:
        result = yaml.unsafe_load(file)
    return result

def test_connection(ip : str):
    f = os.popen('ping ' + ip + ' -c 1 -W 1')
    files = f.read()
    lines = files.split('\n')
    return lines[1][:8]=='64 bytes'