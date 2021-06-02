#!/usr/bin/python3
# encoding: utf-8
#
# ##实现功能: 实现一个服务器来提供切换各个玩法的功能
#
import sys
if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
import subprocess
import time
import threading
import os
import socketserver
import re
import signal
import get_data
    
lastMode = 0
lastPID = None


class LobotServer(socketserver.TCPServer):
    allow_reuse_address = True  # 地址重用


class LobotServerHandler(socketserver.BaseRequestHandler):
    ip = ""
    port = None
    buf = ""

    def setup(self):
        self.ip = self.client_address[0].strip()  # 获取客户端的ip
        self.port = self.client_address[1]  # 获取客户端的端口
        print("connected\tIP:" + self.ip + "\tPort:" + str(self.port))
        self.request.settimeout(20)  # 连接超时设为20秒

    def handle(self):
        global lastMode
        global lastPID
        Flag = True
        while Flag:           
            try:
                recv = self.request.recv(128)  # 接收数据v
                if recv == b'':
                    Flag = False  # 空则推出
                else:
                    self.buf += recv.decode()  # 解码
                    #print(self.buf)
                    self.buf = re.sub(r'333333','',self.buf, 10)  # 约定客户端通过发送'3'来进行心跳， 删除字符串中的3
                    s = re.search(r'mode=\d{1,2}', self.buf, re.I) # 查找字符串中的 MODE=数字  格式的字串
                    if s:
                        self.buf=""   # 只要找到一个就将所有的缓存清除
                        Mode = int(s.group()[5:])  # 从字串中获取mode的数值
                        print(Mode)
                        data = get_data.read_data()
                        if data[1] == "0":
                            lastMode = 0
                        # 根据Mode的数值 向 对于的子进程发送继续运行信号，对应的子进程运行，产生效果
                        if Mode == 0:
                            lastMode = Mode   
                            try:
                                os.kill(lastPID, signal.SIGKILL)
                            except:
                                pass
                            self.request.sendall("OK".encode())   # 向客户端发送“OK"
                        elif Mode == 1:
                            if lastMode != Mode:
                                lastMode = Mode                                         
                                if lastPID is not None and get_data.read_data()[0] != 'K':
                                    os.kill(lastPID, signal.SIGKILL)
                                ChildCvFindStream = subprocess.Popen(["python3", "/home/pi/human_code/cv_find_stream.py"])  # 自动射门 
                                lastPID = ChildCvFindStream.pid
                                get_data.write_data(str(lastPID), str(lastMode))
                                print("lastPID:", lastPID)
                            self.request.sendall("OK".encode())
                        elif Mode == 2:
                            if lastMode != Mode:
                                lastMode = Mode
                                if lastPID is not None and get_data.read_data()[0] != 'K':
                                    os.kill(lastPID, signal.SIGKILL)
                                ChildColorStream = subprocess.Popen(["python3", "/home/pi/human_code/cv_color_stream.py"])  # 颜色识别
                                lastPID = ChildColorStream.pid
                                get_data.write_data(str(lastPID), str(lastMode))
                                print("lastPID:", lastPID)
                            self.request.sendall("OK".encode())
                        elif Mode == 3:
                            if lastMode != Mode:
                                lastMode = Mode
                                if lastPID is not None and get_data.read_data()[0] != 'K':
                                    os.kill(lastPID, signal.SIGKILL)
                                ChildCvFindHand = subprocess.Popen(["python3", "/home/pi/human_code/cv_find_hand.py"])  # 手势识别
                                lastPID = ChildCvFindHand.pid
                                get_data.write_data(str(lastPID), str(lastMode))
                                print("lastPID:", lastPID)
                            self.request.sendall("OK".encode())
                        elif Mode == 4:
                            if lastMode != Mode:
                                lastMode = Mode
                                if lastPID is not None and get_data.read_data()[0] != 'K':
                                    os.kill(lastPID, signal.SIGKILL)
                                ChildCvLinePatrol = subprocess.Popen(["python3", "/home/pi/human_code/cv_line_patrol.py"]) # 寻线
                                lastPID = ChildCvLinePatrol.pid
                                get_data.write_data(str(lastPID), str(lastMode))
                                print("lastPID:", lastPID)
                            self.request.sendall("OK".encode())
                        elif Mode == 5:
                            if lastMode != Mode:
                                lastMode = Mode
                                if lastPID is not None and get_data.read_data()[0] != 'K':
                                    os.kill(lastPID, signal.SIGKILL)
                                ChildCvTrackStream = subprocess.Popen(["python3", "/home/pi/human_code/cv_track_stream.py"])  # 云台跟踪
                                lastPID = ChildCvTrackStream.pid
                                get_data.write_data(str(lastPID), str(lastMode))
                                print("lastPID:", lastPID)
                            self.request.sendall("OK".encode())
                            
                        else:
                            lastMode = 0
                            if lastPID is not None and get_data.read_data()[0] != 'K':
                                os.kill(lastPID, signal.SIGKILL)
                            lastPID = None
                            self.request.sendall("Failed".encode())
                            pass
            except Exception as e:
                print(e)
                Flag = False

    def finish(self):
        global lastMode
        global lastPID

        lastMode = 0
        data = get_data.read_data()
        print("data[0]:", len(data[0]))
        if data[0] != "K":
            os.kill(lastPID, signal.SIGKILL)
        lastPID = None
        get_data.write_data(str("K"), str(lastMode))
        print("disconnected\tIP:" + self.ip + "\tPort:" + str(self.port))


if __name__ == '__main__':
    server = LobotServer(("", 9040), LobotServerHandler)
    server.serve_forever()  # 启动服务器

