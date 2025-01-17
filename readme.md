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
pip install .
```

## 🎥 Usage

On UNIX-like systems (incl. WSL),
you can run the tool by running the following command:

```bash
video-tagger <video_path> -o <output_path>
```

This reads the video from `video_path` and writes the tags to `output_path`.

If the output file already exists, the tool will ask for confirmation to
overwrite. If you want to append to the output file, use the `-a` option.

We have provided a test video `fireworks-kanemori.mp4` in the `media` directory.
You can run the tool by running the following command:

```bash
# in the project root directory
video-tagger media/fireworks-kanemori.mp4 -o csv/tags.csv
```

Check [media/media-sources.md](media/media-sources.md)
for the source and license of the video.

### Playback Controls

- Play or pause the video with the space bar.
- Jump forward or backward by 10 seconds with the right and left arrow keys.
- Slow down the video with the `,` or `<` key,
  and speed up the video with the `.` or `>` key.
  The available playback speeds are
  `[0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]`,
  with the default speed being `1.0`.

### Config

Playback controls can be customized in the `config.toml` file. When the program
is run, it looks for `config.toml` in the current directory, then in the
`~/.config/video-tagger/` directory. If no config file is found, it uses the
default config. Alternatively, you can specify a custom config file by using
the `-c` option.

We have provided an example of the config file in `config.default.toml` in the
project root directory, which also shows the default values.
To customize the playback controls, you can copy this file to `config.toml` and
modify the values. If you only want to change some of the values,
you can omit the other values so that the default values will be used.

### Tagging

- Add a tag by typing a letter or digit ([A-Za-z0-9]).
  Non-alphanumeric characters will be ignored.
- The time will be printed to the console in the format `<char>,<HH:MM:SS.MS>`.
- Pipe the output to a csv file to save the tags.
- Delete the last tag with the `Backspace` key. By default, the program buffers
  the last 1000 tags, which means that the user can delete up to 1000 latest
  tags. If the buffer is exhausted because the user deleted all tags, the
  program will print a warning message.

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
