import requests
import json
import urllib3
urllib3.disable_warnings()

g_url = "https://mamsxooonm3wcq.iot.bj.soundai.cn:8443/things/SpiderPiRobot/shadow"
g_payload = '{"state":{"desired":{"color":"green"}}}'
g_headers = {"Content-Type":"application/json"}
g_cert = ( "./pem/f6c0301439-cert.pem", "./pem/f6c0301439-private.key.pem")

if __name__ == "__main__":
    r = requests.post(g_url, data=g_payload, headers=g_headers, verify="./CA/f6c0301439-AzeroRootCA.pem", cert=g_cert)
    print(r)