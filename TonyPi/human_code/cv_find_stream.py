#!/usr/bin/python3
#coding=utf8
import sys
if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
import cv2
import time
import math
import socket
import signal
import threading
import PWMServo
import check_camera
import numpy as np
import timeout_decorator
from config import *
from cv_ImgAddText import *
import Serial_Servo_Running as SSR

print('''
**********************************************************
自动射门：通过摄像头检测球形，让机器人根据球形位置进行射击
**********************************************************
----------------------------------------------------------
Official website:http://www.lobot-robot.com/pc/index/index
Online mall:https://lobot-zone.taobao.com/
----------------------------------------------------------
Version: --V3.2  2019/11/09
----------------------------------------------------------
''')

PWMServo.setServo(1, servo1, 500)
PWMServo.setServo(2, servo2, 500)

debug = True

def read_data():
    in_file = open("/home/pi/human_code/share.txt", "r")
    state = in_file.readline()
    in_file.close()
    return state

#数值映射
def leMap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

#找出最大的轮廓
def getAreaMaxContour(contours) :
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None;

        for c in contours : #历便所有轮廓
            contour_area_temp = math.fabs(cv2.contourArea(c)) #计算面积
            if contour_area_temp > contour_area_max :
                contour_area_max = contour_area_temp
                if contour_area_temp > 50:  #限制最小面积
                    area_max_contour = c

        return area_max_contour  #返回最大面积

@timeout_decorator.timeout(0.5, use_signals=False)
def Camera_isOpened():
    global stream, cap
    cap = cv2.VideoCapture(stream) 

#摄像头默认分辨率640x480,处理图像时会相应的缩小图像进行处理，这样可以加快运行速度
#缩小时保持比例4：3,且缩小后的分辨率应该是整数
c = 80
width, height = c*4, c*3
resolution = str(width) + "x" + str(height)
orgFrame = None
Running = True
ret = False
stream = "http://127.0.0.1:8080/?action=stream?dummy=param.mjpg"
try:
    Camera_isOpened()
    cap = cv2.VideoCapture(stream)
except:
    print('Unable to detect camera! \n')
    check_camera.CheckCamera()
    
orgFrame = None
ret = False
Running = True
def get_image():
    global orgFrame
    global ret
    global Running
    global stream, cap
    global width, height
    while True:
        if Running:
            try:
                if cap.isOpened():
                    ret, orgFrame = cap.read()
                else:
                    time.sleep(0.01)
            except:               
                cap = cv2.VideoCapture(stream)
                print('Restart Camera Successful!')
        else:
            time.sleep(0.01)

th1 = threading.Thread(target = get_image)
th1.setDaemon(True)
th1.start()

