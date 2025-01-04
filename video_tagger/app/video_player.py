import os
from importlib.resources import files
from collections import deque

from PyQt6.QtWidgets import QVBoxLayout, QWidget, \
     QLabel, QHBoxLayout, QSlider
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, Qt

from video_tagger.util import CSVLine
from video_tagger.app.ui import ImageButton

def to_timestamp_ms(milliseconds):
    hours = milliseconds // (1000 * 60 * 60)
    minutes = (milliseconds // (1000 * 60)) % 60
    seconds = (milliseconds // 1000) % 60
    milliseconds = milliseconds % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

def to_timestamp_s(seconds):
    return f"{seconds // 3600:02}:{(seconds % 3600) // 60:02}:{seconds % 60:02}"
        
class HSlider(QSlider):
    def __init__(self):
        super().__init__(Qt.Orientation.Horizontal)
        # Set initial range. This will be updated when video loads
        self.setRange(0, 0)  
        # don't steal focus from the video player
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus) 

class VideoPlayer(QWidget):
    def __init__(self, video_path, file_stream, config):
        super().__init__()
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        self.file_stream = file_stream
        self.config = config
        
        self.buffer = deque(maxlen=self.config.buffer_size)
        self.current_playback_speed_idx = self.config.default_speed_idx
        
        
        # set up basic information for the window
        self.setWindowTitle("Video Tagger")
        self.setGeometry(100, 100, 800, 600)
        
        self.video_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.video_player.setVideoOutput(self.video_widget)
        self.video_player.setSource(QUrl.fromLocalFile(video_path))
        
        self.video_player.setPlaybackRate(
            self.config.playback_speeds[self.current_playback_speed_idx])
        
        self.play_button = ImageButton(
            str(files("video_tagger.media.icons") / "play.svg"), 
            self.toggle_play_pause)
        self.forward_button = ImageButton(
            str(files("video_tagger.media.icons") / "speed-up.svg"), 
            self.speed_up)
        self.backward_button = ImageButton(
            str(files("video_tagger.media.icons") / "slow-down.svg"), 
            self.slow_down)
        
        self.speed_label = QLabel(self.to_playback_speed_str(
            self.current_playback_speed_idx))
        self.time_label = QLabel("00:00:00 / 00:00:00")
        

        # Create a slider for video position
        self.position_slider = HSlider()
        
        # Connect slider's value change to update the time label
        self.position_slider.sliderMoved.connect(self.set_position)
        self.position_slider.valueChanged.connect(self.update_time_label)
        self.video_player.positionChanged.connect(self.update_position_slider)
        self.video_player.durationChanged.connect(self.update_duration)
        self.setup_layout()
        
    def closeEvent(self, event):
        if self.buffer and self.file_stream is not None:
            for csv_line in self.buffer:
                self.file_stream.write(f"{csv_line}\n")
        event.accept()
        
    def to_playback_speed_str(self, speed_idx):
        return f"Speed: {self.config.playback_speeds[speed_idx]:.2f}x"

    def toggle_play_pause(self):
        if self.video_player.isPlaying():
            self.video_player.pause()
            self.play_button.set_icon(
                    str(files("video_tagger.media.icons") / "play.svg"))
        else:
            self.video_player.play()
            self.play_button.set_icon(
                str(files("video_tagger.media.icons") / "pause.svg"))
            
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
        
        if event.key() == Qt.Key.Key_Comma or \
           event.key() == Qt.Key.Key_Less:
            self.slow_down()
            return
        
        if event.key() == Qt.Key.Key_Period or \
           event.key() == Qt.Key.Key_Greater:
            self.speed_up()
            return
    
        if event.key() == Qt.Key.Key_Backspace:
            self.pop_csv_line()
            return

        text = event.text()
        # checks if the key pressed is a single alphanumeric character
        if len(text) == 1 and text[0].isalnum():
            self.add_csv_line(text)
            
    
    
    def add_csv_line(self, text):
        video_position = self.video_player.position()
        timestamp = to_timestamp_ms(video_position)
        csv_line = CSVLine(text, timestamp)
        print(csv_line, flush=True)                
        # if full, pop the oldest line and write to file
        if len(self.buffer) == self.config.buffer_size:
            popped_csv_line = self.buffer.popleft()
            if self.file_stream is not None:
                self.file_stream.write(f"{popped_csv_line}\n")
        # now add the new line to the buffer
        self.buffer.append(csv_line)

    def pop_csv_line(self):
        if len(self.buffer) == 0:
            print("Warning: No CSV lines in buffer.", flush=True)
            return
        csv_line = self.buffer.pop()
        print(f"[DELETED] {csv_line}", flush=True)

    def jump_forward(self):
        new_position = self.video_player.position() + self.config.jump_interval
        self.video_player.setPosition(new_position)

    def jump_backward(self):
        new_position = self.video_player.position() - self.config.jump_interval
        self.video_player.setPosition(max(0, new_position))
        
    def update_playback_speed(self, speed_idx):
        self.current_playback_speed_idx = speed_idx
        self.video_player.setPlaybackRate(
            self.config.playback_speeds[self.current_playback_speed_idx])
        
    def slow_down(self):
        new_speed_idx = max(0, self.current_playback_speed_idx - 1)
        self.update_playback_speed(new_speed_idx)
        self.speed_label.setText(self.to_playback_speed_str(new_speed_idx))
        
    def speed_up(self):
        new_speed_idx = min(len(self.config.playback_speeds) - 1, 
                                      self.current_playback_speed_idx + 1)
        self.update_playback_speed(new_speed_idx)
        self.speed_label.setText(self.to_playback_speed_str(new_speed_idx))
    
    def reset_playback_speed(self):
        self.update_playback_speed(self.config.default_speed_idx)
        
    def update_position_slider(self, position):
        self.position_slider.setValue(position)

    def update_duration(self, duration):
        self.position_slider.setRange(0, duration)

    def set_position(self, position):
        self.video_player.setPosition(position)
        self.update_time_label()  # Update the time label when the slider is move
    
    def setup_layout(self):
        self.speed_label.setFixedSize(100, 25)
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignLeft | 
                                     Qt.AlignmentFlag.AlignVCenter)
        
        self.time_label.setFixedSize(125, 25)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight | 
                                     Qt.AlignmentFlag.AlignVCenter)
        
        # Create a horizontal layout for the buttons and time label
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins


        button_layout.addSpacing(25)
        button_layout.addWidget(
            self.speed_label, alignment=Qt.AlignmentFlag.AlignVCenter)
        button_layout.addSpacing(25)
        button_layout.addWidget(self.backward_button)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.forward_button)
        button_layout.addSpacing(25)
        button_layout.addWidget(
            self.time_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Create a widget to contain the button layout and set its fixed height
        button_container = QWidget()
        button_container.setLayout(button_layout)
        button_container.setFixedHeight(25)
        
        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addWidget(self.position_slider)  # Add the slider to the layout
        layout.addWidget(
            button_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)