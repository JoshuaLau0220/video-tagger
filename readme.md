# 🏷️ Video Tagger

This is a simple tool to tag video timestamps with a letter or digit, built with
PyQt6. The tool outputs the tags to the console in the format
`<char>,<HH:MM:SS.MS>`, which can be piped to a csv file to save the tags.
Then, we can write scripts to further process the csv files.

🧪 This is a project I developed for personal use and thus is quite rudimentary.
I'm sharing it here in case it's useful to others. Feel free to
use it as you see fit.

## 📦 Installation

Assuming that you have `conda` installed,
you can install the dependencies by running the following commands:

```bash
conda create -n video-tagger python=3.12
conda activate video-tagger
pip install -r requirements.txt
```

## 🎥 Usage

On UNIX-like systems (incl. WSL),
you can run the tool by running the following command:

```bash
python3 video-tagger/main.py <video_path> > <output_path>
```

Controls:

- Play or pause the video with the space bar.
- Jump forward or backward with the right and left arrow keys.
- Add a tag by typing a letter or digit ([A-Za-z0-9]).
  Non-alphanumeric characters will be ignored.
- The time will be printed to the console in the format `<char>,<HH:MM:SS.MS>`.
- Pipe the output to a csv file to save the tags.
