import os

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon, QPixmap, QColor
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QApplication

def is_dark_mode():
    palette = QApplication.palette()
    return palette.color(palette.ColorRole.Window).value() < 128

class ImageButton(QPushButton):
    def __init__(self, icon_path, callback):
        if not os.path.exists(icon_path):
            raise FileNotFoundError(f"Icon file not found: {icon_path}")
        
        super().__init__()
        self.setFixedSize(25, 25)
        self.setIconSize(QSize(25, 25))
        self.set_icon(icon_path)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.clicked.connect(callback)

    def invert_icon_brightness(self, icon):
        # Create a pixmap from the icon
        pixmap = icon.pixmap(self.iconSize())
        image = pixmap.toImage()
        
        # Invert the brightness of the image
        for y in range(image.height()):
            for x in range(image.width()):
                color = image.pixelColor(x, y)
                inverted_color = QColor(
                    255 - color.red(), 
                    255 - color.green(), 
                    255 - color.blue(), 
                    color.alpha())
                image.setPixelColor(x, y, inverted_color)
        
        # Return a new QIcon with the inverted image
        return QIcon(QPixmap.fromImage(image))
    
    def set_icon(self, icon_path):
        if not os.path.exists(icon_path):
            raise FileNotFoundError(f"Icon file not found: {icon_path}")
        if is_dark_mode():
            self.setIcon(self.invert_icon_brightness(QIcon(icon_path)))
        else:
            self.setIcon(QIcon(icon_path))

class EmojiButton(QPushButton):
    def __init__(self, emoji, callback):
        super().__init__()
        self.setFixedSize(25, 25)
        self.setText(emoji)
        self.setStyleSheet("""
            /* Emojis needs no further styling */
            QPushButton {
                background-color: transparent;
                border: none;
            }
            /* lightly highlight the button when hovered */
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.clicked.connect(callback)