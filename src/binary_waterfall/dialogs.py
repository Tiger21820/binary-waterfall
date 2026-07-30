import os
import webbrowser
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGridLayout, QLabel, QPushButton, QDialog, QDialogButtonBox, QComboBox, QLineEdit, QCheckBox, QSpinBox,
    QDoubleSpinBox, QMessageBox
)
from PyQt5.QtGui import QPixmap, QIcon, QColor, QPalette, QFont

from . import constants


# ==============================================================================
# M3 Dialog Mixin
# ==============================================================================
# Provides consistent M3 styling for all dialog windows:
#   - Dark surface background
#   - M3 title styling
#   - Rounded corners via stylesheet
#   - Proper spacing and typography

_M3_DIALOG_STYLE = """
QDialog {
    background-color: {bg};
}
QLabel {
    color: {text};
    font-size: {body}px;
}
QPushButton {{
    background-color: {primary};
    color: {on_primary};
    border: none;
    border-radius: {radius}px;
    padding: 8px 24px;
    font-size: {label}px;
    font-weight: 500;
    min-height: 20px;
}}
QPushButton:hover {{
    background-color: {primary_hover};
}}
QPushButton:pressed {{
    background-color: {primary_pressed};
}}
QPushButton:disabled {{
    background-color: {disabled_bg};
    color: {disabled_text};
}}
QComboBox {{
    background-color: {surface};
    color: {text};
    border: 1px solid {outline};
    border-radius: {radius_small}px;
    padding: 4px 8px;
    font-size: {body}px;
    min-height: 20px;
}}
QComboBox:hover {{
    border-color: {primary};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    image: none;
    border: none;
}}
QComboBox QAbstractItemView {{
    background-color: {surface_high};
    color: {text};
    selection-background-color: {primary_container};
    selection-color: {on_primary_container};
    border: none;
    border-radius: {radius_small}px;
    padding: 4px;
}}
QLineEdit {{
    background-color: {surface};
    color: {text};
    border: 1px solid {outline};
    border-radius: {radius_small}px;
    padding: 4px 8px;
    font-size: {body}px;
    min-height: 20px;
}}
QLineEdit:focus {{
    border-color: {primary};
}}
QSpinBox, QDoubleSpinBox {{
    background-color: {surface};
    color: {text};
    border: 1px solid {outline};
    border-radius: {radius_small}px;
    padding: 4px 8px;
    font-size: {body}px;
    min-height: 20px;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {primary};
}}
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    border: none;
    background: transparent;
    width: 20px;
    subcontrol-position: top right;
}}
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    border: none;
    background: transparent;
    width: 20px;
    subcontrol-position: bottom right;
}}
QCheckBox {{
    color: {text};
    font-size: {body}px;
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {outline};
    border-radius: 3px;
}}
QCheckBox::indicator:checked {{
    background-color: {primary};
    border-color: {primary};
}}
QGroupBox {{
    color: {text};
    font-size: {body}px;
    border: 1px solid {outline_variant};
    border-radius: {radius_small}px;
    margin-top: 12px;
    padding-top: 12px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}}
"""


def _m3_style_kwargs():
    """Build the format kwargs for the M3 dialog stylesheet."""
    c = constants.COLORS
    s = constants.SHAPES
    t = constants.TYPESET

    # Compute primary hover/press variants
    primary_hover = "#5ce8b9"  # lighter than #3ddbac
    primary_pressed = "#2db99a"

    return {
        "bg": c["surface"],
        "text": c["on_surface"],
        "primary": c["primary"],
        "on_primary": c["on_primary"],
        "primary_hover": primary_hover,
        "primary_pressed": primary_pressed,
        "surface": c["surface_variant"],
        "surface_high": c["surface_container_high"],
        "outline": c["outline"],
        "outline_variant": c["outline_variant"],
        "primary_container": c["primary_container"],
        "on_primary_container": c["on_primary_container"],
        "disabled_bg": c["surface_container_highest"],
        "disabled_text": c["outline_variant"],
        "radius": s["small"],
        "radius_small": s["extra_small"],
        "body": t["body_medium"],
        "label": t["label_large"],
    }


def apply_m3_dialog_style(dialog):
    """Apply M3 stylesheet to a dialog."""
    style = _M3_DIALOG_STYLE.format(**_m3_style_kwargs())
    dialog.setStyleSheet(style)


def create_m3_title(parent, text, font_size=None):
    """Create an M3 title label."""
    label = QLabel(text, parent)
    if font_size:
        fs = font_size
    else:
        fs = constants.TYPESET["title_medium"]
    font = QFont()
    font.setPointSize(fs)
    font.setWeight(QFont.Medium)
    label.setFont(font)
    return label


