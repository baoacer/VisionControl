class HandGesture:
    def __init__(self):
        self.fingerId = [4, 8, 12, 16, 20]

    def detect_fingers(self, pointList):
        fingers = []
        if len(pointList) == 0:
            return fingers

        wrist_x = pointList[0][1]
        thumb_x = pointList[4][1]

        hand_side = "left" if thumb_x < wrist_x else "right"

        if hand_side == "left":
            fingers.append(1 if pointList[4][1] < pointList[3][1] else 0)
        else:
            fingers.append(1 if pointList[4][1] > pointList[3][1] else 0)

        for i in range(1, 5):
            fingers.append(1 if pointList[self.fingerId[i]][2] < pointList[self.fingerId[i] - 2][2] else 0)

        return fingers