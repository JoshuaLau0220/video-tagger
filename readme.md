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

We have provided a test video in the `media` directory.
You can run the tool by running the following command:

```bash
python3 video-tagger/main.py media/fireworks-kanemori.mp4 > tags.csv
```

This video, shot by Kanemori and obtained from
[Pixabay](https://pixabay.com/users/kanenori-4749850/?utm_source=link-attribution&utm_medium=referral&utm_campaign=video&utm_content=225661),
is licensed under the CC0 license.

Controls:

- Play or pause the video with the space bar.
- Jump forward or backward with the right and left arrow keys.
- Add a tag by typing a letter or digit ([A-Za-z0-9]).
  Non-alphanumeric characters will be ignored.
- The time will be printed to the console in the format `<char>,<HH:MM:SS.MS>`.
- Pipe the output to a csv file to save the tags.

## 🔧 Troubleshooting

### Windows (WSL 2)

This tool is developed on MacOS. For Windows users, we recommend using WSL.
Please make sure that your environment is set up correctly as follows:

- WSL is version 2.
- Set up X11 forwarding. Install `xclock` by running
  `sudo apt install x11-apps`, and run `xclock` to check if it works. If not,
  - you may need to install `vcxsrv` or other X11 server software on Windows.
  - you may need to set up `DISPLAY` environment variable.
    - Run `echo $DISPLAY` to check if it is set.
    - If not, you can set it by running `export DISPLAY=:0` in your shell.

Here are some tricky issues we have encountered on our side:

- <details>
  <summary>`No QtMultimedia backends found` error</summary>

  If you encounter the following error:

  ```
  No QtMultimedia backends found. Only QMediaDevices, QAudioDevice, QSoundEffect, QAudioSink, and QAudioSource are available.
  Failed to initialize QMediaPlayer "Not available"
  Failed to create QVideoSink "Not available"
  ...
  ```

  This may be due to the fact that the native `ffmpeg` in WSL Ubuntu does
  not work with `PyQt6`. To check if this is the case, rerun the script,
  prepending `QT_DEBUG_PLUGINS=1` to the command:

  ```bash
  QT_DEBUG_PLUGINS=1 python3 video-tagger/main.py <video_path> 2> debug.log
  ```

  Then, check the `debug.log` file. If you see something like the following:

  ```bash
  qt.core.plugin.loader: QLibraryPrivate::loadPlugin failed on "$CONDA_PREFIX/lib/python3.12/site-packages/PyQt6/Qt6/plugins/multimedia/libffmpegmediaplugin.so" : "Cannot load library $CONDA_PREFIX/lib/python3.12/site-packages/PyQt6/Qt6/plugins/multimedia/libffmpegmediaplugin.so: libavformat.so.61: cannot open shared object file: No such file or directory"
  ```

  This means that the native `ffmpeg` in WSL Ubuntu does not work with `PyQt6`.
  You can verify if this is the case by running the following command, and check
  if the output contains some `not found` messages.

  ```bash
  ldd $CONDA_PREFIX/lib/python3.12/site-packages/PyQt6/Qt6/plugins/multimedia/libffmpegmediaplugin.so | grep "not found"
  ```

  Our experience is that installing `ffmpeg` via conda fixes the issue. Run

  ```bash
  conda install -c conda-forge ffmpeg
  ```

  and add the following line to the activation script of your conda environment:

  ```bash
  # in $CONDA_PREFIX/etc/conda/activate.d/
  export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"
  ```

  After that, deactivate and reactivate the conda environment.
  This should force PyQt6 to use the correct libraries.
  </details>
