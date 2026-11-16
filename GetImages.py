import cv2
import cv2 as cv
import numpy as np
import os
from time import time
from windowCapture import WindowCapture





wincap = WindowCapture("Albion online Client")

loop_time = time()

while True:

    screenshot = wincap.get_screenshot()


    cv.imshow("Train data",screenshot)

    current_time = time()
    elapsed = current_time - loop_time

    if elapsed > 0:
        print("FPS:", round(1 / elapsed, 2))

    loop_time = current_time

    key = cv.waitKey(1)

    if key & 0xFF == ord("q"):
        cv2.destroyAllWindows()
        break
    elif key & 0xFF == ord("g"):
        cv.imwrite('Positive/{}.jpg'.format(loop_time), screenshot)
    elif key & 0xFF == ord("f"):
        cv.imwrite('Negative/{}.jpg'.format(loop_time), screenshot)


