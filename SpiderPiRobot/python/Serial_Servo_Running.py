#!/usr/bin/env python3
# encoding: utf-8
import time
import os
import sqlite3 as sql
import SerialServoCmd as ssc
import config_serial_servo
import threading
from hwax import HWAX

runningAction = False
stopRunning = True
online_action_num = None
online_action_times = -1
update_ok = False
action_group_finish = True

def serial_setServo(s_id, pos, s_time):
    if pos > 1000:
        pos = 1000
    elif pos < 0:
        pos = 0
    else:
        pass
    if s_time > 30000:
        s_time = 30000
    elif s_time < 10:
        s_time = 10
    ssc.serial_serro_wirte_cmd(s_id, ssc.LOBOT_SERVO_MOVE_TIME_WRITE, pos, s_time)

def setDeviation(servoId, d):
    '''
    配置舵机偏差
    :param servoId:
    :param d:
    :return:
    '''
    global runningAction
    if servoId < 0 or servoId > 19:
        return
    if d < -200 or d > 200:
        return
    if runningAction is False:
        config_serial_servo.serial_servo_set_deviation(servoId, d)
 
def stop_servo():
    for i in range(18):
        config_serial_servo.serial_servo_stop(i+1) 

def stop_action_group():
    global stopRunning, online_action_num, online_action_times, update_ok
    update_ok = False
    stopRunning = True
    online_action_num = None
    online_action_times = -1
    time.sleep(0.1)

def action_finish():
    global action_group_finish
    return action_group_finish  

def runAction(actNum):
    '''
    运行动作组，无法发送stop停止信号
    :param actNum: 动作组名字 ， 字符串类型
    :param times:  运行次数
    :return:
    '''
    global runningAction
    global stopRunning
    global online_action_times
    if actNum is None:
        return
    hwaxNum = "/home/pi/Desktop/SpiderPiRobot/ActionGroups/" + actNum + ".hwax"
    actNum = "/home/pi/Desktop/SpiderPiRobot/ActionGroups/" + actNum + ".d6a"
    
    if os.path.exists(hwaxNum) is True:
        if runningAction is False:
            runningAction = True
            ssc.portWrite()
            hwax = HWAX(hwaxNum, ssc.serialHandle)
            hwax.reset()
            while True:
                if stopRunning is True:
                    stopRunning = False
                    print('stop')                   
                    break
                ret = hwax.next()
                if ret is None:
                    hwax.reset()
                    break
            hwax.close()
            runningAction = False

    elif os.path.exists(actNum) is True:
        if runningAction is False:
            runningAction = True
            ag = sql.connect(actNum)
            cu = ag.cursor()
            cu.execute("select * from ActionGroup")
            while True:              
                act = cu.fetchone()
                if stopRunning is True:
                    stopRunning = False
                    print('stop')                    
                    break
                if act is not None:
                    for i in range(0, len(act)-2, 1):
                        serial_setServo(i+1, act[2 + i], act[1])
                    time.sleep(float(act[1])/1000.0)
                else:   # 运行完才退出
                    break
            runningAction = False
            
            cu.close()
            ag.close()
    else:
        runningAction = False
        print("未能找到动作组文件")

def run_ActionGroup(actNum, times):
    '''
    运行动作组
    :param actNum:动作组文件名
    :param times:运行次数，次数为0时表示无限循环，无法停止
    :return:无
    '''
    global runningAction
    global stopRunning
    global action_group_finish
        
    d6aNum = "/home/pi/Desktop/SpiderPiRobot/ActionGroups/" + actNum + ".d6a"
    hwaxNum = "/home/pi/Desktop/SpiderPiRobot/ActionGroups/" + actNum + ".hwax"
    
    stopRunning = False
    if action_group_finish:        
        if times == 0:#对传入次数进行分类处理
            times = 1
            state = False
        else:
            times = abs(times)
            state = True
        if os.path.exists(hwaxNum) is True:           
            ssc.portWrite()
            hwax = HWAX(hwaxNum, ssc.serialHandle)
            hwax.reset()
            while times:
                if state:
                    times -= 1             
                if runningAction is False:                   
                    runningAction = True                   
                    while True:
                        if stopRunning is True:                            
                            runningAction = False                           
                            break
                        ret = hwax.next()
                        if ret is None:
                            runningAction = False
                            hwax.reset()
                            break
                else:                        
                    break
                    
        elif os.path.exists(d6aNum) is True: # 如果存在该动作组
            while times:
                if state:
                    times -= 1        
                ag = sql.connect(d6aNum)# 打开数据库actNum
                cu = ag.cursor()# 定义了一个游标
                cu.execute("select * from ActionGroup") # 查询
                if runningAction is False:# 没有动作组在运行
                    runningAction = True
                    while True:
                        if stopRunning is True:                                
                            runningAction = False
                            cu.close()# 关闭一个数据库链接
                            ag.close()# 游标关闭
                            break
                        act = cu.fetchone() # 返回列表中的第一项，再次使用,则返回第二项,依次下去
                        if act is not None:
                            for i in range(0, len(act)-2, 1):
                                serial_setServo(i+1, act[2 + i], act[1])
                            time.sleep(float(act[1])/1000.0)
                        else:
                            runningAction = False
                            cu.close()
                            ag.close()
                            break
                else:                    
                    break 
        else:
            runningAction = False
            print("未能找到动作组文件")

def online_thread_run_acting():
    global online_action_times, online_action_num, update_ok, action_group_finish
    while True:
        if update_ok:
            if online_action_times == 0:
                # 无限次运行                
                runAction(online_action_num)
                action_group_finish = False
            elif online_action_times > 0:
            # 有次数运行
                runAction(online_action_num)
                online_action_times -= 1    # 运行完成后，进入空载
                action_group_finish = False
                if online_action_times == 0:
                    online_action_times = -1
            else:
                # 空载
                action_group_finish = True
                time.sleep(0.01)
        else:
            action_group_finish = True
            time.sleep(0.01)
            
def start_action_thread():
    th1 = threading.Thread(target=online_thread_run_acting)
    th1.setDaemon(True)  # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
    th1.start()
    
def change_action_value(actNum, actTimes):
    global online_action_times, online_action_num, update_ok, stopRunning
    
    online_action_times = actTimes
    online_action_num = actNum
    stopRunning = False
    update_ok = True

if __name__ == '__main__':
    start_action_thread()
    change_action_value('1', 0)
    time.sleep(5)
    stop_action_group()
    run_ActionGroup('0', 1) 
    run_ActionGroup('2', 3)
    run_ActionGroup('0', 1)
