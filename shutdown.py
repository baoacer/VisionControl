import time
import os

class Shutdown:
    def __init__(self):
        self.start_time = None
        self.hold_time = 3  

    def execute(self, fingers):
        if fingers == [0, 0, 0, 0, 1]:
            if self.start_time is None:
                self.start_time = time.time() 

            elapsed_time = time.time() - self.start_time

            if elapsed_time >= self.hold_time:
                os.system("shutdown /s /t 1")
        else:
            self.start_time = None  