def create_m3_label(parent, text):
    """Create an M3 body label."""
    label = QLabel(text, parent)
    font = QFont()
    font.setPointSize(constants.TYPESET["body_medium"])
    label.setFont(font)
    return label


# ==============================================================================
# Audio settings input window
# ==============================================================================
class AudioSettings(QDialog):
    def __init__(self,
                 num_channels,
                 sample_bytes,
                 sample_rate,
                 volume,
                 parent=None
                 ):
        super().__init__(parent=parent)
        self.setWindowTitle("Audio Settings")
        self.setWindowIcon(QIcon(constants.ICON_PATHS["program"]))
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)

        self.num_channels = num_channels
        self.sample_bytes = sample_bytes
        self.sample_rate = sample_rate
        self.volume = volume

        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        row = 0

        # Title
        title = create_m3_title(self, "Audio Settings")
        layout.addWidget(title, row, 0, 1, 2)
        row += 1

        # Channels
        layout.addWidget(create_m3_label(self, "Channels:"), row, 0)
        self.channels_entry = QComboBox()
        self.channels_entry.addItems(["1 (mono)", "2 (stereo)"])
        if self.num_channels == 1:
            self.channels_entry.setCurrentIndex(0)
        elif self.num_channels == 2:
            self.channels_entry.setCurrentIndex(1)
        self.channels_entry.currentIndexChanged.connect(self.channel_entry_changed)
        layout.addWidget(self.channels_entry, row, 1)
        row += 1

        # Sample Size
        layout.addWidget(create_m3_label(self, "Sample Size:"), row, 0)
        self.sample_size_entry = QComboBox()
        self.sample_size_entry.addItems(["8-bit", "16-bit", "24-bit", "32-bit"])
        if self.sample_bytes == 1:
            self.sample_size_entry.setCurrentIndex(0)
        elif self.sample_bytes == 2:
            self.sample_size_entry.setCurrentIndex(1)
        elif self.sample_bytes == 3:
            self.sample_size_entry.setCurrentIndex(2)
        elif self.sample_bytes == 4:
            self.sample_size_entry.setCurrentIndex(3)
        self.sample_size_entry.currentIndexChanged.connect(self.sample_size_entry_changed)
        layout.addWidget(self.sample_size_entry, row, 1)
        row += 1

        # Sample Rate
        layout.addWidget(create_m3_label(self, "Sample Rate:"), row, 0)
        self.sample_rate_entry = QSpinBox()
        self.sample_rate_entry.setMinimum(1)
        self.sample_rate_entry.setMaximum(192000)
        self.sample_rate_entry.setSingleStep(1000)
        self.sample_rate_entry.setSuffix("Hz")
        self.sample_rate_entry.setValue(self.sample_rate)
        self.sample_rate_entry.valueChanged.connect(self.sample_rate_entry_changed)
        layout.addWidget(self.sample_rate_entry, row, 1)
        row += 1

        # Volume
        layout.addWidget(create_m3_label(self, "File Volume:"), row, 0)
        self.volume_entry = QSpinBox()
        self.volume_entry.setMinimum(0)
        self.volume_entry.setMaximum(100)
        self.volume_entry.setSingleStep(5)
        self.volume_entry.setSuffix("%")
        self.volume_entry.setValue(self.volume)
        self.volume_entry.valueChanged.connect(self.volume_entry_changed)
        layout.addWidget(self.volume_entry, row, 1)
        row += 1

        # Buttons
        btn_layout = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_layout.accepted.connect(self.accept)
        btn_layout.rejected.connect(self.reject)
        layout.addWidget(btn_layout, row, 0, 1, 2)
        row += 1

        self.setLayout(layout)
        apply_m3_dialog_style(self)

    def get_audio_settings(self):
        return {
            "num_channels": self.num_channels,
            "sample_bytes": self.sample_bytes,
            "sample_rate": self.sample_rate,
            "volume": self.volume,
        }

    def channel_entry_changed(self, idx):
        self.num_channels = 1 if idx == 0 else 2

    def sample_size_entry_changed(self, idx):
        self.sample_bytes = [1, 2, 3, 4][idx]

    def sample_rate_entry_changed(self, value):
        self.sample_rate = value

    def volume_entry_changed(self, value):
        self.volume = value


