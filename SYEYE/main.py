import sys
import json
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QLockFile, QDir
from pynput import keyboard

from timer_engine import TimerEngine, TimerState
from ui import MainWindow
from sound_manager import SoundManager
from input_listener import InputListener
from tray import SystemTrayManager
from settings_dialog import SettingsDialog

class SYEYEApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        lock_path = os.path.join(QDir.tempPath(), "syeye_app.lock")
        self.lock_file = QLockFile(lock_path)
        if not self.lock_file.tryLock(100):
            print("SYEYE is already running.")
            sys.exit(0)

        self.load_config()
        
        self.engine = TimerEngine(self.config.get("focus_duration", 1800), 
                                   self.config.get("break_duration", 420))
        self.sound = SoundManager(self.config.get("sound_path", "assets/alert.wav"))
        self.input_listener = InputListener()
        
        self.window = MainWindow(self.config)
        self.tray = SystemTrayManager()

        self.setup_connections()
        self.setup_global_hotkey()
        
        self.window.update_time(self.engine.time_remaining)
        self.window.apply_theme(TimerState.FOCUS)
        self.window.state_label.setText("FOCUS TIME")
        self.window.btn_start_pause.setText("▶ Start")

    def load_config(self):
        default_config = {
            "focus_duration": 1800, "break_duration": 420,
            "volume": 100, "opacity": 0.95, 
            "window_x": 100, "window_y": 100,
            "sound_path": "assets/alert.wav"
        }
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    loaded = json.load(f)
                    for key in default_config:
                        if key not in loaded: loaded[key] = default_config[key]
                    self.config = loaded
            else:
                self.config = default_config
                with open("config.json", "w") as f:
                    json.dump(self.config, f, indent=4)
        except Exception:
            self.config = default_config

    def setup_connections(self):
        self.engine.time_updated.connect(self.window.update_time)
        self.engine.state_changed.connect(self.window.update_state)
        self.engine.focus_ended.connect(self.on_focus_ended)
        self.engine.break_ended.connect(self.on_break_ended)

        self.window.btn_start_pause.clicked.connect(self.toggle_start_pause)
        self.window.btn_skip.clicked.connect(self.engine.skip)
        self.window.btn_settings.clicked.connect(self.open_settings)
        
        # ربط أزرار البار
        self.window.close_clicked.connect(self.exit_application) # زر X
        self.window.btn_reload.clicked.connect(self.reset_app)   # زر ريلود

        self.input_listener.interaction_detected.connect(self.on_user_interaction)
        self.tray.show_window.connect(self.toggle_window_visibility)
        self.tray.toggle_pause.connect(self.toggle_start_pause)
        self.tray.exit_app.connect(self.exit_application)

    def reset_app(self):
        """إعادة ضبط البرنامج كأنه فُتح للتو"""
        self.sound.stop_alarm()
        self.input_listener.stop_listening()
        self.engine.timer.stop()
        
        self.engine.current_state = TimerState.PAUSED
        self.engine.previous_state = TimerState.FOCUS
        self.engine.time_remaining = self.engine.focus_duration
        
        self.window.update_time(self.engine.time_remaining)
        self.window.apply_theme(TimerState.FOCUS)
        self.window.state_label.setText("FOCUS TIME")
        self.window.btn_start_pause.setText("▶ Start")

    def open_settings(self):
        dialog = SettingsDialog(self.config, self.window)
        result = dialog.exec()
        if result == 1:
            self.config = dialog.config
            self.engine.update_durations(
                self.config.get("focus_duration", 1800), 
                self.config.get("break_duration", 420)
            )
            self.sound.sound_path = self.config.get("sound_path", "assets/alert.wav")
            self.window.setWindowOpacity(self.config.get("opacity", 0.95))
            if self.engine.current_state in (TimerState.PAUSED, TimerState.WAITING):
                self.window.update_time(self.engine.time_remaining)

    def setup_global_hotkey(self):
        def on_hotkey():
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, self.toggle_start_pause)
        self.hotkey = keyboard.GlobalHotKeys({'<ctrl>+<alt>+p': on_hotkey})
        self.hotkey.start()

    def toggle_start_pause(self):
        state = self.engine.current_state
        if state in (TimerState.FOCUS, TimerState.BREAK): self.engine.pause()
        elif state in (TimerState.PAUSED, TimerState.WAITING): self.engine.start()

    def on_focus_ended(self):
        self.sound.start_alarm()
        self.input_listener.start()

    def on_break_ended(self):
        self.input_listener.start()

    def on_user_interaction(self):
        state = self.engine.current_state
        if self.sound.is_playing: self.sound.stop_alarm()
        if state == TimerState.WAITING: self.engine.start()

    def toggle_window_visibility(self):
        if self.window.isVisible(): self.window.hide()
        else:
            self.window.show()
            self.window.activateWindow()
            self.window.setWindowState(Qt.WindowState.WindowNoState) # استعادة الحجم الطبيعي

    def exit_application(self):
        """إغلاق قوي ونهائي للبرنامج"""
        self.sound.stop_alarm()
        self.input_listener.stop_listening()
        try: self.hotkey.stop()
        except: pass
        
        self.tray.tray.hide()
        self.app.quit()
        
        # هذا السطر يضمن إغلاق البرنامج فوراً حتى لو علقت Threads في الخلفية
        os._exit(0) 

    def run(self):
        self.window.show()
        self.tray.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = SYEYEApp()
    app.run()