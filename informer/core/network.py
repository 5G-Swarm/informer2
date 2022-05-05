# -*- coding: utf-8 -*-
import socket
import threading
import random
from typing import Tuple
from ..utils import SocketStatus

def __creat_tcp_scoket() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock

def __creat_udp_scoket() -> socket.socket:
    sock =  socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    return sock

def creat_sockets(keys : str, config : dict, conn_dict : dict, working_dict : dict):
    for key in keys:
        """
        Not blocking the main process
        """
        recv_thread = threading.Thread(
                target = __creat_socket_thread,
                args = (key, config, conn_dict, working_dict)
                )
        recv_thread.start()

def  __creat_socket_thread(key : str, config : dict, conn_dict : dict, working_dict : dict):
    sock = __creat_tcp_scoket()
    is_tcp = config.get('message_info').get(key).get('is_tcp')
    is_client = config.get('role_info').get('is_client')

    target_ip = config.get('network_info').get('target_info').get('ip')
    target_port = config.get('message_info').get(key).get('port') + config.get('robot_id')
    # print('target_port', target_port, config.get('robot_id'))

    conn_dict[key] = {}
    # conn_dict[key]['conn'] = None
    conn_dict[key]['addr'] = None
    conn_dict[key]['status'] = SocketStatus.UNCONN

    conn, addr = __handshake(sock, is_tcp, is_client, target_ip, target_port)

    conn_dict[key]['conn'] = conn
    conn_dict[key]['addr'] = addr
    conn_dict[key]['status'] = SocketStatus.HANDSHAKED
    working_dict[key] = True

def __handshake(sock : socket.socket, is_tcp : bool, is_client : bool, target_ip : str, target_port : int):
    if is_tcp and is_client:
        conn, addr = __tcp_client_handshake(sock, target_ip, target_port)
    if is_tcp and not is_client:
        conn, addr = __tcp_server_handshake(sock, target_port)
    if not is_tcp and is_client:
        print('Error config')
    if not is_tcp and not is_client:
        print('Error config')
    
    return conn, addr
    

def __tcp_client_handshake(sock : socket.socket, target_ip : str, target_port : int):
    while True:
        try:
            sock.connect((target_ip, target_port))
            break
        except:
            continue
    return sock, (target_ip, target_port)

def __tcp_server_handshake(sock : socket.socket, target_port : int):
    try:
        sock.bind(('0.0.0.0', target_port))
    except:
        new_target_port = random.randint(10000,65536)
        print('Port', target_port, 'already in use! Try to use port', new_target_port)
        sock.bind(('0.0.0.0', new_target_port))

    sock.listen(5)
    conn, addr = sock.accept()
    return conn, addr