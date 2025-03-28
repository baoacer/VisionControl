import time

import cv2
import pyautogui

class TabWindow:
    def __init__(self):
        self.pointList = None
        self.gesture = None
        self.alt_tab_active = False
        self.prev_x = None
        self.threshold_x = 200

    def set_point_list(self, pointList):
        self.pointList = pointList

    def execute(self, frame):
        print(self.pointList)
        if not self.pointList:
            return
        x_index_finger = self.pointList[8][1]  # Vị trí X của ngón trỏ

        # Vẽ đường phân cách (để kiểm tra chuyển động)
        cv2.line(frame, (self.threshold_x, 0), (self.threshold_x, 480), (0, 255, 0), thickness=2)

        if    (self.pointList[8][2] < self.pointList[6][2] and
            self.pointList[12][2] < self.pointList[10][2] and
            self.pointList[16][2] < self.pointList[14][2] and
            self.pointList[20][2] < self.pointList[18][2]) and not self.alt_tab_active:
            print("Bàn tay mở -> Bật Alt+Tab")
            pyautogui.keyDown("win")
            pyautogui.press("tab")
            pyautogui.keyUp("win")
            self.alt_tab_active = True

        if (
                self.pointList[8][2] > self.pointList[7][2] and
                self.pointList[12][2] < self.pointList[11][2] and
                self.pointList[16][2] < self.pointList[15][2] and
                self.pointList[20][2] < self.pointList[19][2]
        ) and self.alt_tab_active:

            print("Bàn tay nắm -> Tắt Alt+Tab và chọn ứng dụng")
            pyautogui.press("enter")
            pyautogui.keyUp("win")
            self.alt_tab_active = False
            self.status = False

        # Kiểm tra chuyển động vuốt ngang nếu chức năng đang bật
        if self.prev_x is not None and self.alt_tab_active:
            if self.prev_x < self.threshold_x and x_index_finger >= self.threshold_x:
                print("Vuốt sang phải -> Nhấn Tab")
                pyautogui.press("right")
        self.prev_x = x_index_finger
