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

        self.img_temp_data = None

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
        if self.img_temp_data is None:
            data = conn.recv(1024)
            if len(data) == 0:
                return None
        else:
            data = self.img_temp_data
            self.img_temp_data = None
        total_size = int(data.decode())
        conn.send(data)

        recv_size = 0
        recv_data = bytes()
        while recv_size < total_size:
            data = conn.recv(65535)
            recv_size += len(data)
            if recv_size > total_size:
                recv_data += data[:-(recv_size-total_size)]
                self.img_temp_data = data[-(recv_size-total_size):]
            else:
                recv_data += data
                self.img_temp_data = None

        img = decode_img(recv_data)
        return img

    def send_img(self, data, wait : bool = True):
        cnt = 0
        while True:
            if 'img' in self.conn_dict.keys():
                if 'conn' in self.conn_dict['img'].keys():
                    break
            if not wait:
                print('CANNOT send img, ignore this img !')
                return
            cnt += 1
            if cnt % 1000 == 0:
                print('CANNOT send img, try to resend !')
            sleep(0.001)

        conn = self.conn_dict['img']['conn']
        message = Message(data)
        ok, sent_data = message.encode()
        if ok:
            try:
                conn.sendall(str(len(sent_data)).encode())
                recv_data = conn.recv(1024)
                conn.sendall(sent_data)
            except:
                print('Send img failed, ignore this img !')