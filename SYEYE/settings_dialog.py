import json
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpinBox, QPushButton, QSlider, QFileDialog, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("SYEYE - Settings")
        self.setFixedSize(350, 380)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
            }
            QSpinBox {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
            QGroupBox {
                border: 1px solid #555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QSlider::groove:horizontal {
                background: #555;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #4a90d9;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        title = QLabel("⚙ Settings")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Timer Settings
        timer_group = QGroupBox("Timer Duration (minutes)")
        timer_layout = QVBoxLayout(timer_group)
        timer_layout.setSpacing(8)

        focus_row = QHBoxLayout()
        focus_row.addWidget(QLabel("Focus Time:"))
        self.focus_spin = QSpinBox()
        self.focus_spin.setRange(1, 120)
        self.focus_spin.setValue(self.config.get("focus_duration", 1800) // 60)
        focus_row.addWidget(self.focus_spin)
        focus_row.addWidget(QLabel("min"))
        timer_layout.addLayout(focus_row)

        break_row = QHBoxLayout()
        break_row.addWidget(QLabel("Break Time:"))
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 60)
        self.break_spin.setValue(self.config.get("break_duration", 420) // 60)
        break_row.addWidget(self.break_spin)
        break_row.addWidget(QLabel("min"))
        timer_layout.addLayout(break_row)

        layout.addWidget(timer_group)

        # Sound Settings
        sound_group = QGroupBox("Sound Settings")
        sound_layout = QVBoxLayout(sound_group)
        sound_layout.setSpacing(8)

        vol_row = QHBoxLayout()
        vol_row.addWidget(QLabel("Volume:"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.config.get("volume", 100))
        self.vol_label = QLabel(f"{self.volume_slider.value()}%")
        vol_row.addWidget(self.volume_slider)
        vol_row.addWidget(self.vol_label)
        sound_layout.addLayout(vol_row)

        self.volume_slider.valueChanged.connect(
            lambda v: self.vol_label.setText(f"{v}%")
        )

        sound_file_row = QHBoxLayout()
        sound_file_row.addWidget(QLabel("Sound File:"))
        self.sound_path = self.config.get("sound_path", "assets/alert.wav")
        self.sound_label = QLabel(os.path.basename(self.sound_path))
        self.sound_label.setFixedWidth(120)
        self.sound_label.setStyleSheet("color: #aaa; font-size: 11px;")
        sound_file_row.addWidget(self.sound_label)
        
        btn_browse = QPushButton("Browse")
        btn_browse.setFixedWidth(70)
        btn_browse.setStyleSheet("font-size: 11px; padding: 4px 8px;")
        btn_browse.clicked.connect(self.browse_sound)
        sound_file_row.addWidget(btn_browse)
        sound_layout.addLayout(sound_file_row)

        layout.addWidget(sound_group)

        # Opacity
        opacity_row = QHBoxLayout()
        opacity_row.addWidget(QLabel("Window Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(int(self.config.get("opacity", 0.95) * 100))
        self.opacity_label = QLabel(f"{self.opacity_slider.value()}%")
        opacity_row.addWidget(self.opacity_slider)
        opacity_row.addWidget(self.opacity_label)
        layout.addLayout(opacity_row)

        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )

        # Buttons
        btn_row = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setStyleSheet("background-color: #666;")
        
        btn_save.clicked.connect(self.save_settings)
        btn_cancel.clicked.connect(self.reject)
        
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

    def browse_sound(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Sound File", "", "WAV Files (*.wav);;All Files (*.*)"
        )
        if path:
            self.sound_path = path
            self.sound_label.setText(os.path.basename(path))

    def save_settings(self):
        self.config["focus_duration"] = self.focus_spin.value() * 60
        self.config["break_duration"] = self.break_spin.value() * 60
        self.config["volume"] = self.volume_slider.value()
        self.config["opacity"] = self.opacity_slider.value() / 100
        self.config["sound_path"] = self.sound_path
        
        try:
            with open("config.json", "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception:
            pass
        
        self.accept()