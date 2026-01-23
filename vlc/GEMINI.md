# VLC Subtitle Troubleshooting Session

## Directory Overview

This directory (`/home/tthongs/builds_tthongs/tasks_aa_ii/vlc/`) was used as a temporary workspace to troubleshoot a VLC subtitle display issue on a CachyOS system. The primary goal was to diagnose why subtitles were not appearing during video playback in VLC, even when explicitly applied.

## Key Files

*   `test.mp4`: A short, black-screen video file created using `ffmpeg`. This was generated to provide a controlled environment for testing VLC's subtitle rendering without external video factors.
*   `test.srt`: A simple SubRip (SRT) subtitle file containing a single line of text. This was created to be used in conjunction with `test.mp4` to verify VLC's ability to display subtitles.

## Usage

These files were created and used to attempt to reproduce and diagnose a reported issue where VLC was not displaying subtitles. The `vlc -vvv --sub-file test.srt test.mp4` command was used to play the test video with the test subtitle, enabling verbose logging to capture diagnostic information.

The troubleshooting process involved:
1. Checking VLC package dependencies (confirming `vlc-plugin-freetype`, `vlc-plugin-ass`, `vlc-plugin-srt` were installed).
2. Listing system fonts (`fc-list`) to ensure fonts were available for rendering.
3. Running VLC with verbose logging to identify specific error messages related to subtitle decoding and rendering.
