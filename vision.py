import cv2 as cv
import numpy as np
from hsvfilter import HsvFilter




class Vision:

    TRACKBAR_WINDOW = "Trackbars"

    needle_img = None

    def __init__(self, needle_img_path):

        if needle_img_path:
            self.needle_img = cv.imread(needle_img_path)

    def find(self, haystack, threshold=0.60, max_results= 10):



        result = cv.matchTemplate(
            haystack,
            self.needle_img,
            cv.TM_CCOEFF_NORMED
        )



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
                int(self.needle_img.shape[1]),  # width
                int(self.needle_img.shape[0])   # height
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

        filtered_rectangles = []

        if len(indices) > 0:
            for i in indices.flatten():
                filtered_rectangles.append(rectangles[int(i)])

        return filtered_rectangles



    def get_click_points(self, rectangles):
        points = []

        # Loop over all the rectangles
        for (x, y, w, h) in rectangles:
            # Determine the center position
            center_x = x + int(w / 2)
            center_y = y + int(h / 2)
            # Save the points
            points.append((center_x, center_y))

        return points



    def init_control_gui(self):
        cv.namedWindow(self.TRACKBAR_WINDOW,cv.WINDOW_NORMAL)
        cv.resizeWindow(self.TRACKBAR_WINDOW, 350, 700)

        def nothing(position):
            pass

        cv.createTrackbar("HMin", self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv.createTrackbar("SMin", self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar("VMin", self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar("HMax", self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv.createTrackbar("SMax", self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar("VMax", self.TRACKBAR_WINDOW, 0, 255, nothing)


        cv.setTrackbarPos("HMax", self.TRACKBAR_WINDOW,  179)
        cv.setTrackbarPos("SMax", self.TRACKBAR_WINDOW,  255)
        cv.setTrackbarPos("VMax", self.TRACKBAR_WINDOW,  255)


        cv.createTrackbar("SAdd", self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar("SSub", self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar("VAdd", self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar("VSub", self.TRACKBAR_WINDOW, 0, 255, nothing)


    def get_hsv_filter_from_controls(self):
        hsv_filter = HsvFilter()
        hsv_filter.hMin = cv.getTrackbarPos("HMin", self.TRACKBAR_WINDOW)
        hsv_filter.sMin = cv.getTrackbarPos("SMin", self.TRACKBAR_WINDOW)
        hsv_filter.vMin = cv.getTrackbarPos("VMin", self.TRACKBAR_WINDOW)
        hsv_filter.hMax = cv.getTrackbarPos("HMax", self.TRACKBAR_WINDOW)
        hsv_filter.sMax = cv.getTrackbarPos("SMax", self.TRACKBAR_WINDOW)
        hsv_filter.vMax = cv.getTrackbarPos("VMax", self.TRACKBAR_WINDOW)
        hsv_filter.sAdd = cv.getTrackbarPos("SAdd", self.TRACKBAR_WINDOW)
        hsv_filter.sSub = cv.getTrackbarPos("SSub", self.TRACKBAR_WINDOW)
        hsv_filter.vAdd = cv.getTrackbarPos("VAdd", self.TRACKBAR_WINDOW)
        hsv_filter.vSub = cv.getTrackbarPos("VSub", self.TRACKBAR_WINDOW)
        return hsv_filter


    def apply_hsv_filter(self, original_image, hsv_filter=None):

        hsv = cv.cvtColor(original_image, cv.COLOR_BGR2HSV)

        if hsv_filter is None:
            hsv_filter = self.get_hsv_filter_from_controls()

        h, s, v = cv.split(hsv)
        s = self.shift_channel(s, hsv_filter.sAdd)
        s = self.shift_channel(s, -hsv_filter.sSub)
        v = self.shift_channel(v, hsv_filter.vAdd)
        v = self.shift_channel(v, -hsv_filter.vSub)
        hsv = cv.merge((h, s, v))

        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax, hsv_filter.sMax, hsv_filter.vMax])

        mask = cv.inRange(hsv, lower, upper)
        result = cv.bitwise_and(hsv, hsv, mask=mask)


        img = cv.cvtColor(result, cv.COLOR_HSV2BGR)

        return img


    def draw_rectangles(self, haystack_img, rectangles):
        # these colors are actually BGR
        line_color = (0, 255, 0)
        line_type = cv.LINE_4

        for (x, y, w, h) in rectangles:
            # determine the box positions
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            # draw the box
            cv.rectangle(haystack_img, top_left, bottom_right, line_color, lineType=line_type)

        return haystack_img



    def shift_channel(self, c, amount):
        if amount > 0:
            lim = 255 -amount
            c[c >= lim] = 255
            c[c < lim] += amount
        elif amount < 0:
            amount = -amount
            lim = amount
            c[c <= lim] = 0
            c[c > lim] -= amount

        return c