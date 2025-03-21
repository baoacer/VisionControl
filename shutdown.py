import time
import os

class Shutdown:
    def __init__(self):
        self.start_time = None  # Biến lưu thời điểm bắt đầu đếm ngược
        self.hold_time = 3  

    def execute(self, fingers):
        """ Kiểm tra nếu chỉ giơ ngón út thì đếm ngược để tắt máy """
        if fingers == [0, 0, 0, 0, 1]: 
            if self.start_time is None:
                self.start_time = time.time() 

            elapsed_time = time.time() - self.start_time
            print(f"Giữ ngón út trong {elapsed_time:.1f}s")

            if elapsed_time >= self.hold_time:
                print("Tắt máy...")
                os.system("shutdown /s /t 1")
        else:
            self.start_time = None  
