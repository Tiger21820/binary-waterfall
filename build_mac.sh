#!/bin/bash
# Binary Waterfall - macOS Build Script
# Builds a standalone .app bundle for macOS using PyInstaller

set -e

MAIN_NAME="binary-waterfall"
PROCESS_NAME="Binary Waterfall Revived"
MODULE_NAME="binary_waterfall"
ORIG_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCEDIR="$ORIG_DIR/src/$MODULE_NAME"
DISTDIR="$ORIG_DIR/dist"
ICON_PNG="$SOURCEDIR/resources/icon.png"
ICON_ICNS="$SOURCEDIR/resources/icon.icns"

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    ARCH_TAG="arm64"
elif [ "$ARCH" = "x86_64" ]; then
    ARCH_TAG="x86_64"
else
    ARCH_TAG="$ARCH"
fi
OUTPUT_APP="${MAIN_NAME}-macos-${ARCH_TAG}.app"
echo "  -> Architecture: $ARCH (tag: $ARCH_TAG)"
echo "  -> Output: $OUTPUT_APP"

echo "=== Binary Waterfall macOS Build ==="

# ---- Cleanup ----
echo "Cleaning up previous builds..."
rm -rf "$DISTDIR" "$ORIG_DIR/build" "$ORIG_DIR/$MAIN_NAME.spec"

# ---- Generate .icns icon (if not present) ----
if [ ! -f "$ICON_ICNS" ]; then
    echo "Generating .icns icon from $ICON_PNG..."
    ICONSET_DIR="/tmp/AppIcon.iconset"
    mkdir -p "$ICONSET_DIR"

    # Generate all required sizes using sips (built-in on macOS)
    for size in 16 32 64 128 256 512 1024; do
        sips -z "$size" "$size" "$ICON_PNG" --out "$ICONSET_DIR/icon_${size}x${size}.png" 2>/dev/null || true
        if [ "$size" -le 512 ]; then
            half=$((size * 2))
            sips -z "$half" "$half" "$ICON_PNG" --out "$ICONSET_DIR/icon_${size}x${size}@2x.png" 2>/dev/null || true
        fi
    done

    # Convert to .icns
    iconutil -c icns "$ICONSET_DIR" -o "$ICON_ICNS"
    echo "  -> Generated $ICON_ICNS"
    rm -rf "$ICONSET_DIR"
else
    echo "  -> Using existing $ICON_ICNS"
fi

# ---- Build with PyInstaller ----
echo ""
echo "Building macOS app bundle with PyInstaller..."
cd "$ORIG_DIR"

# Ensure dependencies are installed
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Install project in editable mode for dependencies
pip install -e .

# Exclude: unused Qt modules, unused PIL plugins
# NOTE: imageio_ffmpeg module is kept (needed by moviepy), but its
# bundled 47MB ffmpeg binary is removed in post-process below.
EXCLUDES=(
    "PyQt5.QtQml" "PyQt5.QtQuick" "PyQt5.QtQuick3D"
    "PyQt5.QtDBus" "PyQt5.QtWebSockets" "PyQt5.QtWebEngineWidgets"
    "PyQt5.QtOpenGL" "PyQt5.QtOpenGLFunctions" "PyQt5.QtPrintSupport"
    "PyQt5.QtXml" "PyQt5.QtXmlPatterns" "PyQt5.QtTest"
    "PyQt5.QtHelp" "PyQt5.QtDesigner" "PyQt5.QtSql"
    "PyQt5.QtBluetooth" "PyQt5.QtNfc" "PyQt5.QtPositioning"
    "PyQt5.QtLocation" "PyQt5.QtSensors" "PyQt5.QtSerialPort"
    "PyQt5.QtContacts" "PyQt5.QtOrganizer" "PyQt5.QtFeedback"
    "PIL.SpiderImagePlugin" "PIL.FpxImagePlugin" "PIL.MicImagePlugin"
    "PIL.MpegImagePlugin" "PIL.DcxImagePlugin" "PIL.PcdImagePlugin"
    "PIL.PcxImagePlugin" "PIL.IptcImagePlugin" "PIL.XbmImagePlugin"
    "PIL.XpmImagePlugin" "PIL.WalImageFile" "PIL.BufrStubImagePlugin"
    "PIL.FitsStubImagePlugin" "PIL.GribStubImagePlugin" "PIL.Hdf5StubImagePlugin"
    "PIL.MpoImagePlugin" "PIL.FtexImagePlugin" "PIL.PalmImagePlugin"
    "PIL.PdfImagePlugin" "PIL.FliImagePlugin" "PIL.GimpPaletteFile"
    "PIL.GimpGradientFile" "PIL.GbrImagePlugin" "PIL.GifImagePlugin"
    "PIL.ImtImagePlugin" "PIL.IcoImagePlugin" "PIL.CurImagePlugin"
    "PIL.SgiImagePlugin" "PIL.SunImagePlugin" "PIL.PpmImagePlugin"
    "PIL.PsdImagePlugin" "PIL.TgaImagePlugin" "PIL.MspImagePlugin"
    "PIL.IcnsImagePlugin" "PIL.DdsImagePlugin" "PIL.BlpImagePlugin"
    "PIL.DibImagePlugin" "PIL.EpsImagePlugin" "PIL.ImImagePlugin"
    "PIL.McIdasImagePlugin" "PIL.PixarImagePlugin" "PIL.PointImagePlugin"
    "PIL.PngImagePlugin" "PIL.JpegImagePlugin"
)

