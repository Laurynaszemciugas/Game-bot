import cv2
import cv2 as cv
import numpy as np
import os
from time import time, sleep
from windowCapture import WindowCapture
from vision import Vision
from hsvfilter import HsvFilter
import pyautogui
from threading import Thread
from detection import Detection
from FpsThread import Fps

# generate Negative image txt
# generate_negative_file()
# get the pos.txt
#  C:/Users/spina/Downloads/opencv/build/x64/vc15/bin/opencv_annotation.exe --annotations=pos.txt --images=Positive/
# get the .vec
# C:/Users/spina/Downloads/opencv/build/x64/vc15/bin/opencv_createsamples.exe -info pos.txt -w 24 -h 24 -num 1000 -vec pos.vec
# train the model
#  C:/Users/spina/Downloads/opencv/build/x64/vc15/bin/opencv_traincascade.exe -data cascade/ -vec pos.vec -bg neg.txt -w 24 -h 24 -numPos 200 -numNeg 100 -numStages 5






# ====================================================================
#  inisilize the filters or classes
# ====================================================================

wincap = WindowCapture("Steam")

fps = Fps()


vision = Vision("img_2.png")

#  show the hsv filtering window used only if hsv filter is not provided to the class
vision.init_control_gui()


hsv_filter = HsvFilter(0,69,42,79,255,255,28,0,63,133)

cascade_limeStone = cv.CascadeClassifier('cascade/limestone_model_final.xml')

vision_limeStone = Vision(None)



#  just time
loop_time = time()



# ====================================================================
#  settings for actions
# ====================================================================

is_bot_in_action = False

start_bot = False

use_hsv = False

model_Name = "Cascade/limestone_model_final.xml Model"


bot_active = "Bot - Off"

allow_to_update_hsv = False


# ====================================================================
#  bot actions logic
# ====================================================================

def bot_actions(points):
    global is_bot_in_action
    global bot_active

    if len(points) > 0:
        target = points[0]

        screen_target = wincap.to_screen_coordinates(target,35,50)
        bot_active = "Bot - moving"
        pyautogui.moveTo(
            screen_target[0],
            screen_target[1],
            2
        )


        pyautogui.click()
        bot_active = "Bot - Clicked"
        sleep(0.5)

    bot_active = "Bot - waiting"
    sleep(5)

    is_bot_in_action = False


# ====================================================================
#  inisialize the model .xml
# ====================================================================

detection = Detection('cascade/limestone_model_final.xml')

# ====================================================================
#  stard threads
# ====================================================================
wincap.start()
detection.start()
fps.start()

while True:

    if wincap.screenshot is None:
        continue

    detection.update(wincap.screenshot,use_hsv)

    detection_image = vision_limeStone.draw_rectangles(wincap.screenshot, detection.points)

    cv.imshow("detection", detection_image)

    # ====================================================================
    #  check if bot needs to be on if yes turn it on and pass detection points from the other thread
    # ====================================================================
    if not is_bot_in_action and start_bot:
        is_bot_in_action = True
        t = Thread(target=bot_actions, args=(detection.points,))
        t.start()
        print("Bot started")




    current_time = time()
    elapsed = current_time - loop_time

    fps.update(elapsed)



    if allow_to_update_hsv:
        procssed_image = vision.apply_hsv_filter(wincap.screenshot)
        cv.imshow("procssed_image", procssed_image)


    # ====================================================================
    #  display stuff
    # ====================================================================

    cv.putText(
        detection_image,
        model_Name,
        (50, 50),  # X, Y position
        cv.FONT_HERSHEY_SIMPLEX,
        1,  # Font size
        (0, 255, 0),  # Green (BGR)
        2  # Thickness
    )

    cv.putText(
        detection_image,
        bot_active,
        (50, 100),  # X, Y position
        cv.FONT_HERSHEY_SIMPLEX,
        1,  # Font size
        (0, 255, 0),  # Green (BGR)
        2  # Thickness
    )


    cv.putText(
        detection_image,
        fps.get_fps(),
        (50, 150),  # X, Y position
        cv.FONT_HERSHEY_SIMPLEX,
        1,  # Font size
        (0, 255, 0),  # Green (BGR)
        2  # Thickness
    )

    # ====================================================================
    #  display frames
    # ====================================================================

    # if elapsed > 0:
    #     print("FPS:", round(1 / elapsed, 2))

    loop_time = current_time

    # ====================================================================
    #  Actions via keyboard
    # ====================================================================

    key = cv.waitKey(1) & 0xFF

    # off
    if key == ord("q"):
        detection.stop()
        wincap.stop()
        fps.stop()
        break

    # On/Off the bot
    elif key == ord("s"):
        if start_bot:
            start_bot = False
            bot_active = "Bot - Off"
        else:
            start_bot = True

    # Show and use other model the non cascade with hsv
    elif key == ord("p"):
        if allow_to_update_hsv:
            allow_to_update_hsv = False
        else:
            allow_to_update_hsv = True


    # Use hsv model or change to cascade
    elif key == ord("l"):
        if use_hsv:
            use_hsv = False
            model_Name = "Cascade/limestone_model_final.xml Model"
        else:
            model_Name = "HSV Filter"
            use_hsv = True

cv.destroyAllWindows()