import threading

global evdev_available

try:
    from evdev import InputDevice, KeyEvent, categorize, ecodes
    evdev_available = True
except ImportError:
    evdev_available = False

from config import settings

import app

class KeyListener(threading.Thread):
    device_available = evdev_available;

    def __init__(self, playlist):
        if(KeyListener.device_available):
            threading.Thread.__init__(self)

            try:
                self.dev = InputDevice(settings.inputdevice)
            except:
                KeyListener.device_available = False
                print settings.inputdevice + " not found"

            self.playlist = playlist

    def run(self):
        if KeyListener.device_available:
            for event in self.dev.read_loop():
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)
                    if key_event.keystate == KeyEvent.key_down:
                        print(key_event.keycode)
                        command = self.playlist.playlist['keys'][key_event.keycode]
                        if(command is not None):
                            print command
                            try:
                                self.playlist.index = command - 1
                                self.playlist.video.terminate()
                            except TypeError:
                                try:
                                    if(command == "previous"):
                                        if(self.playlist.index > 0):
                                            self.playlist.index -= 1
                                            self.playlist.video.terminate()
                                    elif(command == "next"):
                                        if(self.playlist.index < self.playlist.size - 1):
                                            self.playlist.index += 1
                                            self.playlist.video.terminate()
                                except:
                                    print "Unexpected error"

