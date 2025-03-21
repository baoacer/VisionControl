import cv2
import pyautogui
import hand

class TabWindow:
    def __init__(self):
        self.alt_tab_active = False         
        self.prev_x = None  # Lưu vị trí X trước đó để kiểm tra vuốt
        self.threshold_x = 200  # Vị trí đường dọc (giữa màn hình)

    def __set__(self, pointList):
        self.pointList = pointList 

    def detect_gesture(self):
        if not self.pointList:
            return None

        is_hand_open = (
            self.pointList[8][2] > self.pointList[6][2] and
            self.pointList[12][2] > self.pointList[10][2] and
            self.pointList[16][2] > self.pointList[14][2] and
            self.pointList[20][2] > self.pointList[18][2]
        )

        is_hand_closed = (
            self.pointList[8][2] < self.pointList[6][2] and
            self.pointList[12][2] < self.pointList[10][2] and
            self.pointList[16][2] < self.pointList[14][2] and
            self.pointList[20][2] < self.pointList[18][2]
        )

        if is_hand_open:
            return "open"
        elif is_hand_closed:
            return "closed"
        return None
        
    def execute(self, frame):
        if not self.pointList:
            return

        gesture = self.detect_gesture()
        x_index_finger = self.pointList[8][1]  # Vị trí X của ngón trỏ

        cv2.line(frame, (self.threshold_x, 0), (self.threshold_x, 480), (0, 255, 0), 2)  

        if gesture == "open" and not self.alt_tab_active:
            print("Phát hiện bàn tay mở -> Giữ Alt + Tab")
            pyautogui.keyDown("alt")
            pyautogui.press("tab")
            self.alt_tab_active = True  # Đánh dấu trạng thái

        elif gesture == "closed" and self.alt_tab_active:
            print("Phát hiện bàn tay nắm -> Chọn ứng dụng")
            pyautogui.press("enter")
            pyautogui.keyUp("alt")
            self.alt_tab_active = False # Đánh dấu trạng thái

        # Kiểm tra ngón trỏ có vượt qua vị trí chỉ định không
        if self.prev_x is not None and self.alt_tab_active:
            if self.prev_x < self.threshold_x and x_index_finger >= self.threshold_x:
                print("Vuốt sang phải → -> Nhấn Tab")
                pyautogui.press("tab")

        self.prev_x = x_index_finger  
