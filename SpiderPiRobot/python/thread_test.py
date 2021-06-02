import threading
from time import ctime,sleep

def task_handle(task = 's'):
    if task == 'a' or task == 'b':
        while True:
            sleep(0.3)
            if sign == False:
                break
            print(task)
    else:
        print(task)

t = threading.Thread(target=task_handle,args=('s',))

if __name__ == '__main__':
    while True:
        command = input()
        sign = False
        while t.isAlive():
            sleep(0.1)
        t = threading.Thread(target=task_handle,args=(command,))
        t.setDaemon(True)
        sign = True
        t.start()