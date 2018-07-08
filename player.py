# -*- coding: utf-8 -*-

"""
    Player for live stream and camera control
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from constants import *

from libs.video import VideoStream
from libs.worker import Worker
from cv2 import imwrite as cv2imwrite
from resources import *
import sys

class Player(QMainWindow):

    newCoords       = pyqtSignal(object)
    newCoordsCreate = pyqtSignal(object)
    playerClosed    = pyqtSignal(bool)

    def __init__(self, stream_url, master=None):
        QMainWindow.__init__(self, master)

        self.stream_url = stream_url

        # QLabel where the video will be rendered
        self.video_frame = QLabel() 
        self.isPaused = True     # flag for play/pause button       

        # Threadpool to control order of camera movements
        self.threadpool = QThreadPool()

        self.createUI()


    def _clear_background(self, width=1280, height=720):
        """ 
            "Clear" Qlabel background painting it black
        """
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor(0,0,0))
        p = QPainter(pixmap)
        p.drawRect(0,0,width, height)
        p.end()
        self.video_frame.setPixmap(pixmap)
        self.video_frame.setGeometry(QRect(0, 0, width, height))
        # self.resize(width, width)


    def createUI(self):
        """
            Set up the user interface, signals & slots
        """

        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        # Side ToolBar for Buttons (play, pause, etc)
        self.menuToolBar = QToolBar() 
        self.addToolBar(Qt.LeftToolBarArea, self.menuToolBar)

        play_icon = QIcon()
        play_icon.addPixmap(QPixmap(PLAY_PATH))
        play_icon.addPixmap(QPixmap(PLAY_PATH), QIcon.Normal, QIcon.Off)
        play_icon.addPixmap(QPixmap(PAUSE_PATH), QIcon.Normal, QIcon.On)

        self.playAction = QAction(play_icon, 
                                self.tr(u"Play/Pause Video"), 
                                self
                        )
        self.playAction.setObjectName(self.tr(u"Play/Pause Video"))
        self.playAction.activated.connect(self.playPause)
        self.playAction.setCheckable(True)
        self.menuToolBar.addAction(self.playAction)

        self.stopAction = QAction(QIcon(STOP_PATH), 
                                self.tr(u"Stop Video"), 
                                self
                        )
        self.stopAction.setObjectName(self.tr(u"Stop Video"))
        self.stopAction.triggered.connect(self.stop)
        self.menuToolBar.addAction(self.stopAction)

        self.menuToolBar.addSeparator()


        # Main Plugin Layout box
        self.vboxlayout = QVBoxLayout()
        self.vboxlayout.addWidget(self.video_frame)
        self.widget.setLayout(self.vboxlayout)

        # Let everything disabled until loads the stream
        self.playAction.setEnabled(False)
        self.stopAction.setEnabled(False)


    def playPause(self):
        """ 
            Play / Pause button action
            Play: start threads, change button action, 
                recieve signals from streaming threads
            Pause: Only stop image, but keep threads alive
        """

        if self.isPaused:
            self.isPaused = False
            self.playAction.setChecked(True)
            start_worker = Worker(self.video_stream.start)
            self.threadpool.start(start_worker)

        else:
            self.playAction.setChecked(False)
            self.isPaused = True


    def stop(self):
        """ Stop: Stop all streaming threads, 
                clear player background, 
                disable control buttons
        """
        self.isPaused = True
        self.playAction.setChecked(False)
        stop_worker = Worker(self.video_stream.stop)
        self.threadpool.start(stop_worker)
        self._clear_background(self.width, self.height)
        self.resize(self.width, self.height)


    def nextFrame(self, image):
        """ 
            Receive next frame for streaming, process it 
            and display the adjusted image in qt video frame.  
        """
        if not self.isPaused:
            if not self.geo_jpg:
                self.define_geo_files(image)
            image, change = self.processFrame(image)
            image = QImage(image.tostring(),self.width,self.height,
                                        QImage.Format_RGB888)
            pix = QPixmap.fromImage(image)
            self.video_frame.setPixmap(pix)
            if change:
                self.resize(self.width, self.height)


    def processFrame(self, image):
        """ 
            Process stream image with all appropriate changes
            such as resizing, etc. 
        """
        res_changed = False
        height, width  = image.shape[:2]
        if self.width != width or self.height != height:
            self.width, self.height = width, height
            res_changed = True
        return image, res_changed

            
    def start(self, width=1280, height=720):
        """ 
            Start player
        """
        self.video_stream = VideoStream(self.stream_url)

        self.video_frame.connect(self.video_stream,
                    SIGNAL('newImage(PyQt_PyObject)'),
                    self.nextFrame)

        self.playAction.setEnabled(True)
        self.stopAction.setEnabled(True)

        self.playerClosed.emit(False)
        self.width = width
        self.height = height
        self.setWindowTitle("Demo Camera Player")
        self.setWindowIcon(QIcon('icons/ico.png'))
        self._clear_background(width, height)
        self.resize(width, height)
        self.show()


    def closeEvent(self, event):
        """ 
            Close Player: disconnect signals.

        """
        self.stop()

        try:
            self.video_frame.disconnect(self.video_stream,
                        SIGNAL('newImage(PyQt_PyObject)'),
                        self.nextFrame)

            self.playerClosed.emit(True)
        except:
            pass


if __name__ == '__main__':
    # url for stream, considering your camera has MJPEG stream
    # example of some avigilon camera on internal network with ip 192.168.0.50 and motion jpeg stream 

    stream_url = "http://192.168.0.50/media/cam0/still.jpg"

    app = QApplication(sys.argv)
    win = Player(stream_url)
    win.start()
    app.exec_()
