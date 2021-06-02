#!/usr/bin/python3
#coding=utf8
import sys
if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
import cv2
import numpy as np
import time
import math
import signal
import threading
import PWMServo
import check_camera
import timeout_decorator
from config import *
from cv_ImgAddText import *
import Serial_Servo_Running as SSR

print('''
**********************************************************
*颜色识别:分辨出红,绿,蓝,然后根据分辨出的颜色作出对应动作*
**********************************************************
----------------------------------------------------------
Official website:http://www.lobot-robot.com/pc/index/index
Online mall:https://lobot-zone.taobao.com/
----------------------------------------------------------
Version: --V3.2  2019/11/09
----------------------------------------------------------
''')

PWMServo.setServo(1, 1500, 500)
PWMServo.setServo(2, 1500, 500)

debug = True

#数值映射
#将一个数从一个范围映射到另一个范围
def leMap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

#找出面积最大的轮廓
#参数为要比较的轮廓的列表
def getAreaMaxContour(contours) :
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None;

        for c in contours : #历遍所有轮廓
            contour_area_temp = math.fabs(cv2.contourArea(c)) #计算轮廓面积
            if contour_area_temp > contour_area_max :
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  #只有在面积大于300时，最大面积的轮廓才是有效的，以过滤干扰
                    area_max_contour = c

        return area_max_contour, contour_area_max#返回最大的轮廓

@timeout_decorator.timeout(0.5, use_signals=False)
def Camera_isOpened():
    global stream, cap
    cap = cv2.VideoCapture(stream) 

#摄像头默认分辨率640x480,处理图像时会相应的缩小图像进行处理，这样可以加快运行速度
#缩小时保持比例4：3,且缩小后的分辨率应该是整数
c = 80
width, height = c*4, c*3
resolution = str(width) + "x" + str(height)
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

get_color = False
color_max = None
action_finish = True
def runAction():
    global get_color, action_finish
    global color_max
    while True:
        if get_color:
            get_color = False
            action_finish = False
            if color_max == 'red':
                PWMServo.setServo(1, 1800, 200)
                time.sleep(0.2)
                PWMServo.setServo(1, 1200, 200)
                time.sleep(0.2)
                PWMServo.setServo(1, 1800, 200)
                time.sleep(0.2)
                PWMServo.setServo(1, 1200, 200)
                time.sleep(0.2)
                PWMServo.setServo(1, 1500, 100)
                SSR.runAction('pick')
                time.sleep(1)
                action_finish = True
            elif color_max == 'green' or color_max == 'blue':
                PWMServo.setServo(2, 1800, 200)
                time.sleep(0.2)
                PWMServo.setServo(2, 1200, 200)
                time.sleep(0.2)
                PWMServo.setServo(2, 1800, 200)
                time.sleep(0.2)
                PWMServo.setServo(2, 1200, 200)
                time.sleep(0.2)
                PWMServo.setServo(2, 1500, 100)
                SSR.runAction('0')
                time.sleep(1)
                action_finish = True
            else:
                get_color = False
                time.sleep(0.01)
        else:
           time.sleep(0.01)
          
#启动动作运行子线程
th2 = threading.Thread(target=runAction)
th2.setDaemon(True)
th2.start()

range_rgb = {'red': (0, 0, 255),
              'blue': (255, 0,0),
              'green': (0, 255, 0),
              'black': (0, 0, 0),
              }

Color_BGR = (0, 0, 0)
COLOR = 'None'
color_list = []
SSR.runAction('0')
while True:     
  if orgFrame is not None and ret:
    if Running:
        t1 = cv2.getTickCount()  
        orgframe = cv2.resize(orgFrame, (width, height), interpolation = cv2.INTER_CUBIC) #将图片缩放     
        frame = cv2.GaussianBlur(orgframe, (3,3), 0)#高斯模糊
        Frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)#将图片转换到LAB空间
        
        rad = 0
        areaMaxContour = 0
        max_area = 0
        area_max = 0
        centerX = 0
        centerY = 0
        if action_finish: 
            for i in color_range:
                if i != 'black' and i != 'white':
                    frame = cv2.inRange(Frame, color_range[i][0], color_range[i][1])#对原图像和掩模进行位运算
                    opened = cv2.morphologyEx(frame, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))#开运算
                    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))#闭运算
                    contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]#找出轮廓
                    areaMaxContour, area_max = getAreaMaxContour(contours)#找出最大轮廓
                    if areaMaxContour is not None:
                        if area_max > max_area:#找最大面积
                            max_area = area_max
                            color_max = i
                            areaMaxContour_max = areaMaxContour
        if max_area != 0:
            ((centerX, centerY), rad) = cv2.minEnclosingCircle(areaMaxContour_max)  # 获取最小外接圆
            centerX, centerY, rad = int(centerX), int(centerY), int(rad)#获取圆心，半径
            cv2.circle(orgframe, (centerX, centerY), rad, (0, 255, 0), 2)#画圆
            if color_max == 'red':  #红色最大
                color = 1
            elif color_max == 'green':  #绿色最大
                color = 2
            elif color_max == 'blue':  #蓝色最大
                color = 3                   
            else: 
                color = 0
            color_list.append(color)
            if len(color_list) == 10:
                color = int(round(np.mean(color_list)))
                color_list = []
                if color == 1:
                    COLOR = 'red'
                    Color_BGR = range_rgb["red"]
                elif color == 2:
                    COLOR = 'green'
                    Color_BGR = range_rgb["green"]
                elif color == 3:
                    COLOR = 'blue'
                    Color_BGR = range_rgb["blue"]
                else:
                    color_max = 'None'
                    Color_BGR = range_rgb["black"]
                get_color = True
        else:
            if action_finish:
                Color_BGR = (0, 0, 0)
                COLOR = "None"
        
        t2 = cv2.getTickCount()
        time_r = (t2 - t1) / cv2.getTickFrequency()               
        fps = 1.0/time_r
        if debug:
            orgframe = cv2ImgAddText(orgframe, "颜色识别", 10, 10, textColor=(0, 0, 0), textSize=20)
            cv2.putText(orgframe, "Color: " + COLOR, (10, orgframe.shape[0] - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, Color_BGR, 2)
            cv2.putText(orgframe, "FPS:" + str(int(fps)),
                    (10, orgframe.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)#(0, 0, 255)BGR
            cv2.namedWindow('orgframe')
            cv2.imshow("orgframe", orgframe)
            cv2.waitKey(1)
    else:
        time.sleep(0.01)
  else:
    time.sleep(0.01)
cap.release()
cv2.destroyAllWindows()