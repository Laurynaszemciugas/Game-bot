import cv2
import cv2 as cv
import numpy as np
import win32gui

from time import time
from windowCapture import WindowCapture


haystack = cv.imread("img.png")
needle = cv.imread("cabbage.png")

needle_w = needle.shape[1]
needle_h = needle.shape[0]





def detectObjects(haystack, needle):

    result = cv.matchTemplate(
        haystack,
        needle,
        cv.TM_CCOEFF_NORMED
    )

    threshold = 0.60

    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))

    rectangles = []
    scores = []

    for location in locations:

        x = int(location[0])
        y = int(location[1])

        rect = [
            x,
            y,
            int(needle.shape[1]),  # width
            int(needle.shape[0])   # height
        ]

        rectangles.append(rect)

        # Score at this exact match location
        scores.append(float(result[y, x]))


    print(scores)

    indices = cv.dnn.NMSBoxes(
        rectangles,
        scores,
        threshold,
        0.3
    )

    points = []

    for i in indices:

        x, y, w, h = rectangles[i]

        center_x = x + int(w / 2)
        center_y = y + int(h / 2)

        points.append((center_x, center_y))

        cv.rectangle(haystack, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv.drawMarker(
            haystack,
            (center_x, center_y),
            (0, 0, 255),
            cv.MARKER_CROSS
        )


    return points

points = detectObjects(haystack, needle)


detectObjects(haystack, needle)
cv2.imshow("haystack", haystack)
cv2.waitKey(0)



# Replace this with your target application's exact window title
wincap = WindowCapture("Steam")

loop_time = time()

while True:

    screenshot = wincap.get_screenshot()

    if screenshot is not None:
        points = detectObjects(screenshot, needle)

        print("Detected objects:", points)

        cv.imshow("haystack", screenshot)


    current_time = time()
    elapsed = current_time - loop_time

    if elapsed > 0:
        print("FPS:", round(1 / elapsed, 2))

    loop_time = current_time

    if cv.waitKey(1) & 0xFF == ord("q"):
        break

cv.destroyAllWindows()



def get_screen_position(self, position):
    left, top = win32gui.ClientToScreen(self.hwnd, (0, 0))

    return (
        left + position[0],
        top + position[1]
    )


def print_windows(hwnd, extra):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)

        if title:
            print(
                f"HWND={hwnd} | "
                f"Title={title} | "
                f"Rect={win32gui.GetWindowRect(hwnd)}"
            )

win32gui.EnumWindows(print_windows, None)