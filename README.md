# Video Silence Cutter

A desktop application that detects and removes silence segments in videos. The app lets you preview each silence segment and choose which ones to remove.

## Features

- Detect silence segments in video files with customizable threshold and duration
- Visual waveform display showing audio and highlighting silence areas
- Preview each silence segment before deciding to cut it
- Select/deselect which silence segments to remove
- Visual highlighting of silence segments during preview
- Process the video to create a new version with selected silence segments removed

## Requirements

- Python 3.7+
- Required Python packages (install using `pip install -r requirements.txt`):
  - moviepy
  - pydub
  - PyQt5
  - numpy
  - opencv-python
  - matplotlib
- FFmpeg must be installed and available in your system PATH

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Make sure FFmpeg is installed on your system:
   - **Windows**: Download from [FFmpeg.org](https://ffmpeg.org/download.html) and add to your PATH
   - **macOS**: Install via Homebrew: `brew install ffmpeg`
   - **Linux**: Install via your package manager (e.g., `apt install ffmpeg`)

## Usage

1. Run the application:

   ```
   python silence_cutter.py
   ```

2. Click "Select Video" to choose a video file for silence detection

3. Adjust the silence threshold and minimum silence duration:

   - **Silence Threshold**: Lower values (more negative) detect quieter sounds as silence
   - **Minimum Silence Duration**: The minimum length of silence to detect (in milliseconds)

4. Click "Detect Silence" to analyze the video

5. Review the detected silence segments:

   - The audio waveform will display with silence areas highlighted in red
   - Click "Preview" to watch a short clip of each silence segment
   - Check/uncheck boxes to select which silence segments to remove
   - Use "Select All" or "Deselect All" to quickly change multiple selections

6. Click "Process and Save Video" to create a new video with the selected silence segments removed

7. Choose where to save the output video file

## Troubleshooting

- If no silence is detected, try adjusting the silence threshold to a lower (more negative) value
- For videos with background noise, using a higher threshold may help
- If processing is slow, try using shorter videos or increasing the minimum silence duration

### FFMPEG Issues

If you encounter errors like "Error opening output file" or "Broken pipe":

1. Make sure FFmpeg is correctly installed and in your PATH
2. Restart the application after installation
3. Try using a different video format (MP4 files usually work best)
4. On Windows, try running the application as administrator
5. Check if your antivirus or firewall is blocking the creation of temporary files

## Waveform Display Issues

If the waveform display is not showing:

1. Make sure FFmpeg is properly installed and accessible. You can use the included `debug_ffmpeg.py` tool to test:

   ```
   python debug_ffmpeg.py your_video_file.mp4
   ```

   This will attempt to extract audio, analyze it, and create a waveform visualization. It will also show detailed logs about what's happening.

2. If debug_ffmpeg.py successfully creates a waveform but the main app doesn't, it may be related to temporary file handling. Try running the app directly from the command line:

   ```
   python silence_cutter.py
   ```

3. If you get errors about temporary files, make sure your system's temp directory is accessible and has enough free space.

## Preview Functionality Issues

If preview functionality isn't working:

1. Test FFmpeg's ability to create video clips using the debug tool:

   ```
   python debug_ffmpeg.py your_video_file.mp4
   ```

   This will create a preview of the first detected silence segment.

2. Make sure your system has the required codecs to play the video format.

## FFmpeg Not Found

If you get errors about FFmpeg not being found:

1. Make sure FFmpeg is installed properly:

   - Either in the system PATH
   - In C:\ffmpeg\bin
   - Or in the same directory as the application

2. If using the PowerShell installer, run it as Administrator:

   ```
   powershell -ExecutionPolicy Bypass -File install_ffmpeg.ps1
   ```

3. Alternatively, download FFmpeg from the official website (https://ffmpeg.org/download.html) and extract it to C:\ffmpeg or to the application folder.

# Command Line Usage

You can also run the application from the command line with a video file:

```
python silence_cutter.py path/to/your/video.mp4
```

Or use the debug utility to test FFmpeg functionality:

```
python debug_ffmpeg.py path/to/your/video.mp4
```

The debug utility will:

1. Extract audio from the video
2. Detect silent segments
3. Create a waveform visualization with silence highlighted
4. Generate a preview of the first silence segment

This is useful for diagnosing issues with FFmpeg integration or audio extraction.

## License

MIT License
