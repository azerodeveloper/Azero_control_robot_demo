#!/usr/bin/python3
#coding=utf8
import sys
if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
import cv2
import numpy as np
import pid
import time
import math
import signal
import socket
import threading
import PWMServo
import check_camera
import timeout_decorator
from config import *
from cv_ImgAddText import *
import Serial_Servo_Running as SSR

print('''
**********************************************************
*****颜色跟踪:识别对应颜色的小球,让摄像头跟随小球转动*****
**********************************************************
----------------------------------------------------------
Official website:http://www.lobot-robot.com/pc/index/index
Online mall:https://lobot-zone.taobao.com/
----------------------------------------------------------
Version: --V3.2  2019/11/09
----------------------------------------------------------
''')

x_dis = 1500
y_dis = 1500
PWMServo.setServo(1, y_dis, 500)
PWMServo.setServo(2, x_dis, 500)

debug = True
target_color = "blue"

#数值范围映射
def leMap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

#获取面积最大的轮廓
def getAreaMaxContour(contours) :
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None;

        for c in contours :
            contour_area_temp = math.fabs(cv2.contourArea(c)) #计算面积
            if contour_area_temp > contour_area_max : #新面积大于历史最大面积就将新面积设为历史最大面积
                contour_area_max = contour_area_temp
                if contour_area_temp > 100: #只有新的历史最大面积大于100,才是有效的最大面积
                                           #就是剔除过小的轮廓
                    area_max_contour = c

        return area_max_contour #返回得到的最大面积，如果没有就是 None

#@timeout_decorator.timeout(0.5, use_signals=False)
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

dis_ok = False
action_finish = True
servo_1 = 1
servo_2 = 2
#执行动作
def Move():
    global servo_1
    global servo_2
    global dis_ok, x_dis, y_dis
    global action_finish
    while True:
    #云台跟踪
        if dis_ok is True:
            dis_ok = False
            action_finish = False
            PWMServo.setServo(servo_1,y_dis,20)
            PWMServo.setServo(servo_2,x_dis,20)
            time.sleep(0.02)
            action_finish = True
        else:
            time.sleep(0.01)
     
#作为子线程开启
th2 = threading.Thread(target=Move)
th2.setDaemon(True)
th2.start()

x_pid = pid.PID(P=0.1, I=0.02, D=0.01)#pid初始化
y_pid = pid.PID(P=0.2, I=0.02, D=0.01)

range_rgb = {'red': (0, 0, 255),
              'blue': (255, 0,0),
              'green': (0, 255, 0),
              }

SSR.runAction('0')
while True:
  if orgFrame is not None and ret:
    if Running:
        t1 = cv2.getTickCount()
        orgframe = cv2.resize(orgFrame, (width,height), interpolation = cv2.INTER_CUBIC) #将图片缩放到 320*240         
        img_center_x = orgframe.shape[:2][1]/2#获取缩小图像的宽度值的一半
        img_center_y = orgframe.shape[:2][0]/2
        frame = cv2.GaussianBlur(orgframe, (3, 3), 0)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB) #将图像转换到LAB空间

        frame = cv2.inRange(frame, color_range[target_color][0], color_range[target_color][1]) #根据hsv值对图片进行二值化 
        opened = cv2.morphologyEx(frame, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))#开运算
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))#闭运算
        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2] #找出所有外轮廓
        areaMaxContour = getAreaMaxContour(contours) #找到最大的轮廓
        
        centerX = 0
        centerY = 0
        radius = 0
        
        if areaMaxContour is not None:  #有找到最大面积
            (centerX, centerY), radius = cv2.minEnclosingCircle(areaMaxContour) #获取最小外接圆
            cv2.circle(orgframe, (int(centerX), int(centerY)), int(radius), range_rgb[target_color], 2) 
            if radius >= 3:
                ########pid处理#########
                #x2处理的是控制水平的舵机，y2处理控制竖直的舵机#
                #以图像的中心点的x，y坐标作为设定的值，以当前x，y坐标作为输入#
                x_pid.SetPoint = img_center_x#设定
                x_pid.update(centerX)#当前
                x_pwm = x_pid.output#输出
                x_dis += x_pwm
                x_dis = int(x_dis)
                if x_dis < 500:
                    x_dis = 500
                elif x_dis > 2500:
                    x_dis = 2500
                y_pid.SetPoint = img_center_y
                y_pid.update(2*img_center_y - centerY)
                y_pwm = y_pid.output
                y_dis -= y_pwm
                y_dis = int(y_dis)
                if y_dis < 1100:
                    y_dis = 1100
                elif y_dis > 1800:
                    y_dis = 1800
                if action_finish:
                    dis_ok = True
                                       
        t2 = cv2.getTickCount()
        time_r = (t2 - t1) / cv2.getTickFrequency()               
        fps = 1.0/time_r
        if debug:
            orgframe = cv2ImgAddText(orgframe, "云台跟踪", 10, 10, textColor=(0, 0, 0), textSize=20)
            cv2.putText(orgframe, "FPS:" + str(int(fps)),
                    (10, orgframe.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)#(0, 0, 255)BGR
            cv2.imshow("orgframe", orgframe)
            cv2.waitKey(1)
    else:
        time.sleep(0.01)
  else:
    time.sleep(0.01)
cap.release()
cv2.destroyAllWindows()