#!/usr/bin/env python3
"""Local, dependency-free browser front end for FFmpeg."""
import argparse
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
import webbrowser

ROOT = Path(__file__).resolve().parent
FORMATS = {
    'mp4': ['-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart'],
    'mov': ['-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k'],
    'mkv': ['-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k'],
    'webm': ['-c:v', 'libvpx-vp9', '-crf', '31', '-b:v', '0', '-c:a', 'libopus'],
    'mp3': ['-vn', '-c:a', 'libmp3lame', '-q:a', '2'],
    'wav': ['-vn', '-c:a', 'pcm_s16le'],
}
TOKEN = secrets.token_urlsafe(32)

class Handler(BaseHTTPRequestHandler):
    def reply(self, status, content, content_type='text/plain; charset=utf-8'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.path != '/':
            return self.reply(404, b'Not found')
        page = (ROOT / 'index.html').read_text(encoding='utf-8').replace('__TOKEN__', TOKEN)
        self.reply(200, page.encode(), 'text/html; charset=utf-8')

    def do_POST(self):
        # A secret and exact Origin check prevent unrelated sites from invoking FFmpeg.
        origin = self.headers.get('Origin', '')
        expected = f'http://127.0.0.1:{self.server.server_port}'
        if origin != expected or not secrets.compare_digest(self.headers.get('X-FFmpegUI-Token', ''), TOKEN):
            return self.reply(403, b'Forbidden')
        fmt = urlsplit(self.path).path.removeprefix('/convert/')
        if not self.path.startswith('/convert/') or fmt not in FORMATS:
            return self.reply(400, b'Unsupported format')
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length <= 0:
                return self.reply(400, b'Choose a file first.')
            with tempfile.TemporaryDirectory(prefix='ffmpegui-') as directory:
                source = Path(directory) / 'input'
                output = Path(directory) / ('output.' + fmt)
                with source.open('wb') as f:
                    remaining = length
                    while remaining:
                        chunk = self.rfile.read(min(1024 * 1024, remaining))
                        if not chunk:
                            raise ValueError('Upload ended unexpectedly.')
                        f.write(chunk)
                        remaining -= len(chunk)
                command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-i', str(source), *FORMATS[fmt], '-y', str(output)]
                result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=7200)
                if result.returncode:
                    message = result.stderr.decode('utf-8', errors='replace')[-4000:] or 'Conversion failed.'
                    return self.reply(422, message.encode())
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Length', str(output.stat().st_size))
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                with output.open('rb') as f:
                    shutil.copyfileobj(f, self.wfile)
        except subprocess.TimeoutExpired:
            self.reply(504, b'Conversion timed out after two hours.')
        except (OSError, ValueError) as exc:
            try:
                self.reply(500, str(exc).encode())
            except OSError:
                pass

    def log_message(self, format, *args):
        pass

def main():
    parser = argparse.ArgumentParser(description='Run ffmpegUI locally')
    parser.add_argument('--port', type=int, default=0, help='Local port (default: automatically selected)')
    parser.add_argument('--no-browser', action='store_true', help='Do not open a browser automatically')
    args = parser.parse_args()
    if not shutil.which('ffmpeg'):
        parser.error('ffmpeg was not found. Install FFmpeg and try again.')
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'ffmpegUI is running at {url}\nPress Ctrl+C to stop.', flush=True)
    if not args.no_browser:
        threading.Timer(0.3, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
