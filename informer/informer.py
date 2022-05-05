# -*- coding: utf-8 -*-
import os
import sys
from typing import Callable
import threading
import time
from .utils import load_yaml, SocketStatus, test_connection
from .core import creat_sockets
import logging

class Informer():
    def __init__(self, config, robot_id = None):
        self.HEAD_LENGTH = 8
        self.config = load_yaml(config)
        if robot_id is not None:
            self.config['robot_id'] = robot_id
            self.robot_id = robot_id
        else:
            self.robot_id = self.config['robot_id']
        self.debug_mode = self.config.get('debug_mode')
        self.use_log = self.config.get('use_log')
        self.is_client = self.config.get('role_info').get('is_client')
        self.target_ip = self.get_target_info(self.config)
        self.message_keys = self.get_message_keys(self.config)

        self.conn_dict = {}
        self.trd_list = {}
        self.working_dict = {}
        self.starting_dict = {}

        if self.use_log:
            os.makedirs('logs', exist_ok=True)
            logging.basicConfig(filename='logs/log_'+sys.argv[0]+'.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            logging.getLogger('').addHandler(console)

            logging.info('Connecting to IP: ' + self.target_ip)
            res = test_connection(self.target_ip)
            if res:
                logging.info('\033[32mConnection success !\033[0m')
            else:
                logging.error('\033[31mConnection fail !\033[0m')

        self.heartbeat_trd = threading.Thread(
            target = self.heartbeat_func, args=()
        )
        self.heartbeat_trd.start()

    def start_func(self, key : str):
        creat_sockets([key], self.config, self.conn_dict, self.working_dict)
        # this will not block the main thread
        self.wait_connection([key])
        del self.starting_dict[key]
        try:
            receive_func = getattr(self.__class__, key+'_recv')
        except AttributeError:
            # logging.info(str(self.__class__.__name__)+ ' has no attribute called '+ key +'_recv')
            return
        recv_thread = threading.Thread(
            target = receive_func, args=(self,)
        )
        recv_thread.start()
        self.trd_list[key] = recv_thread

    def start_key(self, key : str):
        start_thread = threading.Thread(
            target = self.start_func, args=(key,)
        )
        start_thread.start()

    def heartbeat_func(self):
        cnt = 0
        while True:
            for key in self.message_keys:
                if key not in self.working_dict.keys():
                    if key in self.starting_dict.keys(): continue
                    self.starting_dict[key] = True
                    self.start_key(key)
            time.sleep(0.001)
            cnt += 1
            if cnt > 3001:
                cnt = 0
                if True:#self.debug_mode:
                    self.report_status()

    def report_status(self):
        if self.use_log:
            logging.info('')
            logging.info('\033[36mConnection Status:\033[0m')
            for key in self.conn_dict.keys():
                logging.info('\033[33m' + key + ' : ' + str(self.conn_dict[key]['status']) + '\033[0m')
            logging.info('\033[32mWorking keys: ' + str(list(self.working_dict.keys())) + '\033[0m')
            logging.info('\033[31mStarting keys: ' + str(list(self.starting_dict.keys())) + '\033[0m')

    def wait_connection(self, keys):
        cnt = 0
        while set(keys) - set(self.working_dict.keys()) != set():
            cnt += 1
            unconn_keys = set(self.message_keys) - set(self.conn_dict.keys())
            if cnt % 2000 == 0:
                for key in unconn_keys:
                    if self.use_log: logging.info(key + ' is not connected !')
            time.sleep(0.001)

    def get_target_info(self, config : dict) -> str:
        target_ip = config.get('network_info').get('target_info').get('ip')
        return target_ip

    def get_message_keys(self, config : dict) -> list:
        return list(config.get('message_info').keys())

    def send(self, data, key : str):
        data_len = len(data).to_bytes(self.HEAD_LENGTH, 'big')
        data = data_len + data

        try:
            conn = self.conn_dict[key]['conn']
            conn.sendall(data)
            if self.debug_mode:
                if self.use_log: logging.info('[c] Key '+ key +' send data len:' + str(len(data)))
        except:
            # logging.info('Send '+ key + ' error ! Connection broken !')
            # heartbeat thread is not ready, but send first
            if key not in self.conn_dict.keys():
                self.conn_dict[key] = {}
            self.conn_dict[key]['status'] = SocketStatus.UNCONN
            self.conn_dict[key]['conn'] = None
            self.conn_dict[key]['addr'] = None
            try:
                del self.working_dict[key]
                del self.trd_list[key]
            except:
                pass

    def recv(self, key : str, func : Callable):
        if self.debug_mode: 
            if self.use_log: logging.info('[a] Start to recv key: ' + key + ' ...')
        send_data = bytes()
        data_cache = bytes()
        data_length = 0

        while True:
            conn = self.conn_dict[key]['conn']
            data = conn.recv(65535)
            if self.debug_mode and len(data) > 0:
                if self.use_log: logging.info('[b] Key '+ key + ' recv data len: '+ str(len(data)))
            if len(data) == 0:
                break
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
                    if self.debug_mode:
                        if self.use_log: logging.info('[d] Key: '+ key + ' recv over, go to function: parse_'+key)
                    func(send_data[:data_length], self.robot_id)
                    send_data = send_data[data_length:]
                    data_length = 0

        self.conn_dict[key]['status'] = SocketStatus.UNCONN
        self.conn_dict[key]['conn'] = None
        self.conn_dict[key]['addr'] = None
        del self.working_dict[key]