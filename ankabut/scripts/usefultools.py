import subprocess
import platform
import shutil
import time
import os

os_type = platform.system()

class StopWatch:
    def __init__(self,duration):
        self.duration = duration
        self.ptime = 0 


    def start(self):
        self.ptime = time.time()


    def restart(self):
        self.ptime = time.time()


    def is_passed(self):
        if time.time() >= self.ptime + self.duration:
            return True
        return False

class Timer:
    def __init__(self):
        self.t = 0

    def start(self):
        self.t = time.time()
    
    def elapsed_time(self):
        return int(time.time() - self.t)


def makedir(address):
    if not os.path.exists(address):
            os.makedirs(address)


def makefile(address):
    if not os.path.exists(address):
        f = open(address , 'w' )
        f.close()


def xdg_open(file_path):
    if os.path.exists(file_path):
        if os_type == 'Linux':
            subprocess.call("xdg-open '"+file_path+"' &",shell=True)
        elif os_type == 'Windows':
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(['cmd', '/C', 'start', file_path,  file_path],shell=False, creationflags=CREATE_NO_WINDOW)

def move(pre , new):
    try:
    
        shutil.move(pre , new)

    except Exception as e:
        print(str(e))
    else:
        print('file moved')



if __name__ == '__main__':
    #test 
    pass




