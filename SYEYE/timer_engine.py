from PyQt6.QtCore import QObject, QTimer, pyqtSignal

class TimerState:
    FOCUS = "FOCUS"
    BREAK = "BREAK"
    WAITING = "WAITING"
    PAUSED = "PAUSED"

class TimerEngine(QObject):
    time_updated = pyqtSignal(int)
    state_changed = pyqtSignal(str)
    focus_ended = pyqtSignal()
    break_ended = pyqtSignal()

    def __init__(self, focus_duration=1800, break_duration=420):
        super().__init__()
        self.focus_duration = focus_duration
        self.break_duration = break_duration
        
        self.current_state = TimerState.PAUSED
        self.previous_state = TimerState.FOCUS
        self.time_remaining = self.focus_duration

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)

    def start(self):
        if self.current_state == TimerState.WAITING:
            self.current_state = TimerState.FOCUS
            self.time_remaining = self.focus_duration
            self.state_changed.emit(self.current_state)
        
        if self.current_state == TimerState.PAUSED:
            self.current_state = self.previous_state
            self.state_changed.emit(self.current_state)

        self.timer.start()

    def pause(self):
        if self.current_state in (TimerState.FOCUS, TimerState.BREAK):
            self.timer.stop()
            self.previous_state = self.current_state
            self.current_state = TimerState.PAUSED
            self.state_changed.emit(self.current_state)

    def skip(self):
        self.timer.stop()
        if self.current_state in (TimerState.FOCUS, TimerState.PAUSED):
            # شغل -> بريك
            self.current_state = TimerState.BREAK
            self.time_remaining = self.break_duration
            self.state_changed.emit(self.current_state)
            self.timer.start()
            self.focus_ended.emit() 
            
        elif self.current_state == TimerState.BREAK:
            # بريك -> شغل
            self.current_state = TimerState.FOCUS
            self.time_remaining = self.focus_duration
            self.state_changed.emit(self.current_state)
            self.timer.start()
            
        elif self.current_state == TimerState.WAITING:
            self.current_state = TimerState.FOCUS
            self.time_remaining = self.focus_duration
            self.state_changed.emit(self.current_state)
            self.timer.start()

    def reset_to_waiting(self):
        self.timer.stop()
        self.current_state = TimerState.WAITING
        self.state_changed.emit(self.current_state)

    def _tick(self):
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.time_updated.emit(self.time_remaining)
        else:
            self.timer.stop()
            if self.current_state == TimerState.FOCUS:
                self._handle_focus_end()
            elif self.current_state == TimerState.BREAK:
                self._handle_break_end()

    def _handle_focus_end(self):
        self.focus_ended.emit()
        self.current_state = TimerState.BREAK
        self.time_remaining = self.break_duration
        self.state_changed.emit(self.current_state)
        self.timer.start()

    def _handle_break_end(self):
        self.break_ended.emit()
        self.reset_to_waiting()

    def update_durations(self, focus, break_time):
        self.focus_duration = focus
        self.break_duration = break_time