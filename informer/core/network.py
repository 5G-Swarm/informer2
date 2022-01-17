# -*- coding: utf-8 -*-
import socket

def creat_tcp_scoket(ip : str, port : int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    return sock

def creat_udp_scoket(ip : str = None, port = None):
    sock =  socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    return sock

def handshake():
    pass