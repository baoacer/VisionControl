import math

import cv2
import numpy
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Thiết lập điều khiển âm lượng
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
minVolume, maxVolume = volume.GetVolumeRange()[:2]

class Volume:
    def __init__(self, pointList = None, frame = None, fingers = None):
        self.pointList = pointList
        self.frame = frame
        self.fingers = fingers
        self.adjusting = False

    def __set__(self, pointList, frame, fingers):
        self.pointList = pointList
        self.frame = frame
        self.fingers = fingers

    def run(self):
        if len(self.pointList) != 0:
            self.adjusting = True
            index_x, index_y = self.pointList[4][1], self.pointList[4][2]
            middle_x, middle_y = self.pointList[8][1], self.pointList[8][2]

            cv2.circle(self.frame, (index_x, index_y), 7, (255, 0, 0), -1)
            cv2.circle(self.frame, (middle_x, middle_y), 7, (255, 0, 0), -1)
            cv2.line(self.frame, (index_x, index_y), (middle_x, middle_y), (255, 0, 0), 2)

            if self.adjusting:
                length = math.hypot(middle_x - index_x, middle_y - index_y)
                vol = numpy.interp(length, [15, 150], (minVolume, maxVolume))
                volume.SetMasterVolumeLevel(vol, None)

