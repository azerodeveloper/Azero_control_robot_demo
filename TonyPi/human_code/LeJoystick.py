#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import pygame
import time
import os
from socket import *


HOST = "127.0.0.1"
PORT = 1075
client = None
connected = False
cmd = ""

key_map = {"PSB_CROSS": 2, "PSB_CIRCLE": 1, "PSB_SQUARE": 3, "PSB_TRIANGLE": 0,
           "PSB_L1": 4, "PSB_R1": 5, "PSB_L2": 6, "PSB_R2": 7,
           "PSB_SELECT": 8, "PSB_START": 9, "PSB_L3": 10, "PSB_R3": 11}
action_map = ["CROSS", "CIRCLE", "", "SQUARE", "TRIANGLE", "L1", "R1", "L2", "R2", "SELECT", "START", "", "L3", "R3"]

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.joystick.init()
pygame.display.init()
js = None

if pygame.joystick.get_count() > 0:
    js = pygame.joystick.Joystick(0)
    js.init()
    jsName = js.get_name()
    print("Name of the joystick:", jsName)
    jsAxes = js.get_numaxes()
    print("Number of axis:", jsAxes)
    jsButtons = js.get_numbuttons()
    print("Number of buttons:", jsButtons)
    jsBall = js.get_numballs()
    print("Numbe of balls:", jsBall)
    jsHat = js.get_numhats()
    print("Number of hats:", jsHat)


def control_code():
    global cmd
    global client
    if js.get_button(key_map["PSB_R1"]):  # R1
        cmd = "I003-" + str(15) + "-1\r\n"  #开怀大笑
        client.send(cmd.encode())
        print ('R1')
    if js.get_button(key_map["PSB_R2"]):  # R2:
        cmd = "I003-" + str(30) + "-1\r\n"  #
        client.send(cmd.encode())
        print ('R2')
    if js.get_button(key_map["PSB_SQUARE"]):  # 口
        print ('口')
        cmd = "I003-" + str(31) + "-1\r\n"  #
        client.send(cmd.encode())
    if js.get_button(key_map["PSB_CIRCLE"]):  # ○
        print ('O')
        cmd = "I003-" + str(14) + "-1\r\n"  #下蹲
        client.send(cmd.encode())
    if js.get_button(key_map["PSB_TRIANGLE"]):  # △
        print ('△')
        cmd = "I003-" + str(7) + "-1\r\n"  #俯卧撑
        client.send(cmd.encode())
    if js.get_button(key_map["PSB_CROSS"]):  # X
        print ('X')
        cmd = "I003-" + str(8) + "-1\r\n"  #仰卧起坐
        client.send(cmd.encode())
    if js.get_button(key_map["PSB_L1"]):
        print ('L1')
        cmd = "I003-" + str(9) + "-1\r\n"  #挥手 
        client.send(cmd.encode())
    if js.get_button(key_map["PSB_L2"]):
        print ('L2')
        cmd = "I003-" + str(10) + "-1\r\n"  #鞠躬
        client.send(cmd.encode())

    # 按键上下左右
    hat = js.get_hat(0)
    if hat[0] > 0:
        print ('按键_右')
        cmd = "I003-" + str(4) + "-1\r\n"  # 右转
        client.send(cmd.encode())
    elif hat[0] < 0:
        print ('按键_左')
        cmd = "I003-" + str(3) + "-1\r\n"  # 左转
        client.send(cmd.encode())
    else:
        pass
    if hat[1] > 0:
        print ('按键_上')
        cmd = "I003-" + str(1) + "-1\r\n"    # 前进
        client.send(cmd.encode())
    elif hat[1] < 0:
        print ('按键_下')
        cmd = "I003-" + str(2) + "-1\r\n"    # 后退
        client.send(cmd.encode())
    else:
        pass
    # 左摇杆
    lx = js.get_axis(0)
    ly = js.get_axis(1)
    # 右摇杆
    rx = js.get_axis(2)
    ry = js.get_axis(3)
    if lx > 0.5:
        print ('lx: 右')
        cmd = "I003-" + str(4) + "-1\r\n"  # 右转
        client.send(cmd.encode())
    elif lx < -0.5:
        print ('lx: 左')
        cmd = "I003-" + str(3) + "-1\r\n"  # 左转
        client.send(cmd.encode())
    else:
        pass

    if ly > 0.5:
        print ('lx: 下')
        cmd = "I003-" + str(1) + "-1\r\n"  # 前进
        client.send(cmd.encode())
    elif ly < -0.5:
        print ('lx: 上')
        cmd = "I003-" + str(2) + "-1\r\n"  # 后退
        client.send(cmd.encode())
    else:
        pass
    if rx > 0.5:
        print ('rx: 右')
        cmd = "I003-" + str(12) + "-1\r\n"  # 右侧滑
        client.send(cmd.encode())
    elif rx < -0.5:
        print ('rx: 左')
        cmd = "I003-" + str(11) + "-1\r\n"  # 左侧滑
        client.send(cmd.encode())
    else:
        pass
    if ry > 0.5:
        print ('rx: 下')
        cmd = "I003-" + str(50) + "-1\r\n"  # 
        client.send(cmd.encode())
    elif ry < -0.5:
        print ('rx: 上')
        cmd = "I003-" + str(51) + "-1\r\n"  # 
        client.send(cmd.encode())
    else:
        pass
    if js.get_button(key_map["PSB_START"]):  # 立正
        cmd = "I003-" + str(0) + "-1\r\n"
        client.send(cmd.encode())
    cmd = ""


while True:
    if os.path.exists("/dev/input/js0") is True:
        if connected is False:
            jscount = pygame.joystick.get_count()
            print('js', jscount)
            if jscount > 0:
                try:
                    js = pygame.joystick.Joystick(0)
                    js.init()
                    client = socket(AF_INET, SOCK_STREAM)   # 创建客户端
                    client.connect((HOST, PORT))    # 连接服务器端
                    connected = True
                except Exception as e:
                    print(e)
            else:
                pygame.joystick.quit()
        else:
            pass
    else:
        if connected is True:
            connected = False
            js.quit()
            pygame.joystick.quit()
            client.close()
        else:
            pass
    if connected is True:
        pygame.event.pump()
        try:
            control_code()
        except Exception as e:
            print(e)
            connected = False
            client.close()
    time.sleep(0.06)
