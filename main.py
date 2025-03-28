import cv2
import pyautogui
from pycparser.c_ast import Switch

import hand
from hand_gesture import HandGesture
from hidden_window import WindowControl
from scroll import AutoScroll
from shutdown import Shutdown
from tab_window import TabWindow
from volume import Volume

# Thiết lập camera
cap = cv2.VideoCapture(0)
detector = hand.handDetector(detectionCon=0.9)

# Biến trạng thái
mode = ''

screen_width, screen_height = pyautogui.size()
auto_scroll = AutoScroll(screen_height)
volume = Volume()
window_control = WindowControl()
hand_gesture = HandGesture()
tab_window = TabWindow()
shutdown = Shutdown()
end = [0, 0, 0, 0, 1]
reset = ''
while True:
    ret, frame = cap.read()

    frame = detector.findHands(frame)
    pointList = detector.findPosition(frame, draw=False)
    fingers = hand_gesture.detect_fingers(pointList)
    print("DEBUG: fingers =", fingers)
    if fingers is not None:
        if fingers == [1, 1, 0, 0, 0]:
            mode = 'volume'
        if fingers == [0, 1, 1, 0, 0]:
            mode = 'scroll'
        if fingers == [0, 1, 1, 1, 1]:
            mode = 'tab'
        if fingers == [0, 0, 0, 0,1]:
            mode = 'shutdown'
        if fingers == [1, 0, 0, 0, 0]:
            mode = 'hidden'
    else:
        mode = reset

    match mode:
        case 'volume':
            volume.__set__(pointList, frame, fingers)
            volume.run()
            if fingers.count(1) == 3:
                volume.adjusting = False
                mode = reset
        case 'scroll':
            if not auto_scroll.scroll:
                auto_scroll.start(pointList)
            auto_scroll.update(pointList, fingers)
            if len(fingers) != 0 and fingers[2] == 0:
                auto_scroll.stop()
                mode = reset
        case 'hidden':
            window_control.minimize_window(fingers)
            if fingers == end:
                mode = reset
        case 'tab':
            tab_window.set_point_list(pointList)
            tab_window.execute(frame)
            if len(fingers) != 0 and fingers[4] == 0:
                mode = reset
        case 'shutdown':
            shutdown.execute(fingers)



    # if mode == 'volume':
    #     volume.__set__(pointList, frame, fingers)
    #     volume.run()
    #     if fingers.count(1) == 3:
    #         volume.adjusting = False
    #         mode = ''
    # if mode == 'scroll' and not auto_scroll.scroll:
    #     auto_scroll.start(pointList)
    # if auto_scroll.scroll:
    #     auto_scroll.update(pointList, fingers)
    # if len(fingers) != 0:
    #     if mode == 'scroll' and fingers[1] == 0 or fingers[2] == 0:
    #         auto_scroll.stop()
    #         mode = ''
    # # if mode == 'hidden':
    # #     window_control.minimize_window(fingers)
    # #     if fingers == end:
    # #         mode = ''
    # # if mode == 'tab':
    # #     tab_window.set_point_list(pointList)
    # #     tab_window.execute(frame)
    # # if mode == 'shutdown':
    # #     shutdown.execute(fingers)


    # print(mode)
    cv2.imshow('Vision Control', frame)
    if cv2.waitKey(1) == ord('x'):
        break

cap.release()
cv2.destroyAllWindows()