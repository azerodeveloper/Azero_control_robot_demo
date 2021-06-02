#!/usr/bin/python3
#coding=utf8
import cv2
import time
import math
import threading
import numpy as np
from lab_conf import color_range
import timeout_decorator
import check_camera

debug = True
Running = True

#摄像头默认分辨率640x480,处理图像时会相应的缩小图像进行处理，这样可以加快运行速度
#缩小时保持比例4：3,且缩小后的分辨率应该是整数
c = 80
width, height = c*4, c*3

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

cv2.namedWindow('gray_img')    
cv2.namedWindow('img')
cv2.namedWindow('orgframe')
cv2.moveWindow('gray_img',0, 100)
cv2.moveWindow('img',width + 125, 100)
cv2.moveWindow('orgframe', 2*(width + 125), 100) 
while True:
  if orgFrame is not None and ret:
    t1 = cv2.getTickCount()
    orgframe = cv2.resize(orgFrame,(width, height), interpolation = cv2.INTER_CUBIC)
   
    #灰度图像
    gray_img = cv2.cvtColor(orgframe, cv2.COLOR_BGR2GRAY)
    cv2.imshow("gray_img", gray_img)
    
    #中值滤波
    img = cv2.medianBlur(gray_img, 11)
    cv2.imshow("img", img)
    
    #霍夫曼变化
    circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,400,param1=100,param2=30,minRadius=20,maxRadius=60)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            centerX, centerY, rad = i[0], i[1], i[2]
            cv2.circle(orgframe,(int(centerX), int(centerY)), int(rad), (255, 0, 0), 2)
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