# ==============================================================================
# Video settings input window
# ==============================================================================
class VideoSettings(QDialog):
    def __init__(self,
                 bw,
                 width,
                 height,
                 color_format,
                 flip_v,
                 flip_h,
                 alignment,
                 playhead_visible,
                 parent=None
                 ):
        super().__init__(parent=parent)
        self.setWindowTitle("Video Settings")
        self.setWindowIcon(QIcon(constants.ICON_PATHS["program"]))
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)

        self.bw = bw
        self.width = width
        self.height = height
        self.color_format = color_format
        self.flip_v = flip_v
        self.flip_h = flip_h
        self.alignment = alignment
        self.playhead_visible = playhead_visible

        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        row = 0

        title = create_m3_title(self, "Video Settings")
        layout.addWidget(title, row, 0, 1, 2)
        row += 1

        # Width
        layout.addWidget(create_m3_label(self, "Width:"), row, 0)
        self.width_entry = QSpinBox()
        self.width_entry.setMinimum(4)
        self.width_entry.setMaximum(1024)
        self.width_entry.setSingleStep(4)
        self.width_entry.setSuffix("px")
        self.width_entry.setValue(self.width)
        self.width_entry.valueChanged.connect(self.width_entry_changed)
        layout.addWidget(self.width_entry, row, 1)
        row += 1

        # Height
        layout.addWidget(create_m3_label(self, "Height:"), row, 0)
        self.height_entry = QSpinBox()
        self.height_entry.setMinimum(4)
        self.height_entry.setMaximum(1024)
        self.height_entry.setSingleStep(4)
        self.height_entry.setSuffix("px")
        self.height_entry.setValue(self.height)
        self.height_entry.valueChanged.connect(self.height_entry_changed)
        layout.addWidget(self.height_entry, row, 1)
        row += 1

        # Color Format
        layout.addWidget(create_m3_label(self, "Color Format:"), row, 0)
        self.color_format_entry = QLineEdit()
        self.color_format_entry.setMaxLength(64)
        self.color_format_entry.setText(self.color_format)
        self.color_format_entry.editingFinished.connect(self.color_format_entry_changed)
        layout.addWidget(self.color_format_entry, row, 1)
        row += 1

        # Audio Alignment
        layout.addWidget(create_m3_label(self, "Audio Alignment:"), row, 0)
        self.alignment_entry = QComboBox()
        self.alignment_entry.addItems(["Frame Start", "Frame Center", "Frame End"])
        if self.alignment == constants.AlignmentCode.START:
            self.alignment_entry.setCurrentIndex(0)
        elif self.alignment == constants.AlignmentCode.MIDDLE:
            self.alignment_entry.setCurrentIndex(1)
        elif self.alignment == constants.AlignmentCode.END:
            self.alignment_entry.setCurrentIndex(2)
        self.alignment_entry.currentIndexChanged.connect(self.alignment_entry_changed)
        layout.addWidget(self.alignment_entry, row, 1)
        row += 1

        # Playhead
        layout.addWidget(create_m3_label(self, "Playhead:"), row, 0)
        self.playhead_entry = QCheckBox("Visible")
        self.playhead_entry.setChecked(self.playhead_visible)
        self.playhead_entry.stateChanged.connect(self.playhead_entry_changed)
        layout.addWidget(self.playhead_entry, row, 1)
        row += 1

        # Flip Vertical
        layout.addWidget(create_m3_label(self, "Vertical:"), row, 0)
        self.flip_v_entry = QCheckBox("Flip")
        self.flip_v_entry.setChecked(self.flip_v)
        self.flip_v_entry.stateChanged.connect(self.flip_v_entry_changed)
        layout.addWidget(self.flip_v_entry, row, 1)
        row += 1

        # Flip Horizontal
        layout.addWidget(create_m3_label(self, "Horizontal:"), row, 0)
        self.flip_h_entry = QCheckBox("Flip")
        self.flip_h_entry.setChecked(self.flip_h)
        self.flip_h_entry.stateChanged.connect(self.flip_h_entry_changed)
        layout.addWidget(self.flip_h_entry, row, 1)
        row += 1

        # Buttons
        btn_layout = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_layout.accepted.connect(self.accept)
        btn_layout.rejected.connect(self.reject)
        layout.addWidget(btn_layout, row, 0, 1, 2)

        self.setLayout(layout)
        apply_m3_dialog_style(self)

    def get_video_settings(self):
        return {
            "width": self.width,
            "height": self.height,
            "color_format": self.color_format,
            "flip_v": self.flip_v,
            "flip_h": self.flip_h,
            "alignment": self.alignment,
            "playhead_visible": self.playhead_visible,
        }

    def width_entry_changed(self, value):
        self.width = value

    def height_entry_changed(self, value):
        self.height = value

    def color_format_entry_changed(self):
        color_format = self.color_format_entry.text()
        parsed = self.bw.parse_color_format(color_format)
        if parsed["is_valid"]:
            self.color_format = color_format
        else:
            self.color_format_entry.setText(self.color_format)
            self.color_format_entry.setFocus()
            error_popup = QMessageBox(parent=self)
            error_popup.setIcon(QMessageBox.Critical)
            error_popup.setText("Invalid Color Format")
            error_popup.setInformativeText(parsed["message"])
            error_popup.setWindowTitle("Error")
            error_popup.exec()

    def playhead_entry_changed(self, value):
        self.playhead_visible = value != 0

    def flip_v_entry_changed(self, value):
        self.flip_v = value != 0

    def flip_h_entry_changed(self, value):
        self.flip_h = value != 0

    def alignment_entry_changed(self, idx):
        self.alignment = [constants.AlignmentCode.START,
                          constants.AlignmentCode.MIDDLE,
                          constants.AlignmentCode.END][idx]


