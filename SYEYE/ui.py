import json
import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from timer_engine import TimerState

class MainWindow(QMainWindow):
    close_clicked = pyqtSignal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.old_pos = None
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Window
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setFixedSize(300, 200)
        
        icon_path = "assets/icon.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.move(self.config.get("window_x", 100), self.config.get("window_y", 100))
        self.setWindowOpacity(self.config.get("opacity", 0.95))

        self.init_ui()
        self.apply_theme(TimerState.FOCUS)

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ===== البار العلوي =====
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(30)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(6, 2, 2, 2)
        title_layout.setSpacing(4)

        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setFixedSize(26, 26)
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setToolTip("Settings")
        title_layout.addWidget(self.btn_settings)

        title_layout.addStretch()

        # زر التصغير
        self.btn_minimize = QPushButton("─")
        self.btn_minimize.setFixedSize(26, 26)
        self.btn_minimize.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_minimize.setToolTip("Minimize")
        self.btn_minimize.clicked.connect(self.showMinimized) 
        title_layout.addWidget(self.btn_minimize)

        # زر الإغلاق
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(26, 26)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setToolTip("Exit")
        self.btn_close.clicked.connect(self.close_clicked.emit)
        title_layout.addWidget(self.btn_close)

        self.main_layout.addWidget(self.title_bar)

        # ===== المحتوى =====
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 2, 10, 10)
        content_layout.setSpacing(6)

        self.timer_label = QLabel("30:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setFont(QFont("Segoe UI", 42, QFont.Weight.Bold))
        content_layout.addWidget(self.timer_label)

        self.slogan_label = QLabel("SYEYE - Save your eyes")
        self.slogan_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slogan_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal))
        content_layout.addWidget(self.slogan_label)

        self.state_label = QLabel("FOCUS TIME")
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_label.setFont(QFont("Segoe UI", 9))
        content_layout.addWidget(self.state_label)

        # الأزرار الثلاثة في الأسفل
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(6)
        
        self.btn_start_pause = QPushButton("▶")
        self.btn_skip = QPushButton("⏭")
        self.btn_reload = QPushButton("🔄")  # نقلنا الريلود هنا
        
        for btn in (self.btn_start_pause, self.btn_skip, self.btn_reload):
            btn.setFixedHeight(36)
            btn.setFixedWidth(88)  # عرض مناسب لـ 3 أزرار
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
            self.btn_layout.addWidget(btn)
            
        content_layout.addLayout(self.btn_layout)
        self.main_layout.addWidget(content_widget)

    def apply_theme(self, state):
        if state == TimerState.FOCUS:
            bg_color = "#4a90d9"; text_color = "#ffffff"; btn_bg = "#3578c0"; title_bg = "#3a7bc8"
        elif state == TimerState.BREAK:
            bg_color = "#ba4949"; text_color = "#ffffff"; btn_bg = "#9e3d3d"; title_bg = "#a03f3f"
        elif state == TimerState.WAITING:
            bg_color = "#4c4c4c"; text_color = "#dddddd"; btn_bg = "#3a3a3a"; title_bg = "#3a3a3a"
        else:
            bg_color = "#d99322"; text_color = "#ffffff"; btn_bg = "#b87b1c"; title_bg = "#b87b1c"

        self.title_bar.setStyleSheet(f"""
            QWidget {{ background-color: {title_bg}; }}
            QPushButton {{ background-color: transparent; color: {text_color}; border: none; border-radius: 4px; font-size: 14px; font-weight: bold; }}
            QPushButton:hover {{ background-color: rgba(255, 255, 255, 0.25); }}
        """)

        self.central_widget.setStyleSheet(f"""
            QWidget {{ background-color: {bg_color}; color: {text_color}; }}
            QPushButton {{ background-color: {btn_bg}; color: {text_color}; border: none; font-weight: bold; font-size: 18px; }}
            QPushButton:hover {{ background-color: rgba(255, 255, 255, 0.25); }}
        """)

    def update_time(self, seconds):
        mins, secs = divmod(seconds, 60)
        self.timer_label.setText(f"{mins:02d}:{secs:02d}")

    def update_state(self, state):
        self.apply_theme(state)
        if state == TimerState.FOCUS:
            self.state_label.setText("FOCUS TIME"); self.btn_start_pause.setText("⏸")
        elif state == TimerState.BREAK:
            self.state_label.setText("BREAK TIME"); self.btn_start_pause.setText("⏸")
        elif state == TimerState.WAITING:
            self.state_label.setText("WAITING..."); self.btn_start_pause.setText("▶")
        elif state == TimerState.PAUSED:
            self.state_label.setText("PAUSED"); self.btn_start_pause.setText("▶")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        self.config["window_x"] = self.x()
        self.config["window_y"] = self.y()
        self.save_config()

    def save_config(self):
        try:
            with open("config.json", "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception: pass

    def closeEvent(self, event):
        event.ignore()