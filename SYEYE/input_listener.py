from PyQt6.QtCore import QThread, pyqtSignal
from pynput import mouse, keyboard

class InputListener(QThread):
    interaction_detected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._running = False
        self._mouse_listener = None
        self._keyboard_listener = None

    def run(self):
        self._running = True
        
        def on_action(*args):
            if self._running:
                self.interaction_detected.emit()
                self.stop_listening()

        self._mouse_listener = mouse.Listener(on_move=on_action, on_click=on_action)
        self._keyboard_listener = keyboard.Listener(on_press=on_action)
        
        self._mouse_listener.start()
        self._keyboard_listener.start()

        while self._running:
            self.msleep(100)

    def stop_listening(self):
        self._running = False
        if self._mouse_listener:
            self._mouse_listener.stop()
        if self._keyboard_listener:
            self._keyboard_listener.stop()