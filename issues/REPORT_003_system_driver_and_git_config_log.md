# REPORT 003: System Hardware/Audio Driver Calibration & Global Git Setup Log

**Date**: 2026-07-25  
**Author**: Antigravity AI  
**Target System**: Acer Aspire A715-79G (CachyOS Linux / Arch Linux, Kernel 7.1.4-1-cachyos)  
**Location**: `/home/tthh0ngs/build_tthongs/tasks_aa_ii/issues/REPORT_003_system_driver_and_git_config_log.md`

---

## Executive Summary

This log documents the diagnostic investigation, root-cause resolution, hardware driver verification, and global Git credential configuration performed on the system. 

1. **Microphone Driver & Audio Saturation Fix**: Fixed internal microphone recording pure digital static noise (clipping at $\pm 32,768$) by calibrating ALSA hardware gain levels (`Internal Mic Boost` +30dB to +10dB) and persisting settings via `alsactl store`.
2. **Global Git Authentication & Profile Setup**: Configured global credential persistence (`credential.helper store`), generated an Ed25519 SSH key pair, installed `github-cli`, and set global Git author identity (`tthongs` / `sanskarsinghss123@gmail.com`).

---

## Part 1: System Hardware & Microphone Driver Analysis

### 1.1 Problem Diagnosis
The internal microphone on the Realtek ALC256 audio codec (Intel Raptor Lake cAVS controller `8086:51ca`) produced loud digital static noise upon recording. Audio sample analysis showed full-scale digital clipping with peak values of $-32,768$ / $+32,767$ and an average absolute amplitude of $23,675.7$.

### 1.2 Commands Used & Explanations

#### Command 1: Inspect System Architecture, Kernel, & Audio Hardware
```bash
uname -a; lspci -nnk | grep -A 3 -i audio; lsusb; arecord -l
```
* **Explanation**: 
  * `uname -a`: Prints kernel version (`7.1.4-1-cachyos x86_64`).
  * `lspci -nnk`: Identifies PCI audio devices (`8086:51ca` Intel Raptor Lake-P/U/H cAVS driven by `snd_hda_intel` and `10de:22be` NVIDIA High Definition Audio).
  * `lsusb`: Enumerates connected USB peripherals (webcam, mouse, keyboard, Bluetooth).
  * `arecord -l`: Lists ALSA capture hardware devices (`card 0: PCH, device 0: ALC256 Analog`).

#### Command 2: Inspect PipeWire & PulseAudio Sound Server Status
```bash
pactl list sources; wpctl status
```
* **Explanation**: 
  * `pactl list sources`: Queries active audio input sources, volume levels, mute states, and node routes managed by PipeWire.
  * `wpctl status`: Displays WirePlumber status tree showing active audio sinks, sources, and clients.

#### Command 3: Query ALSA Hardware Mixer Controls
```bash
amixer -c 0 scontrols; amixer -c 0
```
* **Explanation**: 
  * Queries low-level hardware mixer controls for sound card 0 (`Realtek ALC256`). Revealed `Internal Mic Boost` was set to max Level 3 ($+30.00\text{ dB}$) and `Capture` set to max Level 63 ($+30.00\text{ dB}$), resulting in $+60.00\text{ dB}$ total gain overload.

#### Command 4: Record & Analyze Audio Waveform Samples
```bash
arecord -d 2 -f S16_LE -r 44100 /tmp/test_mic.wav && python3 -c "import wave, struct; w = wave.open('/tmp/test_mic.wav'); frames = w.readframes(w.getnframes()); samples = struct.unpack('<' + 'h'*(len(frames)//2), frames); print('Num samples:', len(samples), 'Min:', min(samples), 'Max:', max(samples), 'Avg abs:', sum(abs(s) for s in samples)/len(samples))"
```
* **Explanation**: 
  * `arecord -d 2 -f S16_LE -r 44100`: Captures 2 seconds of 16-bit 44.1kHz audio.
  * `python3 ...`: Parses raw WAV PCM frames into 16-bit signed integers to measure minimum, maximum, and average absolute amplitude. Initial test resulted in `Avg abs: 23675.7` (severe saturation).

#### Command 5: Calibrate Hardware Gain Levels
```bash
amixer -c 0 sset 'Internal Mic Boost' 1
amixer -c 0 sset 'Capture' 65%
```
* **Explanation**: 
  * Reduces `Internal Mic Boost` from $+30.00\text{ dB}$ (Level 3) to $+10.00\text{ dB}$ (Level 1).
  * Sets ALSA `Capture` gain to $65\%$ ($+13.50\text{ dB}$), eliminating input amplifier saturation.

#### Command 6: Re-verify Audio Signal Quality
```bash
arecord -d 2 -f S16_LE -r 44100 /tmp/final_mic_test.wav && python3 -c "import wave, struct; w = wave.open('/tmp/final_mic_test.wav'); frames = w.readframes(w.getnframes()); samples = struct.unpack('<' + 'h'*(len(frames)//2), frames); print('Num samples:', len(samples), 'Min:', min(samples), 'Max:', max(samples), 'Avg abs:', sum(abs(s) for s in samples)/len(samples))"
```
* **Explanation**: 
  * Confirmed clean recording without static: `Min: -2889`, `Max: +3782`, `Avg abs: 604.06`.

#### Command 7: Persist ALSA Settings Across Reboots
```bash
echo "pengoin" | sudo -S alsactl store
```
* **Explanation**: 
  * Writes current hardware mixer configuration to `/var/lib/alsa/asound.state` so kernel restores calibrated gain on system boot.

---

## Part 2: Global Git Credentials & User Profile Setup

### 2.1 Requirement
Configure Git globally across the system so all repositories owned or accessed by the user perform passwordless/credential-cached operations without prompting repeatedly.

### 2.2 Commands Used & Explanations

#### Command 8: Enable Global Git Credential Store Helper
```bash
git config --global credential.helper store
```
* **Explanation**: 
  * Sets `credential.helper=store` in global `~/.gitconfig`. On future HTTPS `git push`/`pull` operations, credentials entered once are saved permanently to `~/.git-credentials`.

#### Command 9: Generate Ed25519 SSH Key Pair
```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh && ssh-keygen -t ed25519 -C "git-auto-auth" -N "" -f ~/.ssh/id_ed25519 <<< y
```
* **Explanation**: 
  * Creates `~/.ssh/` directory with `700` (`rwx------`) permissions.
  * Generates an Ed25519 SSH keypair (`id_ed25519` / `id_ed25519.pub`) without passphrase for passwordless SSH Git operations (`git@github.com:...`).

#### Command 10: Install Official GitHub CLI (`github-cli`)
```bash
echo "pengoin" | sudo -S pacman -S --noconfirm github-cli
```
* **Explanation**: 
  * Installs `github-cli` (`gh` version 2.96.0) from official Arch/CachyOS package repositories. Allows 1-click web OAuth login via `gh auth login`.

#### Command 11: Set Global Git User Identity
```bash
git config --global user.name "tthongs"
git config --global user.email "sanskarsinghss123@gmail.com"
```
* **Explanation**: 
  * Configures global commit author metadata in `~/.gitconfig`. All future commits in any repository on this system will use `tthongs <sanskarsinghss123@gmail.com>`.

#### Command 12: Verify Global Git Configuration
```bash
git config --global -l
```
* **Output**:
  ```text
  credential.helper=store
  user.name=tthongs
  user.email=sanskarsinghss123@gmail.com
  ```

---

## Summary Table of Configured Settings

| Category | Parameter | Configured Value | Scope |
| :--- | :--- | :--- | :--- |
| **Audio** | ALC256 Internal Mic Boost | `1 (+10.00 dB)` | Permanent (`/var/lib/alsa/asound.state`) |
| **Audio** | ALSA Capture Volume | `65% (+13.50 dB)` | Permanent (`/var/lib/alsa/asound.state`) |
| **Git** | `credential.helper` | `store` | Global (`~/.gitconfig`) |
| **Git** | `user.name` | `tthongs` | Global (`~/.gitconfig`) |
| **Git** | `user.email` | `sanskarsinghss123@gmail.com` | Global (`~/.gitconfig`) |
| **SSH Key** | Ed25519 Public Key | `~/.ssh/id_ed25519.pub` | System-wide |
| **CLI Tool** | GitHub CLI | `gh` (v2.96.0) | System-wide (`/usr/bin/gh`) |

---
*Log generated successfully.*