# ==============================================================================
# Player settings input window
# ==============================================================================
class PlayerSettings(QDialog):
    def __init__(self,
                 max_view_dim,
                 fps,
                 parent=None
                 ):
        super().__init__(parent=parent)
        self.setWindowTitle("Player Settings")
        self.setWindowIcon(QIcon(constants.ICON_PATHS["program"]))
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)

        self.max_view_dim = max_view_dim
        self.fps = fps

        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        row = 0

        title = create_m3_title(self, "Player Settings")
        layout.addWidget(title, row, 0, 1, 2)
        row += 1

        # Max Dimension
        layout.addWidget(create_m3_label(self, "Max. Dimension:"), row, 0)
        self.max_dim_entry = QSpinBox()
        self.max_dim_entry.setMinimum(256)
        self.max_dim_entry.setMaximum(7680)
        self.max_dim_entry.setSingleStep(64)
        self.max_dim_entry.setSuffix("px")
        self.max_dim_entry.setValue(self.max_view_dim)
        self.max_dim_entry.valueChanged.connect(self.max_dim_entry_changed)
        layout.addWidget(self.max_dim_entry, row, 1)
        row += 1

        # Framerate
        layout.addWidget(create_m3_label(self, "Framerate:"), row, 0)
        self.fps_entry = QSpinBox()
        self.fps_entry.setMinimum(1)
        self.fps_entry.setMaximum(120)
        self.fps_entry.setSingleStep(1)
        self.fps_entry.setSuffix("fps")
        self.fps_entry.setValue(self.fps)
        self.fps_entry.valueChanged.connect(self.fps_entry_changed)
        layout.addWidget(self.fps_entry, row, 1)
        row += 1

        # Buttons
        btn_layout = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_layout.accepted.connect(self.accept)
        btn_layout.rejected.connect(self.reject)
        layout.addWidget(btn_layout, row, 0, 1, 2)

        self.setLayout(layout)
        apply_m3_dialog_style(self)

    def get_player_settings(self):
        return {
            "max_view_dim": self.max_view_dim,
            "fps": self.fps,
        }

    def max_dim_entry_changed(self, value):
        self.max_view_dim = value

    def fps_entry_changed(self, value):
        self.fps = value


# ==============================================================================
# Export image dialog
# ==============================================================================
class ExportFrame(QDialog):
    def __init__(self,
                 width,
                 height,
                 parent=None
                 ):
        super().__init__(parent=parent)
        self.setWindowTitle("Export Image Settings")
        self.setWindowIcon(QIcon(constants.ICON_PATHS["program"]))
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)

        self.width = width
        self.height = height
        self.keep_aspect = False

        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        row = 0

        title = create_m3_title(self, "Export Image")
        layout.addWidget(title, row, 0, 1, 2)
        row += 1

        layout.addWidget(create_m3_label(self, "Export Width:"), row, 0)
        self.width_entry = QSpinBox()
        self.width_entry.setMinimum(64)
        self.width_entry.setMaximum(7680)
        self.width_entry.setSingleStep(64)
        self.width_entry.setSuffix("px")
        self.width_entry.setValue(self.width)
        self.width_entry.valueChanged.connect(self.width_entry_changed)
        layout.addWidget(self.width_entry, row, 1)
        row += 1

        layout.addWidget(create_m3_label(self, "Export Height:"), row, 0)
        self.height_entry = QSpinBox()
        self.height_entry.setMinimum(64)
        self.height_entry.setMaximum(7680)
        self.height_entry.setSingleStep(64)
        self.height_entry.setSuffix("px")
        self.height_entry.setValue(self.height)
        self.height_entry.valueChanged.connect(self.height_entry_changed)
        layout.addWidget(self.height_entry, row, 1)
        row += 1

        layout.addWidget(create_m3_label(self, "Aspect Ratio:"), row, 0)
        self.aspect_entry = QCheckBox("Force")
        self.aspect_entry.setChecked(self.keep_aspect)
        self.aspect_entry.stateChanged.connect(self.aspect_entry_changed)
        layout.addWidget(self.aspect_entry, row, 1)
        row += 1

        btn_layout = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_layout.accepted.connect(self.accept)
        btn_layout.rejected.connect(self.reject)
        layout.addWidget(btn_layout, row, 0, 1, 2)

        self.setLayout(layout)
        apply_m3_dialog_style(self)

    def get_settings(self):
        return {
            "width": self.width,
            "height": self.height,
            "keep_aspect": self.keep_aspect,
        }

    def width_entry_changed(self, value):
        self.width = value

    def height_entry_changed(self, value):
        self.height = value

    def aspect_entry_changed(self, value):
        self.keep_aspect = value != 0


