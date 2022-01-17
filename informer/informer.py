# -*- coding: utf-8 -*-
from .utils import load_yaml
from .core import handshake, creat_tcp_scoket, creat_udp_scoket
class Informer():
    def __init__(self, config):
        self.config = load_yaml(config)
        self.mode = self.config.get('comm_mode')
        self.target_ip, self.target_port = self.get_target_info(self.config)

        """
        key: message type
        value: tcp/udp socket
        """
        self.conn_dict = {}

        self.message_keys = self.get_message_keys(self.config)
        self.conn_dict = self.creat_sockets(self.message_keys, self.config)

    def get_target_info(self, config : dict):
        target_ip = config.get('network_info').get('target_info').get('ip')
        target_port = config.get('network_info').get('target_info').get('port')
        return target_ip, target_port

    def get_message_keys(self, config : dict) -> list:
        return list(config.get('message_info').keys())

    def creat_sockets(self, keys : str, config : dict) -> dict:
        conn_dict = {}
        for key in keys:
            message_port = config.get('message_info').get()
            conn_dict[key] = creat_tcp_scoket(self.target_ip, message_port)
        return conn_dict