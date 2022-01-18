# -*- coding: utf-8 -*-
from typing import Tuple
from time import sleep

from .utils import load_yaml
from .core import creat_sockets, ConnDict, Message, decode_img
class Informer():
    def __init__(self, config):
        self.config = load_yaml(config)
        self.mode = self.config.get('comm_mode')
        self.target_ip, self.target_port = self.get_target_info(self.config)

        """
        key: message type
        value: tcp/udp socket
        """
        self.conn_dict = ConnDict()

        self.message_keys = self.get_message_keys(self.config)
        creat_sockets(self.message_keys, self.config)

    def get_target_info(self, config : dict) -> Tuple[str , int]:
        target_ip = config.get('network_info').get('target_info').get('ip')
        target_port = config.get('network_info').get('target_info').get('port')
        return target_ip, target_port

    def get_message_keys(self, config : dict) -> list:
        return list(config.get('message_info').keys())

    def send(self, key : str, data):
        while True:
            if key in self.conn_dict.keys():
                if 'conn' in self.conn_dict[key].keys():
                    break
            sleep(0.001)

        conn = self.conn_dict[key]['conn']
        message = Message(data)
        ok, sent_data = message.encode()
        if ok: conn.send(sent_data)

    def test_send(self, data : str):
        while True:
            if 'img' in self.conn_dict.keys():
                if 'conn' in self.conn_dict['img'].keys():
                    break
            sleep(0.001)

        conn = self.conn_dict['img']['conn']
        conn.send(data.encode())

    def recv(self, key):
        while True:
            if key in self.conn_dict.keys():
                if 'conn' in self.conn_dict[key].keys():
                    break
            sleep(0.001)
            
        conn = self.conn_dict[key]['conn']
        data = conn.recv(65535)
        return data

    def test_recv(self):
        while True:
            if 'img' in self.conn_dict.keys():
                if 'conn' in self.conn_dict['img'].keys():
                    break
            sleep(0.001)
            
        conn = self.conn_dict['img']['conn']
        data = conn.recv(65535)
        return data

    def recv_img(self):
        while True:
            if 'img' in self.conn_dict.keys():
                if 'conn' in self.conn_dict['img'].keys():
                    break
            sleep(0.001)
            
        conn = self.conn_dict['img']['conn']
        data = conn.recv(65535)
        total_size = int(data.decode())
        conn.send(data)

        recv_size = 0
        recv_data = bytes()
        while recv_size < total_size:
            data = conn.recv(65535)
            recv_data += data
            recv_size += len(data)

        img = decode_img(recv_data)
        return img

    def send_img(self, data):
        while True:
            if 'img' in self.conn_dict.keys():
                if 'conn' in self.conn_dict['img'].keys():
                    break
            sleep(0.001)

        conn = self.conn_dict['img']['conn']
        message = Message(data)
        ok, sent_data = message.encode()
        if ok:
            conn.send(str(len(sent_data)).encode())
            recv_data = conn.recv(1024)
            conn.send(sent_data)