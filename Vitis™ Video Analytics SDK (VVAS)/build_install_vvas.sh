#!/bin/bash
########################################################################
# Copyright (C) 2020 - 2022 Xilinx, Inc.
# Copyright (C) 2022 - 2026 Advanced Micro Devices, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
########################################################################

# Build and install VVAS for embedded platforms.
#
# Prerequisites:
#   source <sdk-path>/environment-setup-cortexa72-cortexa53-amd-linux
#
# Usage:
#   ./build_install_vvas.sh
#
# Output:
#   install/vvas_installer.tar.gz — deploy to board with:
#     scp install/vvas_installer.tar.gz <board-ip>:/
#     ssh <board-ip> 'cd / && tar -xzf vvas_installer.tar.gz'

set -e

BASEDIR=$PWD
PREFIX="/usr"

# --- Validate cross-compilation environment ---
if [ -z "$CC" ]; then
    echo "ERROR: Cross-compilation environment not set."
    echo "Run: source <sdk-path>/environment-setup-cortexa72-cortexa53-amd-linux"
    exit 1
fi

pkg-config --exists vvas-core || {
    echo "ERROR: vvas-core not found in sysroot. Ensure SDK is sourced."
    exit 1
}

# --- Derive SDK target prefix ---
SDK_TARGET_PREFIX=${TARGET_PREFIX%-}
echo ""
echo "VVAS Build Configuration:"
echo "  SDK target: $SDK_TARGET_PREFIX"
echo ""

# --- Meson version check (setup subcommand required since 0.64.0) ---
MESON_VER=$(meson --version | tail -n 1)
if printf '%s\n' "0.64.0" "$MESON_VER" | sort -V -C; then
    MESON="meson setup"
else
    MESON="meson"
fi

# --- Workaround: meson.native may be missing from SDK ---
if [ ! -f "$OECORE_NATIVE_SYSROOT/usr/share/meson/meson.native" ]; then
    touch "$OECORE_NATIVE_SYSROOT/usr/share/meson/meson.native"
fi

# --- Copy pre-commit hook if this is a git repo ---
if [[ -d ".git" && -d ".git/hooks" ]]; then
    cp -f ./hooks/pre-commit.hook .git/hooks/pre-commit
fi

# --- Helper: configure, build, and install a meson component ---
build_component() {
    local name=$1
    local srcdir=$2
    shift 2
    local extra_args="$*"

    echo "========================================="
    echo " Building: $name"
    echo "========================================="

    cd "$srcdir"
    sed -E 's@<SYSROOT>@'"$SDKTARGETSYSROOT"'@g; s@<NATIVESYSROOT>@'"$OECORE_NATIVE_SYSROOT"'@g; s@<SDKTARGET>@'"$SDK_TARGET_PREFIX"'@g' \
        meson.cross.template > meson.cross

    $MESON build --prefix "$PREFIX" --cross-file "$PWD/meson.cross" $extra_args
    cd build
    ninja
    DESTDIR="$SDKTARGETSYSROOT" ninja install
    DESTDIR="$BASEDIR/install" ninja install
    cd "$BASEDIR"
    echo ""
}

# --- Clean previous build ---
rm -rf install

# --- Build components in dependency order ---
build_component "vvas-utils" \
    "$BASEDIR/vvas-utils"

build_component "vvas-gst-plugins" \
    "$BASEDIR/vvas-gst-plugins" \

build_component "vvas-accel-sw-libs" \
    "$BASEDIR/vvas-accel-sw-libs"

# --- Install example configs (data-only, no sysroot install needed) ---
echo "========================================="
echo " Installing: vvas-examples configs"
echo "========================================="
cd "$BASEDIR/vvas-examples"
# Local embedded builds always package the MIPI camera examples. Yocto recipes
# can continue to select the mipi-camera Meson option independently.
examples_meson_args=("-Dmipi-camera=true")
rm -rf build
$MESON build --prefix "$PREFIX" "${examples_meson_args[@]}"
cd build
ninja
DESTDIR="$BASEDIR/install" ninja install
cd "$BASEDIR"
echo ""

# --- Package installer tarball ---
echo "========================================="
echo " Packaging vvas_installer.tar.gz"
echo "========================================="
cd "$BASEDIR/install"
tar -czf vvas_installer.tar.gz usr etc
cd "$BASEDIR"

echo ""
echo "Build complete: install/vvas_installer.tar.gz"