# ==============================================================================
# Export image sequence dialog
# ==============================================================================
class ExportSequence(QDialog):
    def __init__(self,
                 width,
                 height,
                 parent=None
                 ):
        super().__init__(parent=parent)
        self.setWindowTitle("Export Sequence Settings")
        self.setWindowIcon(QIcon(constants.ICON_PATHS["program"]))
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)

        self.width = width
        self.height = height
        self.fps = 60.0
        self.keep_aspect = False
        self.format = constants.ImageFormatCode.PNG

        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        row = 0

        title = create_m3_title(self, "Export Image Sequence")
        layout.addWidget(title, row, 0, 1, 2)
        row += 1

        layout.addWidget(create_m3_label(self, "FPS:"), row, 0)
        self.fps_entry = QDoubleSpinBox()
        self.fps_entry.setMinimum(1.0)
        self.fps_entry.setMaximum(120.0)
        self.fps_entry.setSingleStep(1.0)
        self.fps_entry.setSuffix("fps")
        self.fps_entry.setValue(self.fps)
        self.fps_entry.valueChanged.connect(self.fps_entry_changed)
        layout.addWidget(self.fps_entry, row, 1)
        row += 1

        layout.addWidget(create_m3_label(self, "Export Width:"), row, 0)
        self.width_entry = QSpinBox()
        self.width_entry.setMinimum(64)
        self.width_entry.setMaximum(7680)
        self.width_entry.setSingleStep(64)
        self.width_entry.setSuffix("px")
        self.width_entry.setValue(self.width)
        self.width_entry.valueChanged.connect(self.width_entry_changed)
        layout.addWidget(self.width_entry, row, 1)
        row += 1

        layout.addWidget(create_m3_label(self, "Export Height:"), row, 0)
        self.height_entry = QSpinBox()
        self.height_entry.setMinimum(64)
        self.height_entry.setMaximum(7680)
        self.height_entry.setSingleStep(64)
        self.height_entry.setSuffix("px")
        self.height_entry.setValue(self.height)
        self.height_entry.valueChanged.connect(self.height_entry_changed)
        layout.addWidget(self.height_entry, row, 1)
        row += 1

        layout.addWidget(create_m3_label(self, "Aspect Ratio:"), row, 0)
        self.aspect_entry = QCheckBox("Force")
        self.aspect_entry.setChecked(self.keep_aspect)
        self.aspect_entry.stateChanged.connect(self.aspect_entry_changed)
        layout.addWidget(self.aspect_entry, row, 1)
        row += 1

        layout.addWidget(create_m3_label(self, "Image Format:"), row, 0)
        self.format_entry = QComboBox()
        self.format_entry.addItems(["PNG (.png)", "JPEG (.jpg)", "BMP (.bmp)"])
        if self.format == constants.ImageFormatCode.PNG:
            self.format_entry.setCurrentIndex(0)
        elif self.format == constants.ImageFormatCode.JPEG:
            self.format_entry.setCurrentIndex(1)
        elif self.format == constants.ImageFormatCode.BITMAP:
            self.format_entry.setCurrentIndex(2)
        self.format_entry.currentIndexChanged.connect(self.format_entry_changed)
        layout.addWidget(self.format_entry, row, 1)
        row += 1

        btn_layout = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_layout.accepted.connect(self.accept)
        btn_layout.rejected.connect(self.reject)
        layout.addWidget(btn_layout, row, 0, 1, 2)

        self.setLayout(layout)
        apply_m3_dialog_style(self)

    def get_settings(self):
        return {
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "keep_aspect": self.keep_aspect,
            "format": self.format,
        }

    def width_entry_changed(self, value):
        self.width = value

    def height_entry_changed(self, value):
        self.height = value

    def aspect_entry_changed(self, value):
        self.keep_aspect = value != 0

    def fps_entry_changed(self, value):
        self.fps = value

    def format_entry_changed(self, value):
        self.format = [constants.ImageFormatCode.PNG,
                       constants.ImageFormatCode.JPEG,
                       constants.ImageFormatCode.BITMAP][value]


