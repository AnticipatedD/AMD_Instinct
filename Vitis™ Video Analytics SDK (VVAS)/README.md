# Vitis™ Video Analytics SDK (VVAS)

GStreamer-based video analytics framework for AMD embedded platforms. Provides
plugins for hardware-accelerated inference, preprocessing, postprocessing, and
overlay rendering.

## Copyright and license statement
Copyright (C) 2022 Xilinx, Inc.

Copyright (C) 2022 - 2026 Advanced Micro Devices, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0).

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## Repository Structure

```
vvas/
├── vvas-gst-plugins/       # GStreamer plugins (xinfer, abrscaler, overlay, etc.)
├── vvas-utils/              # Core utility libraries
├── vvas-accel-sw-libs/      # Software acceleration libraries
├── vvas-examples/           # Example scripts and inference configs
├── build_install_vvas.sh    # Build script
└── clean_vvas.sh            # Clean build artifacts
```

## Prerequisites

- AMD embedded platform with cross-compilation toolchain
- SDK must include: vvas-core, GStreamer 1.18+, XRT, VART, ONNX Runtime

## Clone

```bash
git clone https://github.com/amd/VVAS.git
cd vvas
```

## Build

**Step 1:** Source the cross-compilation toolchain environment:
```bash
source <sdk-path>/environment-setup-cortexa72-cortexa53-amd-linux
```

**Step 2:** Build VVAS:
```bash
./build_install_vvas.sh
```

The local embedded build always includes the VEK385 four-camera scripts and
inference configurations in `install/vvas_installer.tar.gz`. Yocto recipes
can select the `mipi-camera` Meson option independently.

**Step 3:** Deploy to board:
```bash
scp install/vvas_installer.tar.gz <board-ip>:/
ssh <board-ip> 'cd / && tar -xzf vvas_installer.tar.gz'
```

## Quick Start

After deploying the tarball to the board:

```bash
cd /etc/vvas/examples
./01_quickstart.sh <input.nv12> <width> <height>
```

See [vvas-examples/README.md](vvas-examples/README.md) for all example scripts
and configuration details.

## GStreamer Plugins

| Plugin | Description |
|--------|-------------|
| `vvas_xinfer` | ML inference (classification, detection) with ONNXRT and VART backends |
| `vvas_xabrscaler` | HW-accelerated multi-output scaler with mean/scale normalization |
| `vvas_xoverlay` | Draw bounding boxes, labels, and shapes on video |
| `vvas_xmetaconvert` | Convert inference metadata to overlay format |
| `vvas_xmetaaffixer` | Transfer metadata between streams of different resolutions |
| `vvas_xfilter` | Generic filter for custom processing kernels |
| `vvas_xmulticrop` | Crop multiple regions of interest |
| `vvas_xfunnel` | Round-robin stream multiplexer |
| `vvas_xdefunnel` | Stream demultiplexer |
| `vvas_xtilecompositor` | Compose four DMA-BUF tiles using slot and epoch coordination |

## Supported Inference Backends

| Backend | Description |
|---------|-------------|
| ONNXRT (VitisAI EP) | ONNX Runtime with VitisAI execution provider — HW accelerated |
| VART | Vitis AI Runtime — direct model execution with zero-copy DMA |

## Clean

```bash
./clean_vvas.sh
```

## Documentation

Refer to the VVAS documentation for detailed plugin properties, configuration
options, and advanced pipeline patterns.

## License

This project is licensed under the Apache License 2.0 — see [LICENSE](LICENSE)
for details. Some files derived from third-party projects may carry different
licenses — see [THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt) for attribution.
