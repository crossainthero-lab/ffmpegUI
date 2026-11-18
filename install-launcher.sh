#!/bin/sh
# Install a launcher for the current checkout; keep this folder in place.
set -eu
app_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
case "$app_dir" in
  *'"'*|*'%'*|*'\'*|*'`'*|*'$'*) printf '%s\n' 'The install path contains unsupported characters.' >&2; exit 1;;
esac
command -v python3 >/dev/null || { echo 'Python 3 is required.' >&2; exit 1; }
command -v ffmpeg >/dev/null || { echo 'FFmpeg is required.' >&2; exit 1; }
applications_dir=${XDG_DATA_HOME:-"$HOME/.local/share"}/applications
mkdir -p "$applications_dir"
cat > "$applications_dir/ffmpegui.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=ffmpegUI
Comment=Convert video and audio files locally
Exec=python3 "$app_dir/app.py"
Icon=$app_dir/icon.svg
Terminal=false
Categories=AudioVideo;Video;Utility;
Keywords=ffmpeg;convert;video;audio;mp4;mov;
StartupNotify=false
DESKTOP
chmod 644 "$applications_dir/ffmpegui.desktop"
if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database "$applications_dir"; fi
printf 'Installed launcher: %s\n' "$applications_dir/ffmpegui.desktop"
