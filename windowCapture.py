import ctypes
import cv2 as cv
import numpy as np
import win32gui
import win32ui
from threading import Thread, Lock


class WindowCapture:

    stopped = True
    lock = None
    screenshot = None

    def __init__(self, window_name=None):


        self.lock = Lock()
        self.hwnd = win32gui.FindWindow(None, window_name)


        if not self.hwnd:
            raise Exception(f"Window not found: {window_name}")

        print(f"Window found: {window_name}")
        print(f"HWND: {self.hwnd}")

    def get_screenshot(self):

        if not win32gui.IsWindow(self.hwnd):
            raise Exception("Invalid window handle")

        if win32gui.IsIconic(self.hwnd):
            print("Window is minimized")
            return None

        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)

        width = right - left
        height = bottom - top

        if width <= 0 or height <= 0:
            print("Invalid window dimensions")
            return None

        hwnd_dc = win32gui.GetWindowDC(self.hwnd)

        if not hwnd_dc:
            print("Failed to get window device context")
            return None

        window_dc = None
        memory_dc = None
        bitmap = None

        try:
            window_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            memory_dc = window_dc.CreateCompatibleDC()

            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(
                window_dc,
                width,
                height
            )

            memory_dc.SelectObject(bitmap)

            result = ctypes.windll.user32.PrintWindow(
                self.hwnd,
                memory_dc.GetSafeHdc(),
                2
            )

            if result != 1:
                print("PrintWindow failed")
                return None

            bitmap_info = bitmap.GetInfo()
            bitmap_data = bitmap.GetBitmapBits(True)

            image = np.frombuffer(
                bitmap_data,
                dtype=np.uint8
            ).reshape(
                (
                    bitmap_info["bmHeight"],
                    bitmap_info["bmWidth"],
                    4
                )
            )

            image = cv.cvtColor(
                image,
                cv.COLOR_BGRA2BGR
            )

            return image.copy()

        finally:

            if bitmap is not None:
                win32gui.DeleteObject(bitmap.GetHandle())

            if memory_dc is not None:
                memory_dc.DeleteDC()

            if window_dc is not None:
                window_dc.DeleteDC()

            win32gui.ReleaseDC(self.hwnd, hwnd_dc)

    def to_screen_coordinates(self, point, right = 35, down = 50):

        window_x, window_y = win32gui.ClientToScreen(
            self.hwnd, (0, 0)
        )

        return (
            window_x + point[0] + right,  #  right
            window_y + point[1] + down  #  down
        )

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            screenshot = self.get_screenshot()
            self.lock.acquire()
            self.screenshot = screenshot
            self.lock.release()