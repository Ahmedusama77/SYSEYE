import threading
import os
import winsound

class SoundManager:
    def __init__(self, sound_path="assets/alert.wav"):
        self.sound_path = sound_path
        self.is_playing = False
        self._thread = None
        self._stop_event = threading.Event()

    def start_alarm(self):
        if self.is_playing:
            return
        self._stop_event.clear()
        self.is_playing = True
        self._thread = threading.Thread(target=self._play_loop, daemon=True)
        self._thread.start()

    def stop_alarm(self):
        if not self.is_playing:
            return
        self._stop_event.set()
        self.is_playing = False
        winsound.PlaySound(None, winsound.SND_PURGE)

    def _play_loop(self):
        while not self._stop_event.is_set():
            try:
                if os.path.exists(self.sound_path):
                    winsound.PlaySound(self.sound_path, winsound.SND_FILENAME | winsound.SND_NODEFAULT)
                else:
                    winsound.Beep(1000, 500)
            except Exception:
                winsound.Beep(1000, 500)
            
            self._stop_event.wait(1.0)