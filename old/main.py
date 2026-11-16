import os

import cv2 as cv
import numpy as np

import win32gui

haystack_img = cv.imread("img.png", cv.IMREAD_UNCHANGED)
needle_img = cv.imread("pig.png", cv.IMREAD_UNCHANGED)


os.chdir(os.path.dirname(os.path.abspath(__file__)))



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

    threshold = 0.25

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
        0.60,
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

# points = detectObjects(haystack, needle)
#
#
# detectObjects(haystack, needle)
# cv2.imshow("haystack", haystack)
# cv2.waitKey(0)






def list_windows():
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            print(hex(hwnd), win32gui.GetWindowText(hwnd))
    win32gui.EnumWindows(winEnumHandler, None)



    # def list_windows():
    #     def winEnumHandler(hwnd, ctx):
    #         if win32gui.IsWindowVisible(hwnd):
    #             title = win32gui.GetWindowText(hwnd)
    #
    #             if "Arena Breakout" in title:
    #                 print(repr(title))
    #                 print("Length:", len(title))
    #
    #     win32gui.EnumWindows(winEnumHandler, None)


list_windows()