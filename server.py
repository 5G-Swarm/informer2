#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
from time import sleep
import numpy as np

from informer import Informer
from proto.python_out import cmd_msgs_pb2

import math
import pygame
try:
    import pygame
    from pygame.locals import K_DOWN
    from pygame.locals import K_LEFT
    from pygame.locals import K_RIGHT
    from pygame.locals import K_SPACE
    from pygame.locals import K_UP
    from pygame.locals import K_a
    from pygame.locals import K_d
    from pygame.locals import K_s
    from pygame.locals import K_w
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

def parse_vehicle_wheel(joystick, clock):
    # control = carla.VehicleControl()
    keys = pygame.key.get_pressed()
    milliseconds = clock.get_time()

    throttle = 1.0 if keys[K_UP] or keys[K_w] else 0.0
    steer_increment = 5e-4 * milliseconds
    if keys[K_LEFT] or keys[K_a]:
        steer_cache -= steer_increment
    elif keys[K_RIGHT] or keys[K_d]:
        steer_cache += steer_increment
    else:
        steer_cache = 0.0
    steer_cache = min(0.7, max(-0.7, steer_cache))
    steer = round(steer_cache, 1)
    brake = 1.0 if keys[K_DOWN] or keys[K_s] else 0.0
    # hand_brake = keys[K_SPACE]

    numAxes = joystick.get_numaxes()
    jsInputs = [float(joystick.get_axis(i)) for i in range(numAxes)]

    # jsButtons = [float(joystick.get_button(i)) for i in
    #                 range(joystick.get_numbuttons())]

    # Custom function to map range of inputs [1, -1] to outputs [0, 1] i.e 1 from inputs means nothing is pressed
    # For the steering, it seems fine as it is
    K1 = 1.0  # 0.55
    steerCmd = K1 * math.tan(1.1 * jsInputs[0])

    K2 = 1.6  # 1.6
    throttleCmd = K2 + (2.05 * math.log10(
        -0.7 * jsInputs[2] + 1.4) - 1.2) / 0.92
    if throttleCmd <= 0:
        throttleCmd = 0
    elif throttleCmd > 1:
        throttleCmd = 1

    brakeCmd = 1.6 + (2.05 * math.log10(
        -0.7 * jsInputs[3] + 1.4) - 1.2) / 0.92
    if brakeCmd <= 0:
        brakeCmd = 0
    elif brakeCmd > 1:
        brakeCmd = 1

    steer = steerCmd
    brake = brakeCmd
    throttle = throttleCmd
    #toggle = jsButtons[_reverse_idx]
    # hand_brake = bool(jsButtons[4])
    # reverse = gear < 0
    # return control
    return steer, throttle, brake

def parse_img(message):
    # print("Get img size:",len(message))
    nparr = np.frombuffer(message, np.uint8)
    img = cv2.imdecode(nparr,  cv2.IMREAD_COLOR)
    cv2.imshow('Image',img)
    cv2.waitKey(1)

class Server(Informer):
    def img_recv(self):
        self.recv('img', parse_img)

    def send_cmd(self, message):
        self.send(message, 'cmd')

def get_cmd(steer, throttle, brake):
    cmd = cmd_msgs_pb2.Cmd()
    cmd.v = throttle if brake < 0.01 else 0.
    cmd.w = steer
    sent_data = cmd.SerializeToString()
    return sent_data


if __name__ == '__main__':
    import evdev
    from evdev import ecodes, InputDevice
    device = evdev.list_devices()[0]
    evtdev = InputDevice(device)
    val = 25000 #[0,65535]
    evtdev.write(ecodes.EV_FF, ecodes.FF_AUTOCENTER, val)


    pygame.init()
    clock = pygame.time.Clock()
    pygame.joystick.init()

    joystick_count = pygame.joystick.get_count()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    ifm = Server(
        config = 'config_recv.yaml',
        )

    while True:
        for event in pygame.event.get(): # User did something.
            if event.type == pygame.QUIT: # If user clicked close.
                done = True # Flag that we are done so we exit this loop.
            elif event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
            elif event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")

        steer, throttle, brake = parse_vehicle_wheel(joystick, clock)

        cmd = get_cmd(steer, throttle, brake)
        ifm.send_cmd(cmd)

        clock.tick(20)