EXCLUDE_ARGS=()
for mod in "${EXCLUDES[@]}"; do
    EXCLUDE_ARGS+=("--exclude-module" "$mod")
done

pyinstaller --clean --noconfirm --windowed \
    --add-data "src/$MODULE_NAME/*.py:./src/$MODULE_NAME" \
    --add-data "src/$MODULE_NAME/version.yml:./src/$MODULE_NAME" \
    --add-data "src/$MODULE_NAME/constants/*.py:./src/$MODULE_NAME/constants" \
    --add-data "src/$MODULE_NAME/helpers/*.py:./src/$MODULE_NAME/helpers" \
    --add-data "src/$MODULE_NAME/resources/*:./src/$MODULE_NAME/resources" \
    --collect-all "imageio" \
    --collect-all "moviepy" \
    --collect-all "PIL" \
    --collect-all "pydub" \
    --collect-all "yaml" \
    --collect-all "proglog" \
    --copy-metadata "imageio" \
    --copy-metadata "moviepy" \
    --copy-metadata "Pillow" \
    --copy-metadata "pydub" \
    --copy-metadata "PyYAML" \
    --copy-metadata "proglog" \
    --hidden-import "imageio" \
    --hidden-import "PIL._tkinter_finder" \
    "${EXCLUDE_ARGS[@]}" \
    --onedir \
    --icon="$ICON_ICNS" \
    --osx-bundle-identifier="com.nimaid.binary-waterfall" \
    --name "$MAIN_NAME" \
    "binary-waterfall.py"

# ---- Post-process ----
echo ""
echo "Renaming output..."
APP_BUNDLE="$DISTDIR/$MAIN_NAME.app"
if [ -d "$APP_BUNDLE" ]; then
    mv "$APP_BUNDLE" "$ORIG_DIR/$OUTPUT_APP"
    echo "  -> $ORIG_DIR/$OUTPUT_APP"
else
    echo "ERROR: Could not find built app bundle at $APP_BUNDLE"
    ls -la "$DISTDIR/" 2>/dev/null || echo "dist/ directory not found"
    exit 1
fi

# ---- Ad-hoc code sign (required for Finder launch on Apple Silicon) ----
echo ""
echo "Ad-hoc signing bundle for Finder compatibility..."
codesign --force --deep --sign - "$ORIG_DIR/$OUTPUT_APP" 2>/dev/null && \
    echo "  -> Signed ad-hoc: $OUTPUT_APP" || \
    echo "  -> Warning: code signing failed (non-fatal)"

# ---- Cleanup build artifacts ----
echo ""
echo "Cleaning up build artifacts..."
rm -rf "$DISTDIR" "$ORIG_DIR/build" "$ORIG_DIR/$MAIN_NAME.spec"

echo ""
echo "=== Build complete! ==="
echo "Output: $ORIG_DIR/$OUTPUT_APP"
