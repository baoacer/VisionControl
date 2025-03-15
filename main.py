import math
import cv2
import numpy
import hand
import pyautogui
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Thiết lập điều khiển âm lượng
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
minVolume, maxVolume = volume.GetVolumeRange()[:2]

# Thiết lập camera
cap = cv2.VideoCapture(0)
detector = hand.handDetector(detectionCon=0.7)
fingerId = [4, 8, 12, 16, 20]

# Biến trạng thái
mode = ''
adjusting = False
auto_scroll = False
prev_y = None
mouse_y = None
screen_width, screen_height = pyautogui.size()  # Lấy kích thước màn hình

# Giới hạn delta_y trong khoảng [-60, 60]
finger_min = -60
finger_max = 60

# Giới hạn khoảng di chuyển chuột (tùy chỉnh để phù hợp)
mouse_min = -180
mouse_max = 180

while True:
    x, y = pyautogui.position()
    ret, frame = cap.read()

    # Xac dinh vi tri tay
    frame = detector.findHands(frame)
    pointList = detector.findPosition(frame, draw=False)
    # print(pointList) # point

    fingers = []
    if len(pointList) != 0:

        # xác định bàn tay
        wrist_x = pointList[0][1]
        thumb_x = pointList[4][1]

        if thumb_x < wrist_x:
            hand_side = "left"
        else:
            hand_side = "right"

        # xác định hướng bàn tay
        if hand_side == "left":
            if pointList[4][1] < pointList[3][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        elif pointList[4][1] > pointList[3][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 ngon dai
        for i in range(1, 5):
            if pointList[fingerId[i]][2] < pointList[fingerId[i] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)


    if fingers == [1, 1, 0, 0, 0]:
        mode = 'volume'
        adjusting = True
        print('Mode volume')
    # elif fingers == [0, 1, 1, 0, 0]:
    #     mode = 'scroll'
    #     auto_scroll = True
    #     print('Mode scroll')


    if mode == "volume" and len(pointList) != 0:
        x1, y1 = pointList[4][1], pointList[4][2]  # Ngón cái
        x2, y2 = pointList[8][1], pointList[8][2]  # Ngón trỏ

        # Vẽ
        cv2.circle(frame, (x1, y1), 7, (255, 0, 0), -1)
        cv2.circle(frame, (x2, y2), 7, (255, 0, 0), -1)
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # Điều chỉnh âm lượng
        if adjusting:
            length = math.hypot(x2 - x1, y2 - y1)
            vol = numpy.interp(length, [15, 150], (minVolume, maxVolume))
            volume.SetMasterVolumeLevel(vol, None)

        # Nếu giơ lên 3 ngón tay, dừng điều chỉnh
        if fingers.count(1) == 3:
            adjusting = False
            mode = ''
            print("Đã khóa điều chỉnh âm lượng!")


    # Mode = Auto Scroll
    if fingers == [0, 1, 1, 0, 0] and not auto_scroll:
        auto_scroll = True
        pyautogui.mouseDown(button='middle')
        pyautogui.moveTo(x, screen_height // 2) # di chuyển chuột ra giữa màn hình
        prev_y = pointList[8][2]
        mouse_y = screen_height // 2
        print(f"Mouse 1:::{mouse_y}")
        print("Auto-Scroll ON")

    if auto_scroll and len(pointList) != 0:
        x, y = pyautogui.position()

        if fingers[4] == 1:
            print("Giữ nguyên vị trí chuột (ngón út giơ lên)")
            pass
        else:
            # Lấy vị trí hiện tại của chuột
            current_y = pointList[8][2]  # Lấy tọa độ Y của ngón giữa

            # Tính delta_y (khoảng cách di chuyển của ngón giữa)
            delta_y = current_y - prev_y

            # Giới hạn delta_y trong khoảng [-60, 60]
            # delta_y = max(finger_min, min(delta_y, finger_max))

            # Ánh xạ delta_y thành khoảng di chuyển chuột
            mapped_mouse_y = numpy.interp(delta_y, [finger_min, finger_max], [mouse_min, mouse_max])

            print(f"delta_y: {delta_y}, mapped_mouse_y: {mapped_mouse_y}")

            # Di chuyển chuột theo trục Y
            pyautogui.moveTo(x, mouse_y + mapped_mouse_y, duration=0.1)

            # Cập nhật vị trí trước đó của ngón giữa
            prev_y = current_y
            mouse_y += mapped_mouse_y  # Cập nhật vị trí chuột mới

        if fingers[1] == 0 or fingers[2] == 0:
            auto_scroll = False
            pyautogui.mouseDown(button='middle')


    cv2.imshow('Vision Control', frame)
    if cv2.waitKey(1) == ord('x'):
        break


cap.release()
cv2.destroyAllWindows()