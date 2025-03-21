import cv2
import pyautogui

import hand
from hand_gesture import HandGesture
from hidden_window import WindowControl
from scroll import AutoScroll
from volume import Volume

# Thiết lập camera
cap = cv2.VideoCapture(0)
detector = hand.handDetector(detectionCon=0.7)

# Biến trạng thái
mode = ''

screen_width, screen_height = pyautogui.size()
auto_scroll = AutoScroll(screen_height)
volume = Volume()
window_control = WindowControl()
hand_gesture = HandGesture()

while True:
    ret, frame = cap.read()

    frame = detector.findHands(frame)
    pointList = detector.findPosition(frame, draw=False)

    fingers = hand_gesture.detect_fingers(pointList)

    if fingers == [1, 1, 0, 0, 0]:
        mode = 'volume'
    elif fingers == [0, 1, 1, 0, 0]:
        mode = 'scroll'

    if mode == 'volume':
        volume.__set__(pointList, frame, fingers)
        volume.run()
        if fingers.count(1) == 3:
            volume.adjusting = False
            mode = ''
    if mode == 'scroll' and not auto_scroll.scroll:
        auto_scroll.start(pointList)
    if auto_scroll.scroll:
        auto_scroll.update(pointList, fingers)

    window_control.minimize_window(fingers)

    cv2.imshow('Vision Control', frame)
    if cv2.waitKey(1) == ord('x'):
        break

cap.release()
cv2.destroyAllWindows()