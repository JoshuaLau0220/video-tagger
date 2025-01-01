import sys
import os
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout, QSlider, QSpacerItem, QSizePolicy
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import Qt

class EmojiButton(QPushButton):
    def __init__(self, emoji):
        super().__init__()
        self.setFixedSize(25, 25)
        self.setText(emoji)
        # Set button style
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);  /* Light shading on hover */
            }
        """)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

class VideoPlayer(QWidget):
    def __init__(self, video_path):
        super().__init__()
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        self.setWindowTitle("Video Tagger")
        self.setGeometry(100, 100, 800, 600)
        
        self.video_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.video_player.setVideoOutput(self.video_widget)
        
        self.play_button = EmojiButton("▶️")
        self.play_button.clicked.connect(self.toggle_play_pause)
        
        self.forward_button = EmojiButton("⏩")
        self.forward_button.clicked.connect(self.jump_forward)

        self.backward_button = EmojiButton("⏪")
        self.backward_button.clicked.connect(self.jump_backward)
        
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setFixedSize(125, 25)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # Create a horizontal layout for the buttons and time label
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        button_layout.addSpacerItem(QSpacerItem(125, 25, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        button_layout.addWidget(self.backward_button)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.forward_button)
        button_layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Create a widget to contain the button layout and set its fixed height
        button_container = QWidget()
        button_container.setLayout(button_layout)
        button_container.setFixedHeight(25)

        # Create a slider for video position
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)  # Initial range, will be updated when video loads
        self.position_slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.position_slider.sliderMoved.connect(self.set_position)
        # TODO: when clicked, set the position to the slider value

        # Connect slider's value change to update the time label
        self.position_slider.valueChanged.connect(self.update_time_label)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addWidget(self.position_slider)  # Add the slider to the layout
        layout.addWidget(button_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)
        
        self.video_player.setSource(QUrl.fromLocalFile(video_path))
        
        self.video_player.positionChanged.connect(self.update_position_slider)
        self.video_player.durationChanged.connect(self.update_duration)

    def toggle_play_pause(self):
        if self.video_player.isPlaying():
            self.video_player.pause()
            self.play_button.setText("▶️")
        else:
            self.video_player.play()
            self.play_button.setText("⏸️")

    def update_time_label(self):
        position = self.video_player.position() // 1000  # Convert milliseconds to seconds
        duration = self.video_player.duration() // 1000  # Convert milliseconds to seconds
        
        current_time = f"{position // 3600:02}:{(position % 3600) // 60:02}:{position % 60:02}"
        total_time = f"{duration // 3600:02}:{(duration % 3600) // 60:02}:{duration % 60:02}"
        
        self.time_label.setText(f"{current_time} / {total_time}")

    def keyPressEvent(self, event):
        text = event.text()
        
        if event.key() == Qt.Key.Key_Space:
            self.toggle_play_pause()
            return
        
        if event.key() == Qt.Key.Key_Right:
            self.jump_forward()
            return
        
        if event.key() == Qt.Key.Key_Left:
            self.jump_backward()
            return

        if len(text) == 1 and text[0].isalnum():
            # seconds is enough
            video_position = self.video_player.position()  # Get video position in milliseconds
            milliseconds = video_position % 1000
            seconds = (video_position // 1000) % 60
            minutes = (video_position // (1000 * 60)) % 60
            hours = (video_position // (1000 * 60 * 60)) % 24
            timestamp = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
            print(f"{event.text()},{timestamp}")

    def jump_forward(self):
        new_position = self.video_player.position() + 10000  # 10 seconds forward
        self.video_player.setPosition(new_position)

    def jump_backward(self):
        new_position = self.video_player.position() - 10000  # 10 seconds backward
        self.video_player.setPosition(max(0, new_position))  # Ensure position is not negative

    def update_position_slider(self, position):
        self.position_slider.setValue(position)

    def update_duration(self, duration):
        self.position_slider.setRange(0, duration)

    def set_position(self, position):
        self.video_player.setPosition(position)
        self.update_time_label()  # Update the time label when the slider is moved

def main(): 
    # read video from sys.argv
    if len(sys.argv) != 2:
        print("Usage: python main.py <video_path>", file=sys.stderr)
        return 1
    
    video_path = sys.argv[1]
    print(f"Loading video from {video_path}...", file=sys.stderr)
    
    try:
        app = QApplication(sys.argv)
        player = VideoPlayer(video_path)
        player.show()
        return app.exec()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    

if __name__ == "__main__":
    sys.exit(main())