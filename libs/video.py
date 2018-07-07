# -*- coding: utf-8 -*-

from PyQt4.QtCore import QThread, pyqtSignal
from constants import SE_DATA_PATH
import numpy as np
import requests
import os.path

try:
    import cv2
    import_message = ''
    try: 
        BGR2RGB = cv2.cv.CV_BGR2RGB
    except:
        BGR2RGB = cv2.COLOR_BGR2RGB
except ImportError:
    print("The opencv library for python is needed to run video")
    BGR2RGB = None


class VideoStream(QThread):

    newImage = pyqtSignal(np.ndarray)

    def __init__(self, stream_url):
        super(VideoStream,self).__init__()
        self.streamUrl = stream_url


    def readb64(self, base64_string):
        np_array = np.fromstring(base64_string.decode('base64'), np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        return img

    def run(self):
        if self.streamUrl:
            while True:
                try:
                    req = requests.get(self.streamUrl, stream=True)
                    image = self.readb64(req.content)
                    image = cv2.cvtColor(image, BGR2RGB)
                    self.newImage.emit(image)
                except Exception as e:
                    self.stop()
                    print("Cannot start video stream. Reason: {}".format(e))
                    break

    def stop(self):
        self.terminate()