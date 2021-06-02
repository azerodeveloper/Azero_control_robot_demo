import paho.mqtt.client as mqtt
import ssl
import json as js

import threading
from time import sleep
import os

# import Serial_Servo_Running as SSR

HOST = "mamsxooonm3wcq.iot.bj.soundai.cn"
PORT = 8883

continuous_action = {
    "forward_iot" : "1",
    "back_iot" : "2",
    "turnleft_iot" : "3",
    "turnright_iot" : "4"
}

onetime_acton = {
    "stop_iot" : "0"
}
g_sign = False
son_sign = False

topic = "$pub/mamsxooonm3wcq/$azero/things/SpiderPiRobot/shadow/#"
g_sleeptime = 0.2
g_c_pwd = os.path.dirname(os.path.abspath(__file__))

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    print("topic:" + topic)
    res = client.subscribe(topic)
    print(res)

def action_handle(action = 'stop'):
    global g_sign
    global son_sign
    print("action_handle : " + str(g_sign))
    if action in onetime_acton:
        print("onetime_acton:" + onetime_acton[action])
        # SSR.run_ActionGroup(onetime_acton[action], 1)
    elif action in continuous_action:
        son_sign = True
        while True:
            print("continuous_action:" + continuous_action[action])
            sleep(g_sleeptime)
            if g_sign == False:
                son_sign = False
                break
            # SSR.run_ActionGroup(continuous_action[action], 1)
            
    else:
        # SSR.run_ActionGroup("0", 1)
        print("Action stop")

t = threading.Thread(target=action_handle,args=('stop',))

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

if __name__ == '__main__':
    client_loop()
