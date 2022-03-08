#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from os.path import join, dirname
sys.path.insert(0, join(dirname(__file__), '../Latent-RL'))

import simulator
simulator.load('/home/wang/CARLA_0.9.9.4')
import carla
sys.path.append('/home/wang/CARLA_0.9.9.4/PythonAPI/carla')
from agents.navigation.basic_agent import BasicAgent

from simulator import config, set_weather, add_vehicle
from simulator.sensor_manager import SensorManager
from utils.navigator_sim import get_map, get_nav, replan, close2dest
from utils import add_alpha_channel
import matplotlib.pyplot as plt

import os
import cv2
import time
import copy
import random
import numpy as np

from time import sleep
from informer import Informer

import cv2

ifm = Informer(
    config = 'config.yaml',
    )

MAX_SPEED = 30

global_img = None
global_view_img = None
global_nav = None
global_pcd = None
global_vel = 0
global_vehicle= None
global_plan_map = None
global_plan_time = None
global_collision = False

# import socket
# UDP_IP = "127.0.0.1"
# UDP_PORT = 6666
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

lidar_height = 2.5

def collision_callback(data):
    global global_collision
    global_collision = True

def image_callback(data):
    global global_img
    array = np.frombuffer(data.raw_data, dtype=np.dtype("uint8")) 
    array = np.reshape(array, (data.height, data.width, 4)) # RGBA format
    global_img = array
    """
    send tcp img!
    """
    ifm.send_img(global_img[...,:3])


def view_image_callback(data):
    global global_view_img, global_vehicle, global_plan_map, global_plan_time
    global_plan_time = time.time()
    array = np.frombuffer(data.raw_data, dtype=np.dtype("uint8")) 
    array = np.reshape(array, (data.height, data.width, 4)) # RGBA format
    global_view_img = array
    # global_nav = get_nav(global_vehicle, global_plan_map)

def visualize(input_img, nav=None):
    global global_vel
    img = copy.deepcopy(input_img)
    text = "speed: "+str(round(3.6*global_vel, 1))+' km/h'
    cv2.putText(img, text, (20, 30), cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 255, 255), 2)
    if nav is not None:
        new_nav = add_alpha_channel(nav)
        new_nav = cv2.flip(new_nav, 1)
        img[:nav.shape[0],-nav.shape[1]:] = new_nav

    cv2.imshow('Visualization', img)
    cv2.waitKey(5)


def log_data():
    global global_view_img

def lidar_callback(data):
    global global_pcd, global_plan_time, global_vehicle, state0
    lidar_data = np.frombuffer(data.raw_data, dtype=np.float32).reshape([-1, 3])
    mask = np.where((-lidar_data[:,2] < 5-lidar_height)&(-lidar_data[:,2] >= -lidar_height-0.1))[0]
    point_cloud = np.stack([-lidar_data[:,1][mask], -lidar_data[:,0][mask], -lidar_data[:,2][mask]])
    global_pcd = point_cloud
    # if point_cloud.shape[1] < 5400:
    #     sock.sendto(point_cloud.T.tobytes(), (UDP_IP, UDP_PORT))
    # else:
    #     sock.sendto(point_cloud[:,:5400].T.tobytes(), (UDP_IP, UDP_PORT))


def main():
    global global_vel, global_view_img, global_pcd, global_vehicle, global_plan_map, global_nav, state0, global_trajectory, global_collision, global_img
    client = carla.Client(config['host'], config['port'])
    client.set_timeout(config['timeout'])
    
    world = client.load_world('Town01')
    world.set_weather(carla.WeatherParameters.ClearNoon)

    blueprint = world.get_blueprint_library()
    world_map = world.get_map()
    
    vehicle = add_vehicle(world, blueprint, vehicle_type='vehicle.audi.a2')
    global_vehicle = vehicle

    spawn_points = world_map.get_spawn_points()
    waypoint_tuple_list = world_map.get_topology()
    origin_map = get_map(waypoint_tuple_list)

    agent = BasicAgent(vehicle, target_speed=MAX_SPEED)

    # prepare map
    destination = carla.Transform()
    destination.location = world.get_random_location_from_navigation()
    global_plan_map, destination = replan(agent, destination, copy.deepcopy(origin_map), spawn_points)

    vehicle.set_simulate_physics(True)
    # physics_control = vehicle.get_physics_control()

    sensor_dict = {
        'camera':{
            'transform':carla.Transform(carla.Location(x=0.5, y=0.0, z=2.5)),
            'callback':image_callback,
            },
        'camera:view':{
            'transform':carla.Transform(carla.Location(x=0.0, y=0.0, z=20.0), carla.Rotation(yaw=-90, pitch=-90)),
            # 'transform':carla.Transform(carla.Location(x=-3.0, y=0.0, z=6.0), carla.Rotation(pitch=-45)),
            'callback':view_image_callback,
            },
        # 'lidar':{
        #     # 'transform':carla.Transform(carla.Location(x=0.0, y=0.0, z=lidar_height)),
        #     'transform':carla.Transform(carla.Location(x=0.5, y=0.0, z=lidar_height)),
        #     'callback':lidar_callback,
        #     },
        'collision':{
            'transform':carla.Transform(carla.Location(x=0.0, y=0.0, z=0.0)),
            'callback':collision_callback,
            },
        }

    sm = SensorManager(world, blueprint, vehicle, sensor_dict)
    sm.init_all()

    global_nav = get_nav(global_vehicle, global_plan_map)

    for total_steps in range(99999999999):
        while global_view_img is None or global_nav is None:
            time.sleep(0.001)

        # visualize(global_view_img, global_nav)

        if close2dest(vehicle, destination):
            print('get destination !!!')
            destination = carla.Transform()
            destination.location = world.get_random_location_from_navigation()
            global_plan_map, destination = replan(agent, destination, copy.deepcopy(origin_map), spawn_points)

        if global_collision:
            print('Collision')
            # cv2.imwrite('result/img_log/'+log_name+'/'+str(time.time())+'.png', copy.deepcopy(global_view_img))

            start_point = random.choice(spawn_points)
            vehicle.set_transform(start_point)
            global_plan_map, destination = replan(agent, destination, copy.deepcopy(origin_map), spawn_points)

            start_waypoint = agent._map.get_waypoint(agent._vehicle.get_location())
            end_waypoint = agent._map.get_waypoint(destination.location)

            route_trace = agent._trace_route(start_waypoint, end_waypoint)
            start_point.rotation = route_trace[0][0].transform.rotation
            vehicle.set_transform(start_point)
            time.sleep(0.1)
            global_collision = False


        vel = vehicle.get_velocity()
        global_vel = np.sqrt(vel.x**2+vel.y**2+vel.z**2)

        nav = get_nav(global_vehicle, global_plan_map)
        global_nav = nav


        control = agent.run_step()
        control.manual_gear_shift = False

        vehicle.apply_control(control)

        # time.sleep(1/30.)

    cv2.destroyAllWindows()
    sm.close_all()
    vehicle.destroy()
        
if __name__ == '__main__':
    main()