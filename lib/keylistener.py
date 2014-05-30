import threading
from evdev import InputDevice, KeyEvent, categorize, ecodes
import app

class KeyListener(threading.Thread):
    def __init__(self, playlist):
        threading.Thread.__init__(self)
        self.dev = InputDevice('/dev/input/event0')
        self.playlist = playlist
    def run(self):
        for event in self.dev.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keystate == KeyEvent.key_down:
                    print(key_event.keycode)
                    command = self.playlist.playlist['keys'][key_event.keycode]
                    if(command is not None):
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

