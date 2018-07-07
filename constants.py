import os.path

ICONS_PATH = "icons/player"

PLAY_PATH = '{}/play.png'.format(ICONS_PATH)
PAUSE_PATH = '{}/pause.png'.format(ICONS_PATH)
STOP_PATH = '{}/stop.png'.format(ICONS_PATH)


LOGO_PATH = '{}/play.png'.format(ICONS_PATH)



def fileExist(file_path):
    import errno
    file_dir = os.path.dirname(file_path)
    if os.path.isfile(file_path):
        return True
    try:
        os.makedirs(file_dir)
    except OSError as exception:
        # if exception.errno != errno.EEXIST:
        #     raise
        pass
    return False  