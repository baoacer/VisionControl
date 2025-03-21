import pygetwindow


class WindowControl:
    def __init__(self):
        self.window_hidden = False

    def minimize_window(self, fingers):
        if fingers == [0, 0, 0, 0, 0] and not self.window_hidden:
            active_window = pygetwindow.getActiveWindow()
            if active_window:
                active_window.minimize()
                self.window_hidden = True
        elif fingers != [0, 0, 0, 0, 0]:
            self.window_hidden = False
