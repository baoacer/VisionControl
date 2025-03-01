import math
import cv2
import os
import time
import numpy
import pyautogui

import hand

# Video
sTime = 0
cap = cv2.VideoCapture(0)

detector = hand.handDetector(detectionCon=0.5)
fingerId = [4, 8, 12, 16, 20]

prey_y = None

while True:
    ret, frame = cap.read()
    frame = detector.findHands(frame)
    pointList = detector.findPosition(frame, draw=False)

    if len(pointList) != 0:
        fingers = []
        x1, y1 = pointList[8][1], pointList[8][2] # ngón trỏ
        x2, y2 = pointList[12][1], pointList[12][2] # ngón giữa

        if y1 < pointList[6][2] and y2 < pointList[10][2]:
            if prey_y is not None:
                delta_y = y1 - prey_y

            if abs(delta_y) > 5:  # Chỉ cuộn khi di chuyển đáng kể
                scroll_speed = -1 if delta_y > 0 else 1  # Vuốt lên (-) -> cuộn xuống
                pyautogui.scroll(scroll_speed * 10)  # Điều chỉnh tốc độ cuộn

            prev_y = y1  # Cập nhật vị trí Y








    # Hiển thị FPS
    cTime = time.time()
    fps = 1 / (cTime - sTime)
    sTime = cTime
    cv2.putText(frame, f"FPS:{int(fps)}", (150, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)

    cv2.imshow('Vision Control', frame)
    if cv2.waitKey(1) == ord('x'):
        break

cap.release()
cv2.destroyAllWindows()