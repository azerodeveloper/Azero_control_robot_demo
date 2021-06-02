#!/usr/bin/python3
# encoding: utf-8
import threading
import time
# import _thread


class PWM_Servo(object):

    def __init__(self, pi, pin, freq=50, min_width=500, max_width=2500, deviation=0, control_speed=False):
        self.pi = pi
        self.SPin = pin
        self.Position = 1500
        self.positionSet = self.Position
        self.Freq = freq
        self.Min = min_width
        self.Max = max_width

        self.Deviation = deviation

        self.stepTime = 20
        self.positionInc = 0.0
        self.Time = 0
        self.Time_t = 0
        self.incTimes = 0
        self.speedControl = control_speed
        self.positionSet_t = 0
        self.posChanged = False
        self.servoRunning = False

        self.pi.set_PWM_range(self.SPin, int(1000000 / self.Freq))
        self.pi.set_PWM_frequency(self.SPin, self.Freq)
        if control_speed is True:
            t1 = threading.Thread(target=PWM_Servo.updatePosition, args=(self,))
            t1.setDaemon(True)
            t1.start()
            # _thread.start_new(PWM_Servo.updatePosition, (self,))

    def setPosition(self, pos, time=0):
        if pos < self.Min or pos > self.Max:
            print(pos)
            return
        if time == 0:
            self.Position = pos
            self.positionSet = self.Position
            self.pi.set_PWM_dutycycle(self.SPin, self.Position + self.Deviation)
        else:
            if time < 20:
                self.Time_t = 20
            elif time > 30000:
                self.Time_t = 30000
            else:
                self.Time_t = time
            self.positionSet_t = pos
            self.posChanged = True
            
    def getPosition(self):
        return self.Position

    def updatePosition(self):
        while True:
            if self.posChanged is True:
                self.Time = self.Time_t
                self.positionSet = self.positionSet_t
                self.posChanged = False

                self.incTimes = self.Time / self.stepTime
                if self.positionSet > self.Position:
                    self.positionInc = self.positionSet - self.Position
                    self.positionInc = -self.positionInc    
                else:
                    self.positionInc = self.Position - self.positionSet
                self.positionInc = self.positionInc / float(self.incTimes)
                self.servoRunning = True

            if self.servoRunning is True:
                self.incTimes -= 1
                if self.incTimes == 0:
                    self.Position = self.positionSet
                    self.servoRunning = False
                else:
                    self.Position = self.positionSet + self.positionInc * self.incTimes
                self.pi.set_PWM_dutycycle(self.SPin, self.Position + self.Deviation)
            time.sleep(0.02)

    def setDeviation(self, newD=0):
        if newD > 300 or newD < -300:
            return
        self.Deviation = newD



