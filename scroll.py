import numpy
import pyautogui

class AutoScroll:
    def __init__(self, screen_height):
        self.scroll = False
        self.screen_height = screen_height
        self.mouse_x, self.mouse_y = pyautogui.position()
        self.index_y = None
        self.distance_hand_min = -60
        self.distance_hand_max = 60
        self.distance_mouse_min = -180
        self.distance_mouse_max = 180

    def start(self, pointList):
        if len(pointList) >= 21:
            self.scroll = True
            pyautogui.mouseDown(button='middle')
            pyautogui.moveTo(pyautogui.position()[0], self.screen_height // 2)
            self.index_y = pointList[8][2]
            self.mouse_y = self.screen_height // 2

    def update(self, pointList, fingers):
        if len(pointList) >= 21:

            if not self.scroll:
                return

            x, y = pyautogui.position()

            if fingers[4] == 1:
                return

            index_current_y = pointList[8][2]

            if self.index_y is None:
                self.index_y = index_current_y
                return

            distance_y = index_current_y - self.index_y
            mapped_mouse_y = numpy.interp(distance_y, [self.distance_hand_min, self.distance_hand_max],
                                          [self.distance_mouse_min, self.distance_mouse_max])

            pyautogui.moveTo(x, self.mouse_y + mapped_mouse_y, duration=0.1)

            self.index_y = index_current_y
            self.mouse_y += mapped_mouse_y

    def stop(self):
        self.scroll = False
        pyautogui.mouseUp(button='middle')





