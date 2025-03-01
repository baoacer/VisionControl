import math
import cv2
import os
import time
import numpy
import hand

# Video
sTime = 0
cap = cv2.VideoCapture(0)

detector = hand.handDetector(detectionCon=0.9)
fingerId = [4, 8, 12, 16, 20]

start_time = None
hold_time = 3

while True:
    ret, frame = cap.read()
    frame = detector.findHands(frame)
    pointList = detector.findPosition(frame, draw=False)

    if len(pointList) != 0:
        fingers = []

        # ngón cái
        # xác định hướng bàn tay
        if pointList[17][1] > pointList[5][1]:  # tay trai
            if pointList[fingerId[0]][1] < pointList[fingerId[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        elif pointList[fingerId[0]][1] > pointList[fingerId[0] - 1][1]:  # tay phai
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 ngon dai
        for id in range(1, 5):
            if pointList[fingerId[id]][2] < pointList[fingerId[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        # Phát hiện nắm tay
        if fingers.count(1) == 0:
            print("Phát hiện nắm tay, Chuẩn bị tắt máy...")
            if start_time is None:
                start_time = time.time()

            elapsed_time = time.time() - start_time
            print(f"Nắm tay trong {elapsed_time:.1f}s")

            if elapsed_time > hold_time:
                print("Tắt máy...")
                os.system("shutdown /s /t 1")
                break
        else:
            start_time = None


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