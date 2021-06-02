import Serial_Servo_Running as SSR
from time import sleep

if __name__ == '__main__':
    print("34")
    SSR.run_ActionGroup("34", 1)
    sleep(2)
    print("0")
    SSR.run_ActionGroup("0", 1)
    