# ==============================================================================
# Export video dialog
# ==============================================================================
class ExportVideo(QDialog):
    def __init__(self,
                 width,
                 height,
                 parent=None
                 ):
        super().__init__(parent=parent)
        self.setWindowTitle("Export Video Settings")
        self.setWindowIcon(QIcon(constants.ICON_PATHS["program"]))
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)

        self.width = width
        self.height = height
        self.fps = 60.0
        self.keep_aspect = False

        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        row = 0

        title = create_m3_title(self, "Export Video")
        layout.addWidget(title, row, 0, 1, 2)
        row += 1

        layout.addWidget(create_m3_label(self, "FPS:"), row, 0)
        self.fps_entry = QDoubleSpinBox()
        self.fps_entry.setMinimum(1.0)
        self.fps_entry.setMaximum(120.0)
        self.fps_entry.setSingleStep(1.0)
        self.fps_entry.setSuffix("fps")
        self.fps_entry.setValue(self.fps)
        self.fps_entry.valueChanged.connect(self.fps_entry_changed)
        layout.addWidget(self.fps_entry, row, 1)
        row += 1

        layout.addWidget(create_m3_label(self, "Export Width:"), row, 0)
        self.width_entry = QSpinBox()
        self.width_entry.setMinimum(64)
        self.width_entry.setMaximum(7680)
        self.width_entry.setSingleStep(64)
        self.width_entry.setSuffix("px")
        self.width_entry.setValue(self.width)
        self.width_entry.valueChanged.connect(self.width_entry_changed)
        layout.addWidget(self.width_entry, row, 1)
        row += 1

        layout.addWidget(create_m3_label(self, "Export Height:"), row, 0)
        self.height_entry = QSpinBox()
        self.height_entry.setMinimum(64)
        self.height_entry.setMaximum(7680)
        self.height_entry.setSingleStep(64)
        self.height_entry.setSuffix("px")
        self.height_entry.setValue(self.height)
        self.height_entry.valueChanged.connect(self.height_entry_changed)
        layout.addWidget(self.height_entry, row, 1)
        row += 1

        layout.addWidget(create_m3_label(self, "Aspect Ratio:"), row, 0)
        self.aspect_entry = QCheckBox("Force")
        self.aspect_entry.setChecked(self.keep_aspect)
        self.aspect_entry.stateChanged.connect(self.aspect_entry_changed)
        layout.addWidget(self.aspect_entry, row, 1)
        row += 1

        btn_layout = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_layout.accepted.connect(self.accept)
        btn_layout.rejected.connect(self.reject)
        layout.addWidget(btn_layout, row, 0, 1, 2)

        self.setLayout(layout)
        apply_m3_dialog_style(self)

    def get_settings(self):
        return {
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "keep_aspect": self.keep_aspect,
        }

    def width_entry_changed(self, value):
        self.width = value

    def height_entry_changed(self, value):
        self.height = value

    def aspect_entry_changed(self, value):
        self.keep_aspect = value != 0

    def fps_entry_changed(self, value):
        self.fps = value


