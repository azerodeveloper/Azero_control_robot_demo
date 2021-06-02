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

target_color = "green"
debug = True
Running = True

#摄像头默认分辨率640x480,处理图像时会相应的缩小图像进行处理，这样可以加快运行速度
#缩小时保持比例4：3,且缩小后的分辨率应该是整数
c = 80
width, height = c*4, c*3

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
cv2.namedWindow('green')
cv2.moveWindow('lab_frame',0, 100)
cv2.moveWindow('green', width + 125, 100)
cv2.moveWindow('orgframe', 2*(width + 125), 100)

while True:
  if orgFrame is not None and ret:
    t1 = cv2.getTickCount()
    orgframe = cv2.resize(orgFrame, (width,height), interpolation = cv2.INTER_CUBIC) #将图片缩放到 320*240         
    Gauss_frame = cv2.GaussianBlur(orgframe, (7,7), 0)
    
     #将图片转换到LAB空间
    lab_frame = cv2.cvtColor(Gauss_frame, cv2.COLOR_BGR2LAB)    
    cv2.imshow('lab_frame', lab_frame) 

    mask_frame = cv2.inRange(lab_frame, color_range[target_color][0], color_range[target_color][1]) #根据hsv值对图片进行二值化
    cv2.imshow('green', mask_frame)
    frame = cv2.morphologyEx(mask_frame, cv2.MORPH_CLOSE, (3,3))
    
    contours = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2] #找出所有外轮廓
    areaMaxContour = getAreaMaxContour(contours) #找到最大的轮廓    
    if areaMaxContour is not None:  #有找到最大面积
        (centerX, centerY), radius = cv2.minEnclosingCircle(areaMaxContour) #获取最小外接圆
        cv2.circle(orgframe, (int(centerX), int(centerY)), int(radius), range_rgb[target_color], 2)
    t2 = cv2.getTickCount()
    time_r = (t2 - t1) / cv2.getTickFrequency()               
    fps = 1.0/time_r
    cv2.putText(orgframe, "FPS:" + str(int(fps)),
            (10, orgframe.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)   #(0, 0, 255)BGR 
    cv2.imshow("orgframe", orgframe)
    cv2.waitKey(1)
  else:
    time.sleep(0.01)     
cap.release()
cv2.destroyAllWindows()
