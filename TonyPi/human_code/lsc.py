#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import socketserver
import PWMServo
import Serial_Servo_Running as SSR
import threading
import get_data
import math
from config_serial_servo  import  serial_servo_read_vin
import time
import os

DEBUG = False
client_socket = []

SSR.start_action_thread()

class LobotServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True  # 允许地址重用

class LobotServerHandler(socketserver.BaseRequestHandler):
    global client_socket
    ip = ""
    port = None

    def setup(self):
        self.ip = self.client_address[0].strip()
        self.port = self.client_address[1]
        print("connected\tIP:"+self.ip+"\tPort:"+str(self.port))
        client_socket.append(self.request)  # 将此连接加入客户端列表
        self.request.settimeout(6)  # 超时时间为6秒

    def handle(self):
        global action_num, action_times, inf_flag
        conn = self.request
        recv_data = b''
        Flag = True
        stop = False
        t2 = 0
        while Flag:
            try:
                buf = conn.recv(128)
                if buf == b'':
                    Flag = False
                else:
                    recv_data = recv_data + buf
                    print(recv_data)
                    if len(recv_data) <= 13:                     
                        # 解决断包问题，接收到完整命令后才发送到串口,防止出错
                        while True:
                            try:
                                index = recv_data.index(b'\x55\x55')  # 搜索数据中的0x55 0x55
                                if len(recv_data) >= index+3:  # 缓存中的数据长度是否足够
                                    recv_data = recv_data[index:]
                                    if recv_data[2] + 2 <= len(recv_data):  # 缓存中的数据长度是否足够
                                        cmd = recv_data[0:(recv_data[2]+2)]    # 取出命令
                                        #print(cmd)
                                        recv_data = recv_data[(recv_data[2]+3):]  # 去除已经取出的命令
                                        if cmd[0] and cmd[1] is 0x55:
                                            if cmd[2] == 0x08 and cmd[3] == 0x03:  # 数据长度和控制单舵机命令
                                                id = cmd[7]
                                                pos = 0xffff & cmd[8] | 0xff00 & (cmd[9] << 8)
                                                print('id:', cmd[7], 'pos:', pos)
                                                if id == 7:
                                                    if 1900 < pos:
                                                        pos = 1900
                                                    elif pos < 1200:
                                                        pos = 1200
                                                    PWMServo.setServo(1, 3000 - pos, 20)
                                                elif id == 6:
                                                    PWMServo.setServo(2, 3000 - pos, 20)
                                                else:
                                                    pass
                                            elif cmd[2] == 0x05 and cmd[3] == 0x06:
                                                action_num = cmd[4]
                                                action_times = 0xffff & cmd[5] | 0xff00 & cmd[6] << 8

                                                if action_num == 0:
                                                    SSR.stop_action_group()
                                                    SSR.change_action_value('stand_slow', 1)
                                                    try:
                                                        data = get_data.read_data()                                          
                                                        if data[0] != 'K':
                                                            os.system('sudo kill -9 ' + str(data[0]))
                                                            PWMServo.setServo(1, 1500, 300)
                                                            PWMServo.setServo(2, 1500, 300)                                                        
                                                            get_data.write_data("K", "0")
                                                    except BaseException as e:
                                                        print(e)
                                                    
                                                elif action_times == 0:  # 无限次                                                    
                                                    print('action', action_num, 'times', action_times)
                                                    SSR.change_action_value(str(action_num), action_times)
                                                    stop = True
                                                else:
                                                    print('action', action_num, 'times', action_times)
                                                    if stop:                                                       
                                                        SSR.stop_action_group()
                                                        SSR.change_action_value('stand_slow', 1)
                                                        stop = False
                                                    else:
                                                        print('action', action_num, 'times', action_times)
                                                        SSR.change_action_value(str(action_num), action_times)
                                                         
                                            elif cmd[2] == 0x0b and cmd[3] == 0x03:
                                                PWMServo.setServo(1, 1500, 100)
                                                PWMServo.setServo(2, 1500, 100)
                                                time.sleep(0.1)
                                            
                                            elif cmd[2] == 0x02 and cmd[3] == 0x0F:                                               
                                                if SSR.action_finish():
                                                    try:
                                                        time.sleep(0.05)
                                                        v = math.ceil(serial_servo_read_vin(1))
                                                        buf = [0x55, 0x55, 0x04, 0x0F, 0x00, 0x00]
                                                        buf[4] = v & 0xFF
                                                        buf[5] = (v >> 8) & 0xFF
                                                        conn.sendall(bytearray(buf))
                                                    except BaseException as e:
                                                        print(e)    
                                        if DEBUG is True:
                                            for i in cmd:
                                                print (hex(i))
                                            print('*' * 30)
                                    else:
                                        break
                                else:
                                    break
                            except Exception as e:   # 在recv_data 中搜不到 '\x55\x55'子串
                                break
                        recv_data = b''
                        action_times = None
                        action_num = None
                    else:
                        recv_data = b''
                        pass
            except Exception as e:
                print(e)
                Flag = False
                break

    def finish(self):
        client_socket.remove(self.request)  # 从客户端列表中剔除此连接
        print("disconnected\tIP:"+self.ip+"\tPort:"+str(self.port))

if __name__ == "__main__":
    server = LobotServer(("", 9029), LobotServerHandler)    # 建立服务器
    try:
        server.serve_forever()  # 开始服务器循环
    except Exception as e:
        print(e)
        server.shutdown()
        server.server_close()

