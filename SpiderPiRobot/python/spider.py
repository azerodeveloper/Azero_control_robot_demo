import paho.mqtt.client as mqtt
import ssl
import json as js
import threading
from time import sleep
import os
import Serial_Servo_Running as SSR
import hcsr04
import hexapod

HOST = "mamsxooonm3wcq.iot.bj.soundai.cn"
PORT = 8883

continuous_action = {
    "cruise_iot" : "",
    "forward_iot" : "1",
    "back_iot" : "2",
    "turnleft_iot" : "3",
    "turnright_iot" : "4",
    "fight_iot" : "10"
}

onetime_acton = {
    "stop_iot" : "0"
}
g_sign = False
son_sign = False

topic = "$pub/mamsxooonm3wcq/$azero/things/SpiderPiRobot/shadow/#"
g_sleeptime = 0.2
g_c_pwd = os.path.dirname(os.path.abspath(__file__))

# 直行或者左转过程中的计数
g_cruise_times = 0
# 直行或者左转的标志：直行：False；左转：True
g_cruise_sign = False
# 停止标志
g_stop_sign = False

GPIO_TRIG = 12   # 超声波trig引脚对应的IO号
GPIO_ECHO = 16   # 超声波echo引脚对应的IO号
sonar = hcsr04.Measurement(GPIO_TRIG, GPIO_ECHO)

def cruiseAction():
    global g_cruise_sign
    global g_cruise_times
    if g_cruise_sign == False:
        SSR.run_ActionGroup(continuous_action["forward_iot"], 1)
        # 向前进6次
        if g_cruise_times == 6:
            g_cruise_sign = True
            g_cruise_times = 0
            sleep(g_sleeptime)
            SSR.run_ActionGroup(continuous_action["fight_iot"], 1)
    else:
        # 向左转4次（掉头）
        if g_cruise_times == 4:
            g_cruise_sign = False
            g_cruise_times = 0
        SSR.run_ActionGroup(continuous_action["turnleft_iot"], 1)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    print("topic:" + topic)
    res = client.subscribe(topic)
    print(res)

def action_handle(action = 'stop_iot'):
    global g_sign
    global son_sign
    global g_cruise_times
    print("action_handle : " + str(g_sign))
    if action in onetime_acton:
        print("onetime_acton:" + action)
        SSR.run_ActionGroup(onetime_acton[action], 1)
    elif action in continuous_action:
        son_sign = True
        # 统计循环次数
        g_cruise_times = 0
        while True:
            # print("cruise_times:" + str(g_cruise_times))
            print("continuous_action:" + action)
            sleep(g_sleeptime)
            if g_sign == False:
                son_sign = False
                break
            # 巡航指令
            if action == "cruise_iot":
                g_cruise_times += 1
                cruiseAction()
            else:
                SSR.run_ActionGroup(continuous_action[action], 1)
            # 向前运动时若停止标志为真则等待
            if action == "forward_iot" or action == "cruise_iot":
                print("stop_sign:" + str(g_stop_sign))
                while g_stop_sign:
                    sleep(g_sleeptime)
    else:
        SSR.run_ActionGroup("0", 1)
        print("Action stop")

def on_message(client, userdata, msg):
    global g_sign
    global son_sign
    msg_json = msg.payload
    root = js.loads(msg_json)
    print(root)
    state = root['state']
    command = state['value']
    print(command)
    if son_sign == True:
        g_sign = False
        while son_sign == True:
            sleep(g_sleeptime)
    t = threading.Thread(target=action_handle,args=(command,))
    t.setDaemon(True)
    g_sign = True
    t.start()

def client_loop():
    client = mqtt.Client(None, True, None)
    client.on_connect = on_connect
    client.on_message = on_message
    client.tls_set(g_c_pwd + "/pem/f6c0301439-AzeroRootCA.pem", g_c_pwd + "/pem/f6c0301439-cert.pem", g_c_pwd + "/pem/f6c0301439-private.key.pem", tls_version=ssl.PROTOCOL_TLSv1_2)
    client.connect(HOST, PORT, 60)

    client.loop_forever()

def sonar_distance():
    print ("开启超声波避障功能")
    global g_stop_sign
    while True:
        sleep(g_sleeptime)
        try:
            distance = sonar.distance_metric(sonar.raw_distance(2, 0.08))
            if distance > 100.0 or distance == 0:
                g_stop_sign = False
            else:
                g_stop_sign = True
                hexapod.turn(20, 200)
                hexapod.turn(20, 200)
                hexapod.turn(20, 200)
                g_stop_sign = False
        except:
            pass

if __name__ == '__main__':
    sonar_t = threading.Thread(target=sonar_distance)
    sonar_t.setDaemon(True)
    sonar_t.start()
    client_loop()
