# -*- coding: utf-8 -*-
from typing import Tuple, Callable
import threading
import time
from .utils import load_yaml
from .core import creat_sockets, ConnDict
class Informer():
    def __init__(self, config):
        self.HEAD_LENGTH = 8
        self.config = load_yaml(config)
        self.is_client = self.config.get('role_info').get('is_client')
        self.target_ip = self.get_target_info(self.config)
        
        """
        key: message type
        value: tcp/udp socket
        """
        self.conn_dict = ConnDict()

        self.trd_list = []

        self.message_keys = self.get_message_keys(self.config)
        creat_sockets(self.message_keys, self.config)

        self.wait_connection()

        # start receive threads
        for key in self.message_keys:
            try:
                receive_func = getattr(self.__class__, key+'_recv')
            except AttributeError:
                print(self.__class__.__name__, 'has no attribute called', key+'_recv')
                continue
            recv_thread = threading.Thread(
                target = receive_func, args=(self,)
            )
            recv_thread.start()
            self.trd_list.append(recv_thread)

    def wait_connection(self):
        cnt = 0
        while self.message_keys != list(self.conn_dict.keys()):
            cnt += 1
            unconn_keys = set(self.message_keys) - set(self.conn_dict.keys())
            if cnt % 1000 == 0:
                for key in unconn_keys:
                    print(key, 'is not connected !')
            time.sleep(0.001)


    def get_target_info(self, config : dict) -> str:
        target_ip = config.get('network_info').get('target_info').get('ip')
        return target_ip

    def get_message_keys(self, config : dict) -> list:
        return list(config.get('message_info').keys())

    def send(self, data, key : str):
        # print("data len:", len(data))
        data_len = len(data).to_bytes(self.HEAD_LENGTH, 'big')
        data = data_len + data

        conn = self.conn_dict[key]['conn']
        try:
            conn.sendall(data)
        except BrokenPipeError:
            print('Send error ! Connection broken !')

    def recv(self, key : str, func : Callable):
        # print('start to recv ...')
        send_data = bytes()
        data_cache = bytes()
        data_length = 0

        while True:
            conn = self.conn_dict[key]['conn']
            data = conn.recv(65535)
            if len(data) == 0: continue
            send_data += data

            if len(data_cache):
                send_data = data_cache + send_data
                data_cache = bytes()

            while len(send_data):
                if not data_length:
                    if len(send_data) < self.HEAD_LENGTH:
                        data_cache += send_data
                        send_data = bytes()
                    else:
                        data_length = int.from_bytes(send_data[:self.HEAD_LENGTH], 'big')
                        send_data = send_data[self.HEAD_LENGTH:]
                        
                elif len(send_data) < data_length:
                    data_cache += send_data
                    send_data = bytes()
                else:
                    func(send_data[:data_length])
                    send_data = send_data[data_length:]
                    data_length = 0

    def close(self):
        self._cls_trd = True
        for i in self.trd_list:
            del i
        for i in self.message_socket:
            i.close()