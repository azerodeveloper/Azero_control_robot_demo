#!/usr/bin/env python3
# encoding: utf-8

from time import sleep
import Serial_Servo_Running as SSR

if __name__ == "__main__":
    for n in range(2):
        SSR.run_ActionGroup("3", 1)
        sleep(2)

