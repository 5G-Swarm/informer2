#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep
from informer import Informer
from proto.python_out import cmd_msgs_pb2
import cv2
import numpy as np

import rospy
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import Image

V_AMP = 3.0
W_AMP = 2.0

def execute_cmd(ros_cmd):
    global cmd_pub
    cmd_pub.publish(ros_cmd)

def parse_cmd(message):
    cmd = cmd_msgs_pb2.Cmd()
    cmd.ParseFromString(message)

    ros_cmd = Twist()
    linear = Vector3()
    angular = Vector3()
    linear.x = cmd.v * V_AMP
    angular.z = - cmd.w * W_AMP
    ros_cmd.linear = linear
    ros_cmd.angular = angular
    execute_cmd(ros_cmd)

class Client(Informer):
    def send_img(self, message):
        self.send(message, 'img')

    def cmd_recv(self):
        self.recv('cmd', parse_cmd)

def callback_img(ros_img):
    img = np.ndarray(shape=(720, 1280, 3), dtype=np.dtype("uint8"), buffer=ros_img.data)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (320*2, 2*240))
    ret, jpeg = cv2.imencode('.jpg', img)
    data = jpeg.tobytes()
    ifm.send_img(data)

if __name__ == '__main__':
    rospy.init_node('5g-transfer', anonymous=True)
    cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=0)
    rospy.Subscriber('/camera/color/image_raw', Image, callback_img)
    rate = rospy.Rate(1000)

    ifm = Client(config = 'config.yaml')

    while not rospy.is_shutdown():
        rate.sleep()