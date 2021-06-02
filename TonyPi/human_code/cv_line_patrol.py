#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# 小球颜色识别后执行动作组
import sys
if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
import cv2
import numpy as np
import time
import threading
import math
import check_camera
import timeout_decorator
from config import *
from cv_ImgAddText import *
import Serial_Servo_Running as SSR
import signal
import PWMServo

print('''
**********************************************************
*****巡线：通过摄像头检测黑线，使机器人沿着黑线运动*******
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

go_straight = 'go'
turn_left   = 'turn_right_slowly'
turn_right  = 'turn_left_slowly'
ori_width  =  int(4*160)#原始图像640x480
ori_height =  int(3*160)

line_color     = (255, 0, 0)#图像显示时，画出的线框颜色
line_thickness = 2         #图像显示时，画出的线框的粗细

resolution = str(ori_width) + "x" + str(ori_height)

class Point(object):
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Line(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

def GetCrossAngle(l1, l2):
    '''
    求两直线之间的夹角
    :param l1:
    :param l2:
    :return:
    '''
    arr_0 = np.array([(l1.p2.x - l1.p1.x), (l1.p2.y - l1.p1.y)])
    arr_1 = np.array([(l2.p2.x - l2.p1.x), (l2.p2.y - l2.p1.y)])
    cos_value = (float(arr_0.dot(arr_1)) / (np.sqrt(arr_0.dot(arr_0)) * np.sqrt(arr_1.dot(arr_1))))   # 注意转成浮点数运算
    return np.arccos(cos_value) * (180/np.pi)

#映射函数
def leMap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

#画圈，参数（要显示文字的图像，x坐标，y坐标，半径， 处理图像的宽度， 处理图像的高度， 颜色（可不填）， 大小（可不填））
def picture_circle(orgimage, x, y, r, resize_w, resize_h, l_c = line_color, l_t = line_thickness):
    global ori_width
    global ori_height
    
    x = int(leMap(x, 0, resize_w,  0, ori_width))
    y = int(leMap(y, 0, resize_h,  0, ori_height))
    r = int(leMap(r, 0, resize_w,  0, ori_width))   
    cv2.circle(orgimage, (x, y), r, l_c, l_t)

#检测并返回最大面积
def getAreaMaxContour(contours,area=1):
        contour_area_max = 0
        area_max_contour = None

        for c in contours :
            contour_area_temp = math.fabs(cv2.contourArea(c))
            if contour_area_temp > contour_area_max : 
                contour_area_max = contour_area_temp
                if contour_area_temp > area:#面积大于1
                    area_max_contour = c
        return area_max_contour

@timeout_decorator.timeout(0.5, use_signals=False)
def Camera_isOpened():
    global stream, cap
    cap = cv2.VideoCapture(stream) 

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

# 显示图像线程
th1 = threading.Thread(target=get_image)
th1.setDaemon(True)     # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
th1.start()

roi = [ # [ROI, weight]
        (0,  40,  0, 160, 0), 
        (40, 80,  0, 160, 0.2), 
        (80, 120,  0, 160, 0.8)
       ]

angle = 0
get_line = False
centerX = 80
def Tracing(orgimage, r_w, r_h, r = roi, l_c = line_color, l_t = line_thickness):
    global ori_width, ori_height
    global img_center_x, img_center_y
    global deflection_angle, angle
    global get_line, centerX
    #图像缩小，加快处理速度
    orgframe = cv2.resize(orgimage, (r_w, r_h), interpolation = cv2.INTER_LINEAR)
    
    Frame = cv2.GaussianBlur(orgframe, (3, 3), 0)
    Frame = cv2.cvtColor(Frame, cv2.COLOR_BGR2LAB) #将图像转换到LAB空间
    Frame = cv2.inRange(Frame, color_range['black'][0], color_range['black'][1]) #根据hsv值对图片进行二值化 
    opened = cv2.morphologyEx(Frame, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))#开运算
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))#闭运算
           
    centroid_x_sum = 0
    area_sum = 0
    n = 0
    weight_sum = 0
    center_ = []
    max_area = 0
    for r in roi:
        n += 1
        blobs = closed[r[0]:r[1], r[2]:r[3]]
        cnts = cv2.findContours(blobs , cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)[-2]#找出所有轮廓
        cnt_large  = getAreaMaxContour(cnts)#找到最大面积的轮廓
        if cnt_large is not None:
            rect = cv2.minAreaRect(cnt_large)#最小外接矩形
            box = np.int0(cv2.boxPoints(rect))#最小外接矩形的四个顶点
            box[0, 1], box[1, 1], box[2, 1], box[3, 1] = box[0, 1] + (n - 1)*r_w/4, box[1, 1] + (n - 1)*r_w/4, box[2, 1] + (n - 1)*r_w/4, box[3, 1] + (n - 1)*r_w/4
            box[1, 0] = int(leMap(box[1, 0], 0, r_w, 0, ori_width))
            box[1, 1] = int(leMap(box[1, 1], 0, r_h, 0, ori_height))
            box[3, 0] = int(leMap(box[3, 0], 0, r_w, 0, ori_width))
            box[3, 1] = int(leMap(box[3, 1], 0, r_h, 0, ori_height))
            box[0, 0] = int(leMap(box[0, 0], 0, r_w, 0, ori_width))
            box[0, 1] = int(leMap(box[0, 1], 0, r_h, 0, ori_height))
            box[2, 0] = int(leMap(box[2, 0], 0, r_w, 0, ori_width))
            box[2, 1] = int(leMap(box[2, 1], 0, r_h, 0, ori_height))
            pt1_x, pt1_y = box[0, 0], box[0, 1]
            pt3_x, pt3_y = box[2, 0], box[2, 1]
            area = cv2.contourArea(box)
            cv2.drawContours(frame, [box], -1, (0,0,255,255), 2)#画出四个点组成的矩形            
            center_x, center_y = (pt1_x + pt3_x) / 2, (pt1_y + pt3_y) / 2#中心点
            center_.append([center_x,center_y])            
            cv2.circle(frame, (int(center_x), int(center_y)), 10, (0,0,255), -1)#画出中心点
            centroid_x_sum += center_x * r[4]
            weight_sum += r[4]

    if weight_sum is not 0:
        centerX = centroid_x_sum / weight_sum
        #print(center_x_pos)
         #框中心画十字
        #cv2.line(orgimage, (img_center_x/2, img_center_y), (int(center_x_pos), img_center_y/2), l_c, l_t)         
    get_line = True
    
state1 = 0 
def move():
    global deflection_angle, angle
    global get_line, state1, centerX
    global go_straight,turn_left,turn_right, stand
    while True:
        if get_line:
            get_line = False
            if 270 <= centerX + (320 - centerx) <= 370:
                SSR.runAction(go_straight)           
            elif centerX + (320 - centerx) > 370:
                SSR.runAction(turn_left)
            elif 0 < centerX + (320 - centerx) < 270:
                SSR.runAction(turn_right)
        else:
            time.sleep(0.01)
      
th2 = threading.Thread(target=move)
th2.setDaemon(True)     # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
th2.start()    

SSR.runAction('0')
while True:
    if orgFrame is not None and ret:
        if Running:
            t1 = cv2.getTickCount()
            img_center_x = orgFrame.shape[:2][1]
            img_center_y = orgFrame.shape[:2][0]
            frame = orgFrame.copy()
            Tracing(orgFrame, 160, 120)    
            t2 = cv2.getTickCount()
            time_r = (t2 - t1) / cv2.getTickFrequency()
            fps = 1.0/time_r
            if debug == 1:#调试模式下
                frame = cv2ImgAddText(frame, "自主巡线", 10, 10, textColor=(0, 0, 0), textSize=20)
                cv2.putText(frame, "FPS:" + str(int(fps)),
                        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)#(0, 0, 255)BGR
                cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)#显示框命名
                #cv2.moveWindow('frame', img_center_x, 100)#显示框位置
                cv2.imshow('frame', frame) #显示图像
                cv2.waitKey(1)
        else:
            time.sleep(0.01)
    else:
        time.sleep(0.01)
cv2.destroyAllWindows()
