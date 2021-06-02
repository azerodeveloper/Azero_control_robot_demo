import paho.mqtt.client as mqtt
import ssl
import json as js
import threading
from time import sleep
import os
import Serial_Servo_Running as SSR
#sleep(20)

# HOST = "ge78gifrc2f8x5.iot.bj.soundai.cn"
HOST = "kwk9n88tnxjzs2.iot.bj.soundai.cn"

# 6m9vz86xe8nvhk
PORT = 8883

continuous_action = {
    "Forward_Move" : "1",
    "Backward_Move" : "2",
    "Left_Move" : "3",
    "Right_Move" : "4",
    "forward": "1",
    "backward" : "2",
}
onetime_acton = {
    "Stop_Move" : "0",
    "Wave_Hand" : "9",
    "Bow" : "10",
    "Cheer" : "15",
    "Wing_Chun" : "36" ,
    "Forward_Boxing" : "34" ,
    "Crouch" : "14" ,
    "Sit_Up" : "8" ,
    "Push_Up" : "7" ,
    "Right_Hook" : "31",
    "Left_Hook" : "30",
    "Right_Slide" : "12",
    "Left_Slide" : "11",
    "welcome" : "10",
    "seeyou" : "9",
    "dance" : "204",
    "exercise" : "205",
    "wushu" : "209",
    "trun_left": "3",
    "trun_right": "4",
    "" : "0"
}


g_sign = False
son_sign = False

#https://ge78gifrc2f8x5.iot.bj.soundai.cn:8443/things/${thingName}/shadow
#topic = "$pub/6m9vz86xe8nvhk/$azero/things/ToniPiTest/shadow/#"
# topic = "$pub/ge78gifrc2f8x5/$azero/things/ToniPiTest/shadow/#"
topic = "$pub/kwk9n88tnxjzs2/$azero/things/TonyPi/shadow/#"

g_sleeptime = 0.2
g_c_pwd = os.path.dirname(os.path.abspath(__file__))

# 直行或者左转过程中的计数
g_cruise_times = 0
# 直行或者左转的标志：直行：False；左转：True
g_cruise_sign = False
# 停止标志
g_stop_sign = False


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    print("topic:" + topic)
    res = client.subscribe(topic)
    print(res)


def boxingAction():
    SSR.runAction("32")
    #sleep(1)
    SSR.runAction("33")
    #sleep(1)
    #SSR.run_Action("31")
    #SSR.run_Action("32")
    #SSR.run_Action("33")
    #SSR.run_Action("30")

def action_handle(action = 'stop_iot'):
    global g_sign
    global son_sign
    global g_cruise_times
    run_count=0
    print("action_handle : " + str(g_sign))
    if action in onetime_acton:
        print("onetime_acton:" + action)
        SSR.runAction(onetime_acton[action])
    elif action in continuous_action:
        son_sign = True
        while True:
            # print("cruise_times:" + str(g_cruise_times))
            print("continuous_action:" + action)
            sleep(0.1)
            if g_sign == False:
                son_sign = False
                break
            if g_cruise_times:
                if run_count >= g_cruise_times:
                    SSR.runAction(onetime_acton["Stop_Move"])
                    g_cruise_times=0
                    g_sign == False
                    son_sign = False
                    break
            SSR.runAction(continuous_action[action])
            run_count += 1

    else:
        SSR.runAction("0")
        print("Action stop")

def on_message(client, userdata, msg):
    global g_sign
    global son_sign
    global g_cruise_times
    msg_json = msg.payload
    root = js.loads(msg_json)
    print(root)
    state = ""
    command = ""
# not for python3  :  if root.has_key('state'):
    if 'state' in root.keys():
        state = root['state']
    if 'value' in state.keys():
        command = state['value']
    elif 'powerState' in state.keys():
        command = state['powerState']
        if 'step' in state.keys():
            g_cruise_times = int(state['step'])
    else:
        print("====== receive cmd error !!!")

    if state and command:
        print(state)
        print(command)
        if son_sign == True:
            g_sign = False
            while son_sign == True:
                sleep(g_sleeptime)
        t = threading.Thread(target=action_handle,args=(command,))
        t.setDaemon(True)
        g_sign = True
        t.start()
    else:
        print("====== receive cmd error !!! ignore")
def client_loop():
    client = mqtt.Client(None, True, None)
    client.on_connect = on_connect
    client.on_message = on_message
#    client.tls_set(g_c_pwd + "/pem/AzeroRootCA1.pem", g_c_pwd + "/pem/600f86f0a0-cert.pem", g_c_pwd + "/pem/600f86f0a0-private.key.pem", tls_version=ssl.PROTOCOL_TLSv1_2)
    # client.tls_set(g_c_pwd + "/welcome_pem/AzeroRootCA1.pem", g_c_pwd + "/welcome_pem/3c2b8cd582-cert.pem", g_c_pwd + "/welcome_pem/3c2b8cd582-private.key.pem", tls_version=ssl.PROTOCOL_TLSv1_2)
    client.tls_set(g_c_pwd + "/pem_hu/AzeroRootCA1.pem", g_c_pwd + "/pem_hu/bc68232530-cert.pem", g_c_pwd + "/pem_hu/bc68232530-private.key.pem", tls_version=ssl.PROTOCOL_TLSv1_2)
    client.connect(HOST, PORT, 60)

    client.loop_forever()

if __name__ == '__main__':
    client_loop()
