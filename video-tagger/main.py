import sys
import os
import toml

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, \
    QPushButton, QLabel, QHBoxLayout, QSlider, QSpacerItem, QSizePolicy
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, Qt

def get_jump_interval():
    try:
        with open("config.toml", "r") as f:
            config = toml.load(f)
        return config["jump_interval"]["milliseconds"]
    except FileNotFoundError:
        return 10000
    
def to_timestamp_ms(milliseconds):
    hours = milliseconds // (1000 * 60 * 60)
    minutes = (milliseconds // (1000 * 60)) % 60
    seconds = (milliseconds // 1000) % 60
    milliseconds = milliseconds % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

def to_timestamp_s(seconds):
    return f"{seconds // 3600:02}:{(seconds % 3600) // 60:02}:{seconds % 60:02}"

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
        
class HSlider(QSlider):
    def __init__(self):
        super().__init__(Qt.Orientation.Horizontal)
        # Set initial range. This will be updated when video loads
        self.setRange(0, 0)  
        # don't steal focus from the video player
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus) 

class VideoPlayer(QWidget):
    def __init__(self, video_path):
        super().__init__()
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # set up basic information for the window
        self.setWindowTitle("Video Tagger")
        self.setGeometry(100, 100, 800, 600)
        
        self.video_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.video_player.setVideoOutput(self.video_widget)
        self.video_player.setSource(QUrl.fromLocalFile(video_path))
        
        self.play_button = EmojiButton("▶️", self.toggle_play_pause)
        self.forward_button = EmojiButton("⏩", self.jump_forward)
        self.backward_button = EmojiButton("⏪", self.jump_backward)
        
        self.time_label = QLabel("00:00 / 00:00")
        

        # Create a slider for video position
        self.position_slider = HSlider()
        
        # Connect slider's value change to update the time label
        self.position_slider.sliderMoved.connect(self.set_position)
        self.position_slider.valueChanged.connect(self.update_time_label)
        self.video_player.positionChanged.connect(self.update_position_slider)
        self.video_player.durationChanged.connect(self.update_duration)
        self.setup_layout()

    def toggle_play_pause(self):
        if self.video_player.isPlaying():
            self.video_player.pause()
            self.play_button.setText("▶️")
        else:
            self.video_player.play()
            self.play_button.setText("⏸️")

    def update_time_label(self):
        current_time = to_timestamp_s(self.video_player.position() // 1000)
        total_time = to_timestamp_s(self.video_player.duration() // 1000)
        self.time_label.setText(f"{current_time} / {total_time}")

    def keyPressEvent(self, event):
        
        if event.key() == Qt.Key.Key_Space:
            self.toggle_play_pause()
            return
        
        if event.key() == Qt.Key.Key_Right:
            self.jump_forward()
            return
        
        if event.key() == Qt.Key.Key_Left:
            self.jump_backward()
            return

        text = event.text()
        # checks if the key pressed is a single alphanumeric character
        if len(text) == 1 and text[0].isalnum():
            # count to milliseconds. If it's too fine-grained, we can always 
            # round to the nearest second when processing the output csvs.
            video_position = self.video_player.position()
            timestamp = to_timestamp_ms(video_position)
            print(f"{event.text()},{timestamp}")

    def jump_forward(self):
        new_position = self.video_player.position() + get_jump_interval()
        self.video_player.setPosition(new_position)

    def jump_backward(self):
        new_position = self.video_player.position() - get_jump_interval()
        self.video_player.setPosition(max(0, new_position))

    def update_position_slider(self, position):
        self.position_slider.setValue(position)

    def update_duration(self, duration):
        self.position_slider.setRange(0, duration)

    def set_position(self, position):
        self.video_player.setPosition(position)
        self.update_time_label()  # Update the time label when the slider is moved
        
    def setup_layout(self):
        self.time_label.setFixedSize(125, 25)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight | 
                                     Qt.AlignmentFlag.AlignVCenter)
        
        # Create a horizontal layout for the buttons and time label
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # this spacer puts the play button in the center
        button_layout.addSpacerItem(
            QSpacerItem(125, 25, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        button_layout.addWidget(self.backward_button)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.forward_button)
        button_layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Create a widget to contain the button layout and set its fixed height
        button_container = QWidget()
        button_container.setLayout(button_layout)
        button_container.setFixedHeight(25)
        
        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addWidget(self.position_slider)  # Add the slider to the layout
        layout.addWidget(button_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)
        
        

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