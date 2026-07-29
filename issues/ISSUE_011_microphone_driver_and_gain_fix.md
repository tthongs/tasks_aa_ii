# [BUG] Fix Microphone Static Noise & Audio Gain Overload

**Status**: Resolved
**Priority**: High
**Affected Directory**: System / Audio (ALC256 / Intel Raptor Lake cAVS)

## Description
The internal microphone on Acer Aspire A715-79G (Intel Raptor Lake Core 5 210H, Realtek ALC256) was recording pure full-scale digital static noise (amplitude +/- 32768, average absolute amplitude 23675). Voice audio was completely masked by high-gain static saturation.

## Root Cause
The `Internal Mic Boost` in ALSA was maxed out at +30.00 dB (Level 3 - 100%) concurrently with `Capture` volume maxed out at +30.00 dB (Level 63 - 100%). This resulted in an excessive total preamp gain of +60.00 dB, clipping the Realtek ALC256 analog-to-digital converter into full-scale digital static.

## Solution & Action Items
- [x] Analyzed hardware drivers for Intel Raptor Lake audio (`00:1f.3`), NVIDIA GPU audio (`01:00.1`), Wi-Fi (`iwlwifi`), Bluetooth (`btusb`), GPU (`nvidia 610.43.03` & `i915`), and Webcam (`uvcvideo`).
- [x] Verified required firmware packages (`sof-firmware`, `linux-firmware-intel`, `linux-firmware`) are present and loaded properly.
- [x] Calibrated ALSA `Internal Mic Boost` down to +10.00 dB (33%) and PipeWire/ALSA `Capture` gain to nominal range.
- [x] Verified wave recording sample levels (`arecord` min -2889, max +3782, avg abs 604) confirming clean audio capture without clipping or static.
- [x] Saved calibrated settings permanently across reboots via `alsactl store`.

## Verification
Ran python waveform analysis on 2-second WAV recordings. Average absolute signal amplitude dropped from 23,675 (distorted/clipped static) to ~604 (clean ambient audio).
