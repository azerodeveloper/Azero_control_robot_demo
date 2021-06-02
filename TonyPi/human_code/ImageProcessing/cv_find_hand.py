#!/usr/bin/python3
#coding:utf8
import cv2
import numpy as np
import time
import math
import threading
import timeout_decorator
import check_camera

debug = True
Running = True

#摄像头默认分辨率640x480,处理图像时会相应的缩小图像进行处理，这样可以加快运行速度
#缩小时保持比例4：3,且缩小后的分辨率应该是整数
c = 80
width, height = c*4, c*3

class Point(object):#一个坐标点
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Line(object):#一条线
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

def two_distance(start, end):
    """
    计算两点的距离
    :param start: 开始点
    :param end: 结束点
    :return: 返回两点之间的距离
    """
    s_x = start[0]
    s_y = start[1]
    e_x = end[0]
    e_y = end[1]
    x = s_x - e_x
    y = s_y - e_y
    return math.sqrt((x**2)+(y**2))
 
 
cv2.namedWindow('YCC_frame')    
cv2.namedWindow('Cr')
cv2.namedWindow('Cr_inrange')
cv2.namedWindow('opend')
cv2.namedWindow('orgframe')
cv2.moveWindow('YCC_frame',0, 100)
cv2.moveWindow('Cr',0, 100 + height + 75)
cv2.moveWindow('Cr_inrange', (width + 125), 100)    
cv2.moveWindow('opend', (width + 125), 100 + height + 75)
cv2.moveWindow('orgframe', 2*(width + 125), 100)
def image_process(image):#hsv
    '''
    # 光线影响，请修改 cb的范围
    # 正常黄种人的Cr分量大约在140~160之间
    识别肤色
    :param image: 图像
    :return: 识别后的二值图像
    '''
    YCC_frame = cv2.cvtColor(image, cv2.COLOR_BGR2YCR_CB)  # 将图片转化为YCrCb
    cv2.imshow('YCC_frame', YCC_frame) 
    Y, Cr, Cb = cv2.split(YCC_frame)  # 分割YCrCb
    cv2.imshow('Cr', Cr)
    Cr_inrange = cv2.inRange(Cr, 132, 175)
    cv2.imshow('Cr_inrange', Cr_inrange)
    # 开运算，去除噪点
    open_element = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opend = cv2.morphologyEx(Cr_inrange, cv2.MORPH_OPEN, open_element)
    cv2.imshow('opend', opend)
    return opend

def get_defects_far(defects, contours, img):
    '''
    获取凸包中最远的点
    '''
    if defects is None and contours is None:
        return None
    far_list = []
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(contours[s][0])
        end = tuple(contours[e][0])
        far = tuple(contours[f][0])
        # 求两点之间的距离
        a = two_distance(start, end)
        b = two_distance(start, far)
        c = two_distance(end, far)
        # print('a=', a)
        # print('b= ', b)
        # print('c= ', c)
        # 求出手指之间的角度
        angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180 / math.pi
        # 手指之间的角度一般不会大于100度
        # 小于90度
        if angle <= 75:  # 90:
            # cv.circle(img, far, 10, [0, 0, 255], 1)
            far_list.append(far)
    return far_list

def get_max_coutour(cou, max_area):
    '''
    找出最大的轮廓
    根据面积来计算，找到最大后，判断是否小于最小面积，如果小于侧放弃
    :param cou: 轮廓
    :return: 返回最大轮廓
    '''
    max_coutours = 0
    r_c = None
    if len(cou) < 1:
        return None
    else:
        for c in cou:
            # 计算面积
            temp_coutours = math.fabs(cv2.contourArea(c))
            if temp_coutours > max_coutours:
                max_coutours = temp_coutours
                cc = c
        # 判断所有轮廓中最大的面积
        if max_coutours > max_area:
            r_c = cc
        return r_c

def find_contours(binary, max_area):
    '''
    mode  提取模式.
    CV_RETR_EXTERNAL - 只提取最外层的轮廓
    CV_RETR_LIST - 提取所有轮廓，并且放置在 list 中
    CV_RETR_CCOMP - 提取所有轮廓，并且将其组织为两层的 hierarchy: 顶层为连通域的外围边界，次层为洞的内层边界。
    CV_RETR_TREE - 提取所有轮廓，并且重构嵌套轮廓的全部 hierarchy
    method  逼近方法 (对所有节点, 不包括使用内部逼近的 CV_RETR_RUNS).
    CV_CHAIN_CODE - Freeman 链码的输出轮廓. 其它方法输出多边形(定点序列).
    CV_CHAIN_APPROX_NONE - 将所有点由链码形式翻译(转化）为点序列形式
    CV_CHAIN_APPROX_SIMPLE - 压缩水平、垂直和对角分割，即函数只保留末端的象素点;
    CV_CHAIN_APPROX_TC89_L1,
    CV_CHAIN_APPROX_TC89_KCOS - 应用 Teh-Chin 链逼近算法. CV_LINK_RUNS - 通过连接为 1 的水平碎片使用完全不同的轮廓提取算法
    :param binary: 传入的二值图像
    :return: 返回最大轮廓
    '''
    # 找出所有轮廓
    contours = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
    # 返回最大轮廓
    return get_max_coutour(contours, max_area)

def get_hand_number(binary_image, rgb_image):
    '''
    返回手指的个数
    :param binary_image:
    :param rgb_image:
    :return:
    '''
    # # 2、找出手指尖的位置
    # # 查找轮廓，返回最大轮廓
    x = 0
    y = 0
    contours = find_contours(binary_image, 1000)
    coord_list = []

    if contours is not None:
        # 周长  0.035 根据识别情况修改，识别越好，越小
        epsilon = 0.025 * cv2.arcLength(contours, True)
        # 轮廓相似
        approx = cv2.approxPolyDP(contours, epsilon, True)
        #cv2.approxPolyDP()的参数2(epsilon)是一个距离值，表示多边形的轮廓接近实际轮廓的程度，值越小，越精确；参数3表示是否闭合
        cv2.polylines(rgb_image, [approx], True, (0, 255, 0), 1)#画多边形

        if approx.shape[0] >= 3:  # 有三个点以上#多边形最小为三角形，三角形需要三个点
            approx_list = []
            for j in range(approx.shape[0]):#将多边形所有的点储存在一个列表里
                # cv2.circle(rgb_image, (approx[j][0][0],approx[j][0][1]), 5, [255, 0, 0], -1)
                approx_list.append(approx[j][0])
            approx_list.append(approx[0][0])    # 在末尾添加第一个点
            approx_list.append(approx[1][0])    # 在末尾添加第二个点

            for i in range(1, len(approx_list) - 1):
                p1 = Point(approx_list[i - 1][0], approx_list[i - 1][1])    # 声明一个点
                p2 = Point(approx_list[i][0], approx_list[i][1])
                p3 = Point(approx_list[i + 1][0], approx_list[i + 1][1])
                line1 = Line(p1, p2)    # 声明一条直线
                line2 = Line(p2, p3)
                angle = GetCrossAngle(line1, line2)     # 获取两条直线的夹角
                angle = 180 - angle     #
                # print angle
                if angle < 42:  # 求出两线相交的角度，并小于37度的
                    #cv2.circle(rgb_image, tuple(approx_list[i]), 5, [255, 0, 0], -1)
                    coord_list.append(tuple(approx_list[i]))
        ##############################################################################
        # 去除手指间的点
        # 1、获取凸包缺陷点，最远点点
        # cv.drawContours(rgb_image, contours, -1, (255, 0, 0), 1)
        hull = cv2.convexHull(contours, returnPoints=False)
        # 找凸包缺陷点 。返回的数据， 【起点，终点， 最远的点， 到最远点的近似距离】
        defects = cv2.convexityDefects(contours, hull)
        # 返回手指间的点
        hand_coord = get_defects_far(defects, contours, rgb_image)
        # print 'h', hand_coord
        # print 'c', coord_list
        # 2、从coord_list 去除最远点
        new_hand_list = []  # 获取最终的手指间坐标
        alike_flag = False
        if len(coord_list) > 0:
            for l in range(len(coord_list)):
                for k in range(len(hand_coord)):
                    if (-10 <= coord_list[l][0] - hand_coord[k][0] <= 10 and
                            -10 <= coord_list[l][1] - hand_coord[k][1] <= 10):    # 最比较X,Y轴, 相近的去除
                        alike_flag = True
                        break   #
                if alike_flag is False:
                    new_hand_list.append(coord_list[l])
                alike_flag = False
            # print new_hand_list
            # 获取指尖的坐标列表并显示
            for i in new_hand_list:
                cv2.circle(rgb_image, tuple(i), 5, [0, 0, 100], -1)
        if new_hand_list is []:
            return 0
        else:
            return len(new_hand_list)
    else:
        return 0

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


num = []
num_mean = 0
while True:               
  if orgFrame is not None and ret:
    t1 = cv2.getTickCount()
    orgframe = cv2.resize(orgFrame, (width,height), interpolation = cv2.INTER_CUBIC) #将图片缩放
    frame = orgframe
    binary = image_process(frame)#处理图像
    hand_num = get_hand_number(binary, frame)#获取手指个数
    num.append(hand_num)
    if len(num) == 10:
        num_mean = int(round(np.mean(num)))
        num = num[1:]
    t2 = cv2.getTickCount()
    time_r = (t2 - t1) / cv2.getTickFrequency()               
    fps = 1.0/time_r
    cv2.putText(orgframe, "FPS:" + str(int(fps)),
            (10, orgframe.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)   #(0, 0, 255)BGR 
    cv2.putText(orgframe, "Current:" + str(num_mean),
            (10, orgframe.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)#显示当前检测到的手指个数，(0, 0, 255)BGR
    cv2.imshow("orgframe", orgframe)
    cv2.waitKey(1)
  else:
    time.sleep(0.01)     
cap.release()
cv2.destroyAllWindows()
