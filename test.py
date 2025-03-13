import math
import cv2
import numpy as np
import pyautogui
import hand
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
screen_w, screen_h = pyautogui.size()
scale_factor = 0.5


def get_hand_info(pointList):
    """Xác định bàn tay trái/phải và trạng thái các ngón tay."""
    if not pointList:
        return None, []

    wrist_x, thumb_x = pointList[0][1], pointList[4][1]
    hand_side = "left" if thumb_x < wrist_x else "right"

    fingers = [
        pointList[fingerId[0]][1] < pointList[fingerId[0] - 1][1] if hand_side == "left"
        else pointList[fingerId[0]][1] > pointList[fingerId[0] - 1][1]
    ]

    fingers += [pointList[fingerId[i]][2] < pointList[fingerId[i] - 2][2] for i in range(1, 5)]
    return hand_side, fingers


def adjust_volume(pointList):
    """Điều chỉnh âm lượng bằng cử chỉ ngón cái và ngón trỏ."""
    global adjusting
    x1, y1, x2, y2 = *pointList[4][1:], *pointList[8][1:]
    cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    if adjusting:
        length = math.hypot(x2 - x1, y2 - y1)
        vol = np.interp(length, [10, 160], (minVolume, maxVolume))
        volume.SetMasterVolumeLevel(vol, None)

    if fingers.count(1) == 3:
        adjusting = False


def handle_auto_scroll(pointList):
    """Bật/Tắt chế độ Auto-Scroll."""
    global auto_scroll
    if auto_scroll and fingers == [0, 1, 0, 0, 0]:
        auto_scroll = False
        pyautogui.mouseUp(button='middle')
        print("❌ Auto-Scroll OFF")
    elif not auto_scroll and fingers == [0, 1, 1, 0, 0]:
        auto_scroll = True
        pyautogui.mouseDown(button='middle')
        print("🔄 Auto-Scroll ON")

    if auto_scroll and pointList:
        x, y = pointList[12][1], pointList[12][2]
        cursor_x = np.interp(x, [0, frame.shape[1]], [0, screen_w]) * scale_factor
        cursor_y = np.interp(y, [0, frame.shape[0]], [0, screen_h]) * scale_factor
        pyautogui.moveTo(cursor_x, cursor_y, duration=0.1)


while True:
    ret, frame = cap.read()
    frame = detector.findHands(frame)
    pointList = detector.findPosition(frame, draw=False)
    hand_side, fingers = get_hand_info(pointList)

    if fingers == [1, 1, 0, 0, 0]:
        mode, adjusting = 'volume', True
        print('Mode: Volume')
    elif fingers == [0, 1, 1, 0, 0]:
        mode = 'scroll'

    if mode == 'volume' and pointList:
        adjust_volume(pointList)
    if mode == 'scroll':
        handle_auto_scroll(pointList)

    cv2.imshow('Vision Control', frame)
    if cv2.waitKey(1) == ord('x'):
        break

cap.release()
cv2.destroyAllWindows()
