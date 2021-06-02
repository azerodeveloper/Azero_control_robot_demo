#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import cv2
import numpy as np
import time
import threading
import math
from lab_conf import *
import timeout_decorator
import check_camera

debug = True
Running = True

#摄像头默认分辨率640x480,处理图像时会相应的缩小图像进行处理，这样可以加快运行速度
#缩小时保持比例4：3,且缩小后的分辨率应该是整数
c = 80
width, height = c*4, c*3
ori_width  =  int(4*160)#原始图像640x480
ori_height =  int(3*160)

line_color     = (255, 0, 0)#图像显示时，画出的线框颜色
line_thickness = 2         #图像显示时，画出的线框的粗细

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
    
def get_image():
    global orgFrame
    global ret
    global Running
    global stream, cap
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
        (0,               int(height/3),   0, width, 0.5), 
        (int(height/3),   int(2*height/3), 0, width, 0.3), 
        (int(2*height/3), height,          0, width, 0.2)
       ]

cv2.namedWindow('lab_frame')
cv2.namedWindow('threshold')
cv2.namedWindow('opened')
cv2.namedWindow('closed')
cv2.namedWindow('blobs1')
cv2.namedWindow('blobs2')
cv2.namedWindow('blobs3')
cv2.namedWindow('orgframe')
cv2.moveWindow('lab_frame',0, 100)
cv2.moveWindow('threshold',width + 30, 70)
cv2.moveWindow('opened', width + 30, (70 + height + 75)) 
cv2.moveWindow('closed', width + 30, 70 + 2*(height + 75))    
cv2.moveWindow('blobs1', 3*(width) - 20, 100)
cv2.moveWindow('blobs2', 3*(width) - 20, 100 + height)
cv2.moveWindow('blobs3', 3*(width) - 20, 100 + 2*(height))
cv2.moveWindow('orgframe', 5*(width), 100)#显示框位置
while True:
    if orgFrame is not None and ret:       
        if Running:
            t1 = cv2.getTickCount()
            orgframe = orgFrame.copy()
            frame = cv2.resize(orgframe, (width, height), interpolation = cv2.INTER_LINEAR)
 
            Gauss_frame = cv2.GaussianBlur(frame, (3, 3), 0)
            
            lab_frame = cv2.cvtColor(Gauss_frame, cv2.COLOR_BGR2LAB) #将图像转换到LAB空间
            cv2.imshow('lab_frame',lab_frame)
            
            Imask = cv2.inRange(lab_frame, color_range['black'][0], color_range['black'][1]) #根据hsv值对图片进行二值化
            cv2.imshow('threshold',Imask)
            
            opened = cv2.morphologyEx(Imask, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))#开运算
            cv2.imshow('opened',opened)
            
            closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))#闭运算
            cv2.imshow('closed',closed)
                      
            n = 0
            for r in roi:
                n += 1
                blobs = closed[r[0]:r[1], r[2]:r[3]]
                cv2.imshow('blobs' + str(n), blobs)
                cnts = cv2.findContours(blobs.copy() , cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)[-2]#找出所有轮廓
                cnt_large  = getAreaMaxContour(cnts)#找到最大面积的轮廓
                
                if cnt_large is not None:
                    rect = cv2.minAreaRect(cnt_large)#最小外接矩形
                    box = np.int0(cv2.boxPoints(rect))#最小外接矩形的四个顶点                    
                    box[0, 1], box[1, 1], box[2, 1], box[3, 1] = box[0, 1] + (n - 1)*width/4, box[1, 1] + (n - 1)*width/4, box[2, 1] + (n - 1)*width/4, box[3, 1] + (n - 1)*width/4
                    pt1_x, pt1_y = box[0, 0], box[0, 1]
                    pt3_x, pt3_y = box[2, 0], box[2, 1]
                    cv2.drawContours(frame, [box], -1, (0,0,255,255), 2)#画出四个点组成的矩形            
                    center_x, center_y = (pt1_x + pt3_x) / 2, (pt1_y + pt3_y) / 2#中心点                    
                    cv2.circle(frame, (int(center_x), int(center_y)), 10, (0,0,255), -1)#画出中心点
            t2 = cv2.getTickCount()
            time_r = (t2 - t1) / cv2.getTickFrequency()               
            fps = 1.0/time_r
            cv2.putText(frame, "FPS:" + str(int(fps)),
                    (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)   #(0, 0, 255)BGR                     
            cv2.imshow('orgframe', frame) #显示图像
            cv2.waitKey(1)
        else:
            time.sleep(0.01)
    else:
        time.sleep(0.01)
cv2.destroyAllWindows()
