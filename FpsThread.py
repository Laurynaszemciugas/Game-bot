import cv2 as cv
from threading import Thread, Lock
from time import time, sleep

class Fps:

    stopped = True
    lock = None
    elapsed = None
    fps = "Fps - none"

    def __init__(self):
        self.lock = Lock()

    def start(self):
            self.stopped = False
            t = Thread(target=self.run)
            t.start()


    def stop(self):
            self.stopped = True



    def update(self, elap):


            self.lock.acquire()
            self.elapsed = elap
            self.lock.release()


    def run(self):
            while not self.stopped:

                    sleep(1)



                    fps_text = f"FPS: {round(1 / self.elapsed, 2)}"

                    self.lock.acquire()
                    self.fps = fps_text
                    self.lock.release()

    def get_fps(self):
        with self.lock:
            return self.fps