# ==============================================================================
# Export video encoder settings dialog
# ==============================================================================
class VideoEncoderSettings(QDialog):
    def __init__(self,
                 video_format,
                 parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Video Encoder Settings")
        self.setWindowIcon(QIcon(constants.ICON_PATHS["program"]))
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)

        self.video_format = video_format

        if self.video_format == constants.VideoFormatCode.MP4:
            self.codec = constants.VideoCodecCode.LIBX264
        elif self.video_format == constants.VideoFormatCode.AVI:
            self.codec = constants.VideoCodecCode.PNG
        self.audio_codec = constants.AudioCodecCode.MP3
        self.preset = constants.EncoderPresetCode.ULTRAFAST

        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        row = 0

        title = create_m3_title(self, "Video Encoder")
        layout.addWidget(title, row, 0, 1, 2)
        row += 1

        layout.addWidget(create_m3_label(self, "Video Codec:"), row, 0)
        self.codec_entry = QComboBox()
        if self.video_format == constants.VideoFormatCode.MP4:
            self.codec_entry.addItems(["LIBX264", "MPEG4"])
            if self.codec == constants.VideoCodecCode.LIBX264:
                self.codec_entry.setCurrentIndex(0)
            elif self.codec == constants.VideoCodecCode.MPEG4:
                self.codec_entry.setCurrentIndex(1)
        elif self.video_format == constants.VideoFormatCode.AVI:
            self.codec_entry.addItems(["PNG", "Raw"])
            if self.codec == constants.VideoCodecCode.PNG:
                self.codec_entry.setCurrentIndex(0)
            elif self.codec == constants.VideoCodecCode.RAW:
                self.codec_entry.setCurrentIndex(1)
        self.codec_entry.currentIndexChanged.connect(self.codec_entry_changed)
        layout.addWidget(self.codec_entry, row, 1)
        row += 1

        layout.addWidget(create_m3_label(self, "Audio Codec:"), row, 0)
        self.audio_codec_entry = QComboBox()
        self.audio_codec_entry.addItems(["MP3", "M4A", "WAV 16-bit", "WAV 32-bit"])
        if self.audio_codec == constants.AudioCodecCode.MP3:
            self.audio_codec_entry.setCurrentIndex(0)
        elif self.audio_codec == constants.AudioCodecCode.M4A:
            self.audio_codec_entry.setCurrentIndex(1)
        elif self.audio_codec == constants.AudioCodecCode.WAV16:
            self.audio_codec_entry.setCurrentIndex(2)
        elif self.audio_codec == constants.AudioCodecCode.WAV32:
            self.audio_codec_entry.setCurrentIndex(3)
        self.audio_codec_entry.currentIndexChanged.connect(self.audio_codec_entry_changed)
        layout.addWidget(self.audio_codec_entry, row, 1)
        row += 1

        layout.addWidget(create_m3_label(self, "Encoder Preset:"), row, 0)
        self.preset_entry = QComboBox()
        self.preset_entry.addItems([
            "Ultra Fast", "Super Fast", "Very Fast", "Faster", "Fast",
            "Medium", "Slow", "Slower", "Very Slow", "Placebo"
        ])
        preset_map = {
            constants.EncoderPresetCode.ULTRAFAST: 0,
            constants.EncoderPresetCode.SUPERFAST: 1,
            constants.EncoderPresetCode.VERYFAST: 2,
            constants.EncoderPresetCode.FASTER: 3,
            constants.EncoderPresetCode.FAST: 4,
            constants.EncoderPresetCode.MEDIUM: 5,
            constants.EncoderPresetCode.SLOW: 6,
            constants.EncoderPresetCode.SLOWER: 7,
            constants.EncoderPresetCode.VERYSLOW: 8,
            constants.EncoderPresetCode.PLACEBO: 9,
        }
        self.preset_entry.setCurrentIndex(preset_map.get(self.preset, 0))
        self.preset_entry.currentIndexChanged.connect(self.preset_entry_changed)
        layout.addWidget(self.preset_entry, row, 1)
        row += 1

        btn_layout = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_layout.accepted.connect(self.accept)
        btn_layout.rejected.connect(self.reject)
        layout.addWidget(btn_layout, row, 0, 1, 2)

        self.setLayout(layout)
        apply_m3_dialog_style(self)

    def get_settings(self):
        return {
            "codec": self.codec,
            "audio_codec": self.audio_codec,
            "preset": self.preset,
        }

    def codec_entry_changed(self, value):
        if self.video_format == constants.VideoFormatCode.MP4:
            self.codec = [constants.VideoCodecCode.LIBX264,
                         constants.VideoCodecCode.MPEG4][value]
        elif self.video_format == constants.VideoFormatCode.AVI:
            self.codec = [constants.VideoCodecCode.PNG,
                         constants.VideoCodecCode.RAW][value]

    def audio_codec_entry_changed(self, value):
        self.audio_codec = [
            constants.AudioCodecCode.MP3,
            constants.AudioCodecCode.M4A,
            constants.AudioCodecCode.WAV16,
            constants.AudioCodecCode.WAV32,
        ][value]

    def preset_entry_changed(self, value):
        preset_list = [
            constants.EncoderPresetCode.ULTRAFAST,
            constants.EncoderPresetCode.SUPERFAST,
            constants.EncoderPresetCode.VERYFAST,
            constants.EncoderPresetCode.FASTER,
            constants.EncoderPresetCode.FAST,
            constants.EncoderPresetCode.MEDIUM,
            constants.EncoderPresetCode.SLOW,
            constants.EncoderPresetCode.SLOWER,
            constants.EncoderPresetCode.VERYSLOW,
            constants.EncoderPresetCode.PLACEBO,
        ]
        self.preset = preset_list[value]


