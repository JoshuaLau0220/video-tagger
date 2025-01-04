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
    parser.add_argument("-c", "--config", type=str, default="config.toml",
                        help="path to the config file")
    
    return parser
    
        
def main(): 
    parser = get_parser()
    
    args = parser.parse_args()
    
    config = Config(args.config)
    
    # if not appending, checks if the output file exists. If so, asks for 
    # confirmation to overwrite.
    
    if args.output is not None and not args.append:
        if os.path.exists(args.output):
            print(f"Output file {args.output} already exists. Overwrite? (y/N)", 
                  flush=True)
            if input() != "y":
                print("Note: use `-a` if you want to append to the file.", 
                      flush=True)
                return 1
            
    mode = "w" if not args.append else "a"
    
    file_stream = open(args.output, mode) if args.output is not None else None

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