#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep
from informer import Informer
from proto.python_out import cmd_msgs_pb2
import cv2
import numpy as np

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image

def execute_cmd(ros_cmd):
    cmd_pub.publish(ros_cmd)

def parse_cmd(message):
    cmd = cmd_msgs_pb2.Cmd()
    cmd.ParseFromString(message)

    ros_cmd = Twist()
    ros_cmd.linear.x = cmd.v
    ros_cmd.angular.z = cmd.w
    execute_cmd(cmd)

class Client(Informer):
    def send_img(self, message):
        self.send(message, 'img')

    def cmd_recv(self):
        self.recv('cmd', parse_cmd)

ifm = Client(
    config = 'config.yaml',
    )

def callback_img(ros_img):
    img = np.ndarray(shape=(480, 640, 3), dtype=np.dtype("uint8"), buffer=ros_img.data)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # img = cv2.resize(img, (320*4, 4*240))
    ret, jpeg = cv2.imencode('.jpg', img)
    data = jpeg.tobytes()
    ifm.send_img(data)
    # print('send !')


if __name__ == '__main__':
    rospy.init_node('5g-transfer', anonymous=True)
    cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=0)
    rospy.Subscriber('/camera/color/image_raw', Image, callback_img)

    rate = rospy.Rate(1000)
    while not rospy.is_shutdown():
        rate.sleep()