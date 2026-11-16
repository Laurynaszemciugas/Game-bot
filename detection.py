import cv2 as cv
from threading import Thread, Lock
from vision import Vision

class Detection:

    stopped = True
    lock = None
    points = []
    cascade = None
    screenshot = None
    use_hsv = False

    vision = Vision("needle.png")

    def __init__(self, model_file_xml):

        self.lock = Lock()
        self.cascade = cv.CascadeClassifier(model_file_xml)

    def update(self, screenshot, use_hsv):

        self.use_hsv = use_hsv

        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            if not self.screenshot is None:

                if self.use_hsv:
                  points = self.vision.find(self.screenshot)
                else:
                  points = self.cascade.detectMultiScale(self.screenshot)

                self.lock.acquire()
                self.points = points
                self.lock.release()