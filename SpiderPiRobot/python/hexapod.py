#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import math
import SerialServoCmd as Servoctrl
import time
import PWMServo

# 输入腿的编号和腿的足端坐标，控制腿的运动
# leg:0~5
# position:数组，存放足端的坐标
# 运行该动作的速度
def get_angle(leg, position, speed):
    angle = []
    output = []

    C = 44.60
    F = 75.00
    T = 126.50

    factor = 180 / math.pi / 0.24

    angle.append(math.atan(position[1]/position[0]))

    L = position[1] / math.sin(angle[0])

    temp = math.pow(position[2], 2) + pow(L - C, 2)

    ft = math.sqrt(temp)

    a = math.atan(position[2] / (L - C))

    b = math.acos((math.pow(F, 2) + math.pow(ft, 2) - math.pow(T, 2)) / (2 * F * ft))

    angle.append(a + b)

    angle.append(math.acos((math.pow(ft, 2) - math.pow(F, 2) - math.pow(T, 2)) / (2 * F * T)))

    if leg < 3:
        output.append(313 + angle[0] * factor)
        output.append(500 - angle[1] * factor)
        output.append(687 - angle[2] * factor - 5)
    else:
        output.append(687 - angle[0] * factor)
        output.append(500 + angle[1] * factor)
        output.append(313 + angle[2] * factor + 5)
    for i in range(1, 4):
        Servoctrl.serial_serro_wirte_cmd(leg * 3 + i, Servoctrl.LOBOT_SERVO_MOVE_TIME_WRITE, int(output[i - 1]), speed)

# 站立姿势
def hexapod_init():
    get_angle(0, [100.0, 100.0, -70.0], 1000)
    get_angle(1, [100.0, 100.0, -70.0], 1000)
    get_angle(2, [100.0, 100.0, -70.0], 1000)
    get_angle(3, [100.0, 100.0, -70.0], 1000)
    get_angle(4, [100.0, 100.0, -70.0], 1000)
    get_angle(5, [100.0, 100.0, -70.0], 1000)
    time.sleep(1)

def camera_pos_init():
    PWMServo.setServo(1, 1500, 100)
    time.sleep(0.1)
    PWMServo.setServo(2, 1500, 100)
    time.sleep(0.1)

# 坐下姿势
def hexapod_sit():
    get_angle(0, [100.0, 100.0, 20.0], 1000)
    get_angle(1, [100.0, 100.0, 20.0], 1000)
    get_angle(2, [100.0, 100.0, 20.0], 1000)
    get_angle(3, [100.0, 100.0, 20.0], 1000)
    get_angle(4, [100.0, 100.0, 20.0], 1000)
    get_angle(5, [100.0, 100.0, 20.0], 1000)
    time.sleep(1)

def fixedPoints():
    get_angle(0, [100.0, 100.0, -70.0], 1000)
    get_angle(1, [150.0, 100.0, 70.0], 1000)
    get_angle(2, [100.0, 100.0, 70.0], 1000)
    get_angle(3, [100.0, 100.0, 70.0], 1000)
    get_angle(4, [150.0, 100.0, 70.0], 1000)
    get_angle(5, [100.0, 100.0, -70.0], 1000)
    time.sleep(1)


# angle:为正时，足端逆时针旋转
#       为负时，足端顺时针旋转
# leg：每条腿的代号，0~5
def get_point(leg, angle):
    angle = angle * math.pi / 180   # 角度制转弧度制
    R = 271.5
    RM = 232.5
    base_angle_FB = 0.9465
    base_angle_M = 0.7853

    if leg == 0:
        x = R * math.cos(base_angle_FB + angle) - 58.5
        y = R * math.sin(base_angle_FB + angle) - 120.0
    elif leg == 1:
        x = RM * math.cos(base_angle_M + angle) - 64.70
        y = RM * math.sin(base_angle_M + angle) - 64.70
    elif leg == 2:
        x = R * math.sin(base_angle_FB - angle) - 120.0
        y = R * math.cos(base_angle_FB - angle) - 58.5
    elif leg == 3:
        x = R * math.cos(base_angle_FB - angle) - 58.5
        y = R * math.sin(base_angle_FB - angle) - 120.0
    elif leg == 4:
        x = RM * math.cos(base_angle_M - angle) - 64.70
        y = RM * math.sin(base_angle_M - angle) - 64.70
    elif leg == 5:
        x = R * math.sin(base_angle_FB + angle) - 120.0
        y = R * math.cos(base_angle_FB + angle) - 58.5
    else:
        x = 100
        y = 100
    return [x, y, -70]

# angle：为正时，右转
#        为负时，左转
# 一个完整的转向周期所旋转的角度是angle*2
# 所以检测到的角度要先除以2再传入
# speed：完成转向所用的毫秒数，最快建议不要小于100ms
def turn(angle, speed):
    lift = (100, 100, -40)
    if angle >= 23:
        angle = 23
        # print('R')
    elif  angle <= -23:
        angle = -23
        # print('L')

    leg0 = get_point(0, angle)
    leg1 = get_point(1, -angle)
    leg2 = get_point(1, angle)
    leg3 = get_point(3, -angle)
    leg4 = get_point(4, angle)
    leg5 = get_point(5, -angle)

    get_angle(0, leg0, 2 * speed)
    get_angle(1, lift, speed)
    get_angle(2, leg2, 2 * speed)
    get_angle(3, lift, speed)
    get_angle(4, leg4, 2 * speed)
    get_angle(5, lift, speed)
    time.sleep(speed * 0.001)

    get_angle(1, leg1, speed)
    get_angle(3, leg3, speed)
    get_angle(5, leg5, speed)
    time.sleep(speed * 0.001)

    leg0 = get_point(0, -angle)
    leg1 = get_point(1, angle)
    leg2 = get_point(1, -angle)
    leg3 = get_point(3, angle)
    leg4 = get_point(4, -angle)
    leg5 = get_point(5, angle)
    
    get_angle(0, lift, speed)
    get_angle(1, leg1, 2 * speed)
    get_angle(2, lift, speed)
    get_angle(3, leg3, 2 * speed)
    get_angle(4, lift, speed)
    get_angle(5, leg5, 2 * speed)
    time.sleep(speed * 0.001)
    
    get_angle(0, leg0, speed)
    get_angle(2, leg2, speed)
    get_angle(4, leg4, speed)
    time.sleep(speed * 0.001)

if __name__ == '__main__':
    hexapod_init()
    time.sleep(1)
    turn(2, 200)
    turn(-10, 200)