# ==============================================================================
# Hotkey info dialog
# ==============================================================================
class HotkeysInfo(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Hotkey Info")
        self.setWindowIcon(QIcon(constants.ICON_PATHS["program"]))
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)

        layout = QGridLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(20, 16, 20, 16)

        row = 0

        title = create_m3_title(self, "Keyboard Shortcuts")
        layout.addWidget(title, row, 0, 1, 2)
        row += 1

        hotkeys = [
            ("Play / Pause", "Spacebar"),
            ("Back", "Left"),
            ("Forward", "Right"),
            ("Frame Back", "<"),
            ("Frame Forward", ">"),
            ("Restart", "R"),
            ("Volume Up", "Up"),
            ("Volume Down", "Down"),
            ("Mute", "M"),
        ]

        body_font = QFont()
        body_font.setPointSize(constants.TYPESET["body_medium"])

        label_font = QFont()
        label_font.setPointSize(constants.TYPESET["body_medium"])
        label_font.setWeight(QFont.Medium)

        for action, key in hotkeys:
            action_label = QLabel(action)
            action_label.setFont(body_font)
            action_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            layout.addWidget(action_label, row, 0)

            key_label = QLabel(key)
            key_label.setFont(label_font)
            key_label.setStyleSheet(f"""
                background-color: {constants.COLORS["surface_container_highest"]};
                color: {constants.COLORS["on_surface"]};
                border-radius: {constants.SHAPES["extra_small"]}px;
                padding: 2px 10px;
            """)
            key_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(key_label, row, 1)
            row += 1

        btn_layout = QDialogButtonBox(QDialogButtonBox.Ok)
        btn_layout.accepted.connect(self.accept)
        layout.addWidget(btn_layout, row, 0, 1, 2)

        self.setLayout(layout)
        apply_m3_dialog_style(self)


# ==============================================================================
# About dialog
# ==============================================================================
class About(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle(f"About {constants.TITLE}")
        self.setWindowIcon(QIcon(constants.ICON_PATHS["program"]))
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)

        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)

        row = 0

        # App icon
        icon_pixmap = QPixmap(constants.ICON_PATHS["program"])
        icon_label = QLabel()
        icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label, row, 0, 1, 2)
        row += 1

        # Title
        title = create_m3_title(self, constants.TITLE, font_size=constants.TYPESET["title_large"])
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, row, 0, 1, 2)
        row += 1

        # Version
        version_label = QLabel(f"Version {constants.VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        vfont = QFont()
        vfont.setPointSize(constants.TYPESET["body_medium"])
        version_label.setFont(vfont)
        version_label.setStyleSheet(f"color: {constants.COLORS['on_surface_variant']};")
        layout.addWidget(version_label, row, 0, 1, 2)
        row += 1

        # Description
        desc_label = QLabel(constants.DESCRIPTION)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        dfont = QFont()
        dfont.setPointSize(constants.TYPESET["body_small"])
        desc_label.setFont(dfont)
        desc_label.setStyleSheet(f"color: {constants.COLORS['on_surface_variant']};")
        layout.addWidget(desc_label, row, 0, 1, 2)
        row += 1

        # Copyright
        copyright_label = QLabel(constants.COPYRIGHT)
        copyright_label.setAlignment(Qt.AlignCenter)
        cfont = QFont()
        cfont.setPointSize(constants.TYPESET["body_small"])
        copyright_label.setFont(cfont)
        copyright_label.setStyleSheet(f"color: {constants.COLORS['on_surface_variant']};")
        layout.addWidget(copyright_label, row, 0, 1, 2)
        row += 1

        # Links
        link_label = QLabel(f'<a href="{constants.PROJECT_URL}" style="color: {constants.COLORS["primary"]};">{constants.PROJECT_URL}</a>')
        link_label.setTextFormat(Qt.RichText)
        link_label.setAlignment(Qt.AlignCenter)
        link_label.linkActivated.connect(lambda url: webbrowser.open(url))
        layout.addWidget(link_label, row, 0, 1, 2)
        row += 1

        btn_layout = QDialogButtonBox(QDialogButtonBox.Ok)
        btn_layout.accepted.connect(self.accept)
        layout.addWidget(btn_layout, row, 0, 1, 2)

        self.setLayout(layout)
        apply_m3_dialog_style(self)

        # Override QPushButton styling for About dialog to be more compact
        self.setStyleSheet(self.styleSheet() + """
            QPushButton {
                min-width: 80px;
            }
        """)