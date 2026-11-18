# ffmpegUI

A simple, local drag-and-drop interface for converting videos with FFmpeg. Choose MP4, MOV, MKV, WebM, MP3, or WAV; the converted file downloads through your browser. Files are processed on your computer and are not uploaded to an external service.

## Requirements

- Linux, macOS, or another system with Python 3.9 or newer
- FFmpeg on your PATH, with the encoders for the formats you use (libx264, AAC, libvpx-vp9, libopus, and libmp3lame)
- A modern web browser

On Ubuntu or Debian, install FFmpeg with `sudo apt install ffmpeg`.

## Run

```bash
python3 app.py
```

Your browser opens automatically. Drag in a file (or click to browse), pick a format, and click **Convert video**. When it finishes, your browser saves the result to its usual download location. Stop the app with Ctrl+C in the terminal.

Use `python3 app.py --no-browser` to open the printed address yourself, or `--port 8000` to choose a port. The server only listens on 127.0.0.1.

Conversions re-encode media; MP3 and WAV extract audio. Large files require enough free disk space for temporary input and output files and enough browser memory to download the result. Temporary files are removed when conversion finishes. Errors from FFmpeg appear in the app.

## Add to the applications menu (Linux)

Run `./install-launcher.sh` from this folder. Then search for **ffmpegUI** in your applications menu. The launcher uses this checkout, so keep the folder in place. To remove the launcher, delete `~/.local/share/applications/ffmpegui.desktop`. Launching the app starts a local server in the background; to stop it, run `pkill -f "python3 .*ffmpegUI/app.py"`.

## License

MIT. FFmpeg is a separate project and is subject to its own licensing terms.
