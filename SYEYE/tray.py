from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal, QObject
import os

class SystemTrayManager(QObject):
    show_window = pyqtSignal()
    hide_window = pyqtSignal()
    toggle_pause = pyqtSignal()
    exit_app = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        icon_path = "assets/icon.png"
        self.icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon.fromTheme("appointment-soon")
        
        self.tray = QSystemTrayIcon(self.icon, parent)
        self.tray.setToolTip("SYEYE - Protect Your Eyes")
        
        self.menu = QMenu()
        
        self.action_show = QAction("Show/Hide")
        self.action_toggle = QAction("Start/Pause")
        self.action_exit = QAction("Exit")
        
        self.menu.addAction(self.action_show)
        self.menu.addAction(self.action_toggle)
        self.menu.addSeparator()
        self.menu.addAction(self.action_exit)
        
        self.tray.setContextMenu(self.menu)
        
        self.action_show.triggered.connect(self._on_show_hide)
        self.action_toggle.triggered.connect(self.toggle_pause.emit)
        self.action_exit.triggered.connect(self.exit_app.emit)
        self.tray.activated.connect(self._on_tray_activated)

    def show(self):
        self.tray.show()

    def _on_show_hide(self):
        self.show_window.emit()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_window.emit()