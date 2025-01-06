import sys
import os

from argparse import ArgumentParser
from PyQt6.QtWidgets import QApplication

from video_tagger.util import Config
from video_tagger.app import VideoPlayer

def get_parser():
    parser = ArgumentParser(
        description="Tag video frames by typing letters or digits. "
                    "Read README.md for more details.",
    )
    parser.add_argument("video_path", type=str, 
                        help="path to the video file")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="path to the output file. "
                        "When set, the output will be printed to the file "
                        "as well as the console.")
    parser.add_argument("-a", "--append", action="store_true", 
                        help="append to the output file")
    parser.add_argument("-c", "--config", type=str, default=None,
                        help="path to the config file")
    
    return parser

def get_config_path(config_path):
    home_config_path = os.path.expanduser("~/.config/video-tagger/config.toml")
    if config_path is not None:
        if not os.path.exists(config_path):
            print(f"Error: Config file {config_path} does not exist. "
                  "Falling back to default config...", 
                  file=sys.stderr)
            return None
        return config_path
    elif os.path.exists("config.toml"):
        return "config.toml"
    elif os.path.exists(home_config_path):
        return home_config_path
    else:
        return None
    
def get_config(config_path):
    if config_path is not None:
        print(f"Note: Loading config from {config_path}...", 
              file=sys.stderr)
        config = Config(config_path)
    else:
        print("Note: No config.toml found. Using default config...", 
              file=sys.stderr)
        config = Config()
    return config
        
def main(): 
    parser = get_parser()
    
    args = parser.parse_args()
    
    # if not appending, checks if the output file exists. If so, asks for 
    # confirmation to overwrite.
    
    if args.output is not None and not args.append:
        if os.path.exists(args.output) and sys.stdin.isatty():
            print(f"Output file {args.output} already exists. Overwrite? (y/N)", 
                  file=sys.stderr)
            if input() != "y":
                print("Note: use `-a` if you want to append to the file.", 
                      file=sys.stderr)
                return 1
            
    mode = "w" if not args.append else "a"
    
    if args.output is not None: 
        try:
            file_stream = open(args.output, mode)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    else:
        file_stream = None
        
    config_path = get_config_path(args.config)
    config = get_config(config_path)

    try:
        app = QApplication([])
        player = VideoPlayer(args.video_path, file_stream, config)
        player.show()
        return app.exec()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    

if __name__ == "__main__":
    sys.exit(main())