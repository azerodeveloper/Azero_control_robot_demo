#!/usr/bin/python3
#coding=utf8
import cv2
import numpy as np
import time
import math
import threading
from lab_conf import color_range
import timeout_decorator
import check_camera

debug = True
Running = True

#摄像头默认分辨率640x480,处理图像时会相应的缩小图像进行处理，这样可以加快运行速度
#缩小时保持比例4：3,且缩小后的分辨率应该是整数
c = 80
width, height = c*4, c*3

orgFrame = None
ret = False

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

th1 = threading.Thread(target = get_image)
th1.setDaemon(True)
th1.start()

range_rgb = {'red': (0, 0, 255),
              'blue': (255, 0,0),
              'green': (0, 255, 0),
              }

cv2.namedWindow('lab_frame')    
cv2.namedWindow('orgframe')
cv2.namedWindow('red')
cv2.namedWindow('green')
cv2.namedWindow('blue')
cv2.moveWindow('lab_frame',0, 100)   
cv2.moveWindow('red', width + 125, 100)
cv2.moveWindow('green', width + 125, 100 + height + 75)
cv2.moveWindow('blue', width + 125, 100 + 2*(height + 75))
cv2.moveWindow('orgframe', 2*(width + 125), 100)

while True:     
  if orgFrame is not None and ret:
    t1 = cv2.getTickCount()
    orgframe = cv2.resize(orgFrame, (width, height), interpolation = cv2.INTER_CUBIC) #将图片缩放     
    Gauss_frame = cv2.GaussianBlur(orgframe, (7, 7), 0)#高斯模糊
    
    #将图片转换到LAB空间
    lab_frame = cv2.cvtColor(Gauss_frame, cv2.COLOR_BGR2LAB)    
    cv2.imshow('lab_frame', lab_frame) 
   
    max_area = 0   
    for i in color_range:
        if i != 'black' and i != 'white':
            mask_frame= cv2.inRange(lab_frame, color_range[i][0], color_range[i][1])#对原图像和掩模进行位运算
            cv2.imshow(i, mask_frame)
            opened = cv2.morphologyEx(mask_frame, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))#开运算
            closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))#闭运算
            contours  = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]#找出轮廓
            areaMaxContour, area_max = getAreaMaxContour(contours)#找出最大轮廓
            if areaMaxContour is not None:
                if area_max > max_area:#找最大面积
                    max_area = area_max
                    color_max = i
                    areaMaxContour_max = areaMaxContour
    if max_area != 0:
        ((centerX, centerY), rad) = cv2.minEnclosingCircle(areaMaxContour_max)  # 获取最小外接圆
        centerX, centerY, rad = int(centerX), int(centerY), int(rad)#获取圆心，半径
        Color_BGR = range_rgb[color_max] 
        cv2.circle(orgframe, (centerX, centerY), rad, Color_BGR, 2)#画圆                             
    else:
        color_max = 'None'
        Color_BGR = (0, 0, 0)
    t2 = cv2.getTickCount()
    time_r = (t2 - t1) / cv2.getTickFrequency()               
    fps = 1.0/time_r
    cv2.putText(orgframe, "FPS:" + str(int(fps)),
            (10, orgframe.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)   #(0, 0, 255)BGR 
    cv2.putText(orgframe, "Color: " + color_max, (10, orgframe.shape[0] - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, Color_BGR, 2)
    cv2.imshow("orgframe", orgframe)
    cv2.waitKey(1)
  else:
    time.sleep(0.01)
cap.release()
cv2.destroyAllWindows()
