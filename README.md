## Simple PyQt4 Player
### Requirements

- Python 2.7.*
- python qt4 (on Ubuntu: `sudo apt-get install python-qt4 libqt4-dev`)
- opencv (`pip install opencv-python`)
- requests (`pip install requests`)

## How to

Change the path for the stream url in the main `Player.py` file. This is assuming your camera has a motion jpeg stream (MJPEG). For rtsp stream, you need to decode the rtp packets. A solution would be, for example, using VLC player and its python library for bidings.


