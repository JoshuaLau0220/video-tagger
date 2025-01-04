import os
import toml

class Config:
    def __init__(self, config_path="config.toml"):
        if not os.path.exists(config_path):
            self.jump_interval = 10000
            self.playback_speeds = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]
            self.default_speed_idx = 3
            self.buffer_size = 1000
        else:
            with open(config_path, "r") as f:
                config = toml.load(f)
            self.jump_interval = config["jump_interval"] \
                if "jump_interval" in config \
                else 10000
            self.playback_speeds = config["playback_speeds"] \
                if "playback_speeds" in config \
                else [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]
            self.default_speed_idx = config["default_speed_idx"] \
                if "default_speed_idx" in config \
                else 3
            self.buffer_size = config["buffer_size"] \
                if "buffer_size" in config \
                else 1000