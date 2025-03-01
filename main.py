import math
import cv2
import os
import time
import numpy
import hand

# Volume
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Lấy thông tin âm lượng hệ thống
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volume.GetMute()
volume.GetMasterVolumeLevel()
volumeRange = volume.GetVolumeRange()
minVolume = volumeRange[0]
maxVolume = volumeRange[1]

sTime = 0
cap = cv2.VideoCapture(0)

detector = hand.handDetector(detectionCon=0.7)
fingerId = [4, 8, 12, 16, 20]

mode = ''
adjusting = False

while True:
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
            if pointList[fingerId[0]][1] < pointList[fingerId[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        elif pointList[fingerId[0]][1] > pointList[fingerId[0] - 1][1]: # tay phai
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
            vol = numpy.interp(length, [10, 160], (minVolume, maxVolume))
            volume.SetMasterVolumeLevel(vol, None)

        # Nếu giơ lên 3 ngón tay, dừng điều chỉnh
        if fingers.count(1) == 3:
            adjusting = False
            print("Đã khóa điều chỉnh âm lượng!")

        if fingers.count(1) == 0:
            mode = ''
            adjusting = False
            print("Huy che do dieu chinh volume")








    # Calculate FPS
    cTime = time.time() # 0:0:00s
    fps = 1/(cTime - sTime)
    sTime = cTime

    # Show FPS
    cv2.putText(frame,
                f"FPS:{int(fps)}",
                (150, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                1)

    cv2.imshow('Vision Control', frame)
    if cv2.waitKey(1) == ord('x'):
        break


cap.release() # Giải phóng camera
cv2.destroyAllWindows()