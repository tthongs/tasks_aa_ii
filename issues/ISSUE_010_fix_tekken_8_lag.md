# [BUG] Fix Tekken 8 Lag and Black Screen on Hybrid Graphics Laptop

**Status**: Resolved
**Priority**: High
**Affected Directory**: /T8

## Description
Tekken 8 experienced severe performance lag and slow-motion execution on the
user's hybrid graphics laptop running CachyOS. This occurred because Vulkan
applications (including DX12 via Proton VKD3D) default to the integrated Intel
UHD Graphics GPU instead of offloading to the dedicated NVIDIA GeForce RTX 3050
Mobile GPU, as the required Vulkan Optimus layer variables were not configured.

Furthermore, after modifying launch options to force NVIDIA offloading, the game
encountered a black screen hang after the intro. This was due to the existing
Proton compatibility prefix and shader cache having been initialized under the
Intel GPU driver context, causing driver/device mismatches on boot.

## Steps to Reproduce
1. Launch Tekken 8 from Steam on the hybrid graphics laptop.
2. The game executes on the Intel integrated GPU because Vulkan device selection
   fails to select the NVIDIA dGPU.
3. Observe severe framerate drops below 60 FPS, resulting in slow-motion play.
4. Set the correct NVIDIA environment variables in launch options.
5. Launch the game and observe it hang on a black screen right after the intro.

## Proposed Solution / Action Items
- [x] Terminate Steam completely to prevent configuration overwrites.
- [x] Configure Steam launch options for Tekken 8 (AppID 1778820) in
  `localconfig.vdf` to include:
  - `__VK_LAYER_NV_optimus=NVIDIA_only` to force the Vulkan API (and
    VKD3D-Proton) to run on the NVIDIA GPU.
  - `__NV_PRIME_RENDER_OFFLOAD=1` and `__GLX_VENDOR_LIBRARY_NAME=nvidia` to
    enable proper PRIME offloading.
  - `__GL_SHADER_DISK_CACHE=1`, `__GL_SHADER_DISK_CACHE_SKIP_CLEANUP=1`, and
    `__GL_SHADER_DISK_CACHE_SIZE=10737418240` (10 GB) to optimize shader caching
    and avoid stutters.
  - `gamemoderun` to engage Feral GameMode for CPU/GPU performance optimization.
  - `PROTON_LOG=1` to generate Proton runtime logs for troubleshooting.
- [x] Back up and delete the old Intel-initialized Wine prefixes in both
  `compatdata/1778820` and `compatdata_ssd/1778820` to force Proton to build
  a fresh prefix under the NVIDIA context.
- [x] Clean the shader cache directory for Tekken 8.
- [x] Verify changes.

## Notes
The final configuration injected into Steam launch options:
`__NV_PRIME_RENDER_OFFLOAD=1 __VK_LAYER_NV_optimus=NVIDIA_only
__GLX_VENDOR_LIBRARY_NAME=nvidia PROTON_LOG=1 PROTON_ENABLE_NVAPI=1
PROTON_HIDE_NVIDIA_GPU=0 __GL_SHADER_DISK_CACHE=1
__GL_SHADER_DISK_CACHE_SKIP_CLEANUP=1 __GL_SHADER_DISK_CACHE_SIZE=10737418240
gamemoderun %command% -dx12`