step = 1
count = 0
centerX = 0
centerY = 0 
xc = False
stoop = False
get_ball = False
count = 0 
SSR.runAction('0')
#执行动作组
def logic():
    global xc
    global centerX
    global centerY
    global Running
    global step 
    global stoop
    global count
    global get_ball
    
    while True:
        if Running is True:
            if xc is True:               
                if stoop:
                    SSR.runAction('0')
                    time.sleep(0.5)
                    stoop = False
                    get_ball = True
                    step = 5
                count = 0
                if step == 1:
                    if 640 >= centerX + (320 - centerx) > 520:#不在中心，根据方向让机器人转向一步
                        SSR.runAction('right_move_one_step')
                        print('1')
                    elif 0 <= centerX + (320 - centerx) < 120:
                        SSR.runAction('left_move_one_step')
                        print('2')
                    else:
                        step = 2
                    xc = False
                elif step == 2:
                    print(centerY)
                    if 250 < centerY <= 380:
                        print(3)
                        SSR.runAction('go_fast')
                        step = 3
                    elif 0 <= centerY <= 200:
                        print(3)
                        SSR.runAction('go_fast')
                        SSR.runAction('go_fast')
                        SSR.runAction('go_fast')
                        step = 3
                    else:
                        step = 4                  
                    xc = False
                elif step == 3:
                    if 640 >= centerX + (320 - centerx) > 450:#不在中心，根据方向让机器人转向一步
                        SSR.runAction('right_move_one_step')
                        print('1')
                    elif 0 <= centerX + (320 - centerx) < 190:
                        SSR.runAction('left_move_one_step')
                        print('2')
                    else:
                        step = 2
                    xc = False                    
                elif step == 4:
                    if (320 - centerx > 0 and centerx + 80 > centerX) or (320 - centerx < 0 and  centerx + 180 > centerX):#不在中心，根据方向让机器人转向一步
                        if get_ball:
                            SSR.runAction('stand_')
                            time.sleep(0.5)
                        SSR.runAction('left_move_one_step')
                        print('4')                       
                    elif (320 - centerx > 0 and centerx + 180 < centerX) or (320 - centerx < 0 and  centerx - 80 < centerX):
                        if get_ball:
                            SSR.runAction('stand_')
                            time.sleep(0.5)
                        SSR.runAction('right_move_one_step')                       
                        print('5')
                    else:
                        SSR.stop_action_group()
                        get_ball = False
                        step = 5
                    if get_ball:                                               
                        step = 5
                    else:
                        xc = False
                elif step == 5:
                    print('ok')
                    SSR.runAction('stand_')
                    SSR.runAction('stoop')
                    time.sleep(0.5)
                    if get_ball:
                        step = 4
                    else:
                        step = 6
                    xc = False
                elif step == 6:
                    print(centerY)
                    if 0 < centerY <= 250:
                        print('6')
                        SSR.runAction('stand_')
                        SSR.runAction('go_fast')
                        SSR.runAction('go_fast')  
                        step = 5
                    elif 250 < centerY <= 380:
                        print('7')
                        SSR.runAction('stand_')
                        SSR.runAction('go_fast')
                        step = 5
                    elif centerY > 380:
                        print('8')
                        print(centerY)
                        step = 7
                    else:
                        step = 1
                elif step == 7:
                    if (320 - centerx) >= 0:
                        print('shot_right')
                        SSR.runAction('stand_')
                        SSR.runAction('shot_right')                      
                        step = 1
                        xc = False
                    elif (320 - centerx) < 0:
                        print('shot_left')
                        SSR.runAction('stand_')
                        SSR.runAction('shot_left')
                        step = 1
                        xc = False
            else:                
                if step == 1:
                    if count >= 50:
                        count = 50
                        if not stoop:                       
                            stoop = True
                            SSR.runAction('0')
                            SSR.runAction('stoop')
                            time.sleep(2)
                        else:
                            PWMServo.setServo(1, servo1 + 250, 500)
                            time.sleep(2)
                            PWMServo.setServo(1, servo1, 500)
                            time.sleep(2)
        else:
            time.sleep(0.01)

#启动动作的线程
th2 = threading.Thread(target=logic)
th2.setDaemon(True)
th2.start()

range_rgb = {'red': (0, 0, 255),
              'blue': (255, 0,0),
              'green': (0, 255, 0),
              }

circles_list = []
while True:
  if orgFrame is not None and ret:
    if Running:
        t1 = cv2.getTickCount()
        orgframe = cv2.resize(orgFrame,(width, height), interpolation = cv2.INTER_CUBIC)
        gray_img = cv2.cvtColor(orgframe, cv2.COLOR_BGR2GRAY)
        img = cv2.medianBlur(gray_img, 11)
        circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,400,param1=100,param2=10,minRadius=10,maxRadius=60)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            circle = circles[0,:][0]
            centerX, centerY, rad = circle[0], circle[1], circle[2]
            circles_list.append([centerX, centerY])            
            if len(circles_list) == 3:                   
                var = np.mean(np.var(circles_list, axis=0))
                circles_list = []
                if var <= 1.5:
                    centerX = int(leMap(centerX, 0.0, width, 0.0, 640.0))  #将数据从0-width 映射到 0-640
                    centerY = int(leMap(centerY, 0.0, height, 0.0, 480.0))
                    xc = True                    
            cv2.circle(orgframe,(centerX, centerY), rad, (255, 0, 0), 2)
        else:
            centerX, centerY = 0, 0
        t2 = cv2.getTickCount()
        time_r = (t2 - t1) / cv2.getTickFrequency()
        fps = 1.0/time_r
        if debug:
            #print(centerX)
            orgframe = cv2ImgAddText(orgframe, "点球射门", 10, 10, textColor=(0, 0, 0), textSize=20)
            cv2.putText(orgframe, "FPS:" + str(int(fps)),
                    (10, orgframe.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)#(0, 0, 255)BGR
            cv2.imshow("orgFframe", orgframe)
            cv2.waitKey(1)
        count += 1
    else:
        time.sleep(0.01)
  else:
     time.sleep(0.01)      
cap.release()
cv2.destroyAllWindows()