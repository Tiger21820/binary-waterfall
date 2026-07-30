import os
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QHBoxLayout, QLabel,
    QFileDialog, QAction, QMessageBox, QProgressDialog
)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor

from . import constants, generators, outputs, widgets, dialogs


# ==============================================================================
# Global M3 Application Stylesheet
# ==============================================================================
# Use __OB__ / __CB__ placeholders to avoid clash with .format() braces
# __OB__ = open brace {, __CB__ = close brace }
_M3_STYLE_TEMPLATE = """
/* === M3 Dark Theme === */
QMainWindow __OB__
    background-color: {bg};
__CB__
QMenuBar __OB__
    background-color: {bg};
    color: {on_surface};
    font-size: {label}px;
    padding: 4px 0;
    border-bottom: 1px solid {outline_variant};
__CB__
QMenuBar::item __OB__
    background: transparent;
    padding: 4px 12px;
    border-radius: {radius_small}px;
    margin: 2px 0;
__CB__
QMenuBar::item:selected __OB__
    background-color: {primary_container};
__CB__
QMenu __OB__
    background-color: {surface_high};
    color: {on_surface};
    border: none;
    border-radius: {radius_small}px;
    padding: 4px;
__CB__
QMenu::item __OB__
    padding: 6px 24px;
    border-radius: {radius_small}px;
    font-size: {body}px;
__CB__
QMenu::item:selected __OB__
    background-color: {primary_container};
    color: {on_primary_container};
__CB__
QMenu::separator __OB__
    height: 1px;
    background: {outline_variant};
    margin: 4px 12px;
__CB__
QWidget#controls_panel __OB__
    background-color: {surface};
    border-top: 1px solid {outline_variant};
__CB__
QWidget#viewer_panel __OB__
    background-color: {viewer};
__CB__
QToolTip __OB__
    background-color: {surface_high};
    color: {on_surface};
    border: none;
    border-radius: {radius_small}px;
    padding: 4px 8px;
    font-size: {body_small}px;
__CB__
QProgressDialog __OB__
    background-color: {bg};
    color: {on_surface};
__CB__
QProgressBar __OB__
    background-color: {surface_variant};
    border: none;
    border-radius: {radius_small}px;
    text-align: center;
    font-size: {body_small}px;
    height: 8px;
__CB__
QProgressBar::chunk __OB__
    background-color: {primary};
    border-radius: {radius_small}px;
__CB__
"""


def _m3_app_style():
    c = constants.COLORS
    s = constants.SHAPES
    t = constants.TYPESET
    formatted = _M3_STYLE_TEMPLATE.format(
        bg=c["background"],
        on_surface=c["on_surface"],
        on_surface_variant=c["on_surface_variant"],
        primary=c["primary"],
        on_primary_container=c["on_primary_container"],
        primary_container=c["primary_container"],
        surface=c["surface"],
        surface_variant=c["surface_variant"],
        surface_high=c["surface_container_high"],
        outline_variant=c["outline_variant"],
        viewer=c["viewer"],
        radius_small=s["extra_small"],
        body=t["body_medium"],
        body_small=t["body_small"],
        label=t["label_large"],
    )
    return formatted.replace("__OB__", "{").replace("__CB__", "}")


# ==============================================================================
# Main Window
# ==============================================================================
class MyQMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_savename = None
        self.muted = None

        self.setWindowTitle(f"{constants.TITLE}")
        self.setWindowIcon(QIcon(constants.ICON_PATHS["program"]))

        self.bw = generators.BinaryWaterfall()

        self.last_save_location = constants.USER_DIR
        self.last_load_location = constants.USER_DIR

        self.renderer = outputs.Renderer(
            binary_waterfall=self.bw
        )

        self.padding_px = 12

        # --- Seek Bar (M3) ---
        self.seek_bar = widgets.M3SeekBar()
        self.seek_bar.setFocusPolicy(Qt.NoFocus)
        self.seek_bar.setMinimum(0)
        self.seek_bar.setMaximum(100)
        self.update_seekbar()
        self.seek_bar.sliderMoved.connect(self.seekbar_moved)
        self.seek_bar.sliderPressed.connect(lambda: None)

        # --- Viewer ---
        self.player_label = QLabel()
        self.player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.player_label.setStyleSheet(f"background-color: {constants.COLORS['viewer']};")
        self.player_label.setObjectName("viewer_panel")

        # --- Player ---
        self.player = outputs.Player(
            binary_waterfall=self.bw,
            display=self.player_label,
            set_playbutton_function=self.set_play_button,
            set_seekbar_function=self.seek_bar.setValue
        )

        self.current_volume = self.player.volume

        # Setup seek bar to correctly change player location
        self.seek_bar.set_position_changed_function(self.seekbar_moved)

        self.set_file_savename()

        # --- Play/Pause Icon Button (M3) ---
        self.play_icons = {
            "play": {
                "base": QPixmap(constants.ICON_PATHS["button"]["play"]["base"]),
                "hover": QPixmap(constants.ICON_PATHS["button"]["play"]["hover"]),
                "clicked": QPixmap(constants.ICON_PATHS["button"]["play"]["clicked"])
            },
            "pause": {
                "base": QPixmap(constants.ICON_PATHS["button"]["pause"]["base"]),
                "hover": QPixmap(constants.ICON_PATHS["button"]["pause"]["hover"]),
                "clicked": QPixmap(constants.ICON_PATHS["button"]["pause"]["clicked"])
            }
        }

        self.transport_play = widgets.M3IconButton(
            pixmap=self.play_icons["play"]["base"],
            pixmap_hover=self.play_icons["play"]["hover"],
            pixmap_pressed=self.play_icons["play"]["clicked"],
            scale=1.0,
            parent=self,
            tooltip="Play / Pause (Space)"
        )
        self.transport_play.setFocusPolicy(Qt.NoFocus)
        self.transport_play.clicked.connect(self.play_clicked)

        self.transport_forward = widgets.M3IconButton(
            pixmap=QPixmap(constants.ICON_PATHS["button"]["forward"]["base"]),
            pixmap_hover=QPixmap(constants.ICON_PATHS["button"]["forward"]["hover"]),
            pixmap_pressed=QPixmap(constants.ICON_PATHS["button"]["forward"]["clicked"]),
            scale=0.75,
            parent=self,
            tooltip="Forward 5s (Right)"
        )
        self.transport_forward.setFocusPolicy(Qt.NoFocus)
        self.transport_forward.clicked.connect(self.forward_clicked)

        self.transport_back = widgets.M3IconButton(
            pixmap=QPixmap(constants.ICON_PATHS["button"]["back"]["base"]),
            pixmap_hover=QPixmap(constants.ICON_PATHS["button"]["back"]["hover"]),
            pixmap_pressed=QPixmap(constants.ICON_PATHS["button"]["back"]["clicked"]),
            scale=0.75,
            parent=self,
            tooltip="Back 5s (Left)"
        )
        self.transport_back.setFocusPolicy(Qt.NoFocus)
        self.transport_back.clicked.connect(self.back_clicked)

        self.transport_restart = widgets.M3IconButton(
            pixmap=QPixmap(constants.ICON_PATHS["button"]["restart"]["base"]),
            pixmap_hover=QPixmap(constants.ICON_PATHS["button"]["restart"]["hover"]),
            pixmap_pressed=QPixmap(constants.ICON_PATHS["button"]["restart"]["clicked"]),
            scale=0.5,
            parent=self,
            tooltip="Restart (R)"
        )
        self.transport_restart.setFocusPolicy(Qt.NoFocus)
        self.transport_restart.clicked.connect(self.restart_clicked)

        # --- Volume (M3) ---
        self.volume_icons = {
            "base": QPixmap(constants.ICON_PATHS["volume"]["base"]),
            "mute": QPixmap(constants.ICON_PATHS["volume"]["mute"]),
        }

        self.volume_icon = QLabel()
        self.volume_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.volume_icon.setScaledContents(True)
        self.volume_icon.setFixedSize(20, 20)
        self.set_volume_icon(mute=self.is_player_muted())
        self.unmute_volume = self.current_volume
        self.volume_icon.mousePressEvent = self.volume_icon_clicked

        self.volume_label = QLabel()
        self.volume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.volume_label.setFixedWidth(30)
        vfont = QFont()
        vfont.setPointSize(constants.TYPESET["label_small"])
        self.volume_label.setFont(vfont)
        self.set_volume_label_value(self.current_volume)

        self.volume_slider = widgets.M3VolumeSlider()
        self.volume_slider.setFocusPolicy(Qt.NoFocus)
        self.volume_slider.setFixedSize(40, 60)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.valueChanged.connect(self.volume_slider_changed)

        # --- Transport Layouts ---
        self.transport_left_layout = QHBoxLayout()
        self.transport_left_layout.setSpacing(4)
        self.transport_left_layout.addWidget(self.transport_restart)
        self.transport_left_layout.addWidget(self.transport_back)

        self.restart_counterpad = QLabel()

        self.transport_right_layout = QHBoxLayout()
        self.transport_right_layout.setSpacing(4)
        self.transport_right_layout.addWidget(self.transport_forward)
        self.transport_right_layout.addWidget(self.restart_counterpad)

        self.volume_layout = QGridLayout()
        self.volume_layout.setContentsMargins(0, 0, self.padding_px, 0)

        self.volume_layout.addWidget(self.volume_icon, 0, 0,
                                     alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        self.volume_layout.addWidget(self.volume_label, 1, 0,
                                     alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.volume_layout.addWidget(self.volume_slider, 0, 1, 2, 1,
                                     alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # --- Main Layout ---
        self.main_layout = QGridLayout()
        self.main_layout.setContentsMargins(self.padding_px, self.padding_px,
                                            self.padding_px, self.padding_px)
        self.main_layout.setSpacing(self.padding_px)

        self.main_layout.addWidget(self.player_label, 0, 0, 1, 5,
                                   alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.seek_bar, 1, 0, 1, 5,
                                   alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addLayout(self.transport_left_layout, 2, 1,
                                   alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        self.main_layout.addWidget(self.transport_play, 2, 2,
                                   alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addLayout(self.transport_right_layout, 2, 3,
                                   alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addLayout(self.volume_layout, 2, 4,
                                   alignment=Qt.AlignmentFlag.AlignCenter)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Apply M3 stylesheet
        self.setStyleSheet(_m3_app_style())

        # --- Menu Bar (M3) ---
        self.main_menu = self.menuBar()

        self.file_menu = self.main_menu.addMenu("File")
        self.file_menu_open = QAction("Open...", self)
        self.file_menu_open.triggered.connect(self.open_file_clicked)
        self.file_menu.addAction(self.file_menu_open)
        self.file_menu_close = QAction("Close", self)
        self.file_menu_close.setEnabled(False)
        self.file_menu_close.triggered.connect(self.close_file_clicked)
        self.file_menu.addAction(self.file_menu_close)

        self.main_menu.addSeparator()

        self.settings_menu = self.main_menu.addMenu("Settings")
        self.settings_menu_audio = QAction("Audio...", self)
        self.settings_menu_audio.triggered.connect(self.audio_settings_clicked)
        self.settings_menu.addAction(self.settings_menu_audio)
        self.settings_menu_video = QAction("Video...", self)
        self.settings_menu_video.triggered.connect(self.video_settings_clicked)
        self.settings_menu.addAction(self.settings_menu_video)
        self.settings_menu_player = QAction("Player...", self)
        self.settings_menu_player.triggered.connect(self.player_settings_clicked)
        self.settings_menu.addAction(self.settings_menu_player)

        self.main_menu.addSeparator()

        self.export_menu = self.main_menu.addMenu("Export")
        self.export_menu.setEnabled(False)
        self.export_menu_audio = QAction("Audio...", self)
        self.export_menu_audio.triggered.connect(self.export_audio_clicked)
        self.export_menu.addAction(self.export_menu_audio)
        self.export_menu_image = QAction("Image...", self)
        self.export_menu_image.triggered.connect(self.export_image_clicked)
        self.export_menu.addAction(self.export_menu_image)
        self.export_menu_sequence = QAction("Image Sequence...", self)
        self.export_menu_sequence.triggered.connect(self.export_sequence_clicked)
        self.export_menu.addAction(self.export_menu_sequence)
        self.export_menu_video = QAction("Video...", self)
        self.export_menu_video.triggered.connect(self.export_video_clicked)
        self.export_menu.addAction(self.export_menu_video)

        self.main_menu.addSeparator()

        self.help_menu = self.main_menu.addMenu("Help")
        self.help_menu_hotkeys = QAction("Hotkeys...", self)
        self.help_menu_hotkeys.triggered.connect(self.hotkeys_clicked)
        self.help_menu.addAction(self.help_menu_hotkeys)
        self.help_menu_about = QAction("About...", self)
        self.help_menu_about.triggered.connect(self.about_clicked)
        self.help_menu.addAction(self.help_menu_about)

        self.set_volume(self.current_volume)
        self.resize_window()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Space:
            self.play_clicked()
        elif key == Qt.Key_Left:
            self.back_clicked()
        elif key == Qt.Key_Right:
            self.forward_clicked()
        elif key == Qt.Key_Up:
            new_volume = min(self.current_volume + 5, 100)
            self.set_volume(new_volume)
        elif key == Qt.Key_Down:
            new_volume = max(self.current_volume - 5, 0)
            self.set_volume(new_volume)
        elif key == Qt.Key_M:
            self.toggle_mute()
        elif key == Qt.Key_R:
            self.restart_clicked()
        elif key == Qt.Key_Comma:
            self.player.frame_back()
        elif key == Qt.Key_Period:
            self.player.frame_forward()

    def resize_window(self):
        self.seek_bar.setFixedWidth(20)
        self.update_counterpad_size()
        QTimer.singleShot(10, self.resize_window_helper)

    def resize_window_helper(self):
        size_hint = self.sizeHint()
        self.setFixedSize(size_hint)
        self.seek_bar.setFixedWidth(size_hint.width() - (self.padding_px * 2))

    def update_counterpad_size(self):
        self.restart_counterpad.setFixedSize(self.transport_restart.sizeHint())

    def set_play_button(self, play):
        if play:
            self.transport_play.change_pixmaps(
                pixmap=self.play_icons["play"]["base"],
                pixmap_hover=self.play_icons["play"]["hover"],
                pixmap_pressed=self.play_icons["play"]["clicked"]
            )
        else:
            self.transport_play.change_pixmaps(
                pixmap=self.play_icons["pause"]["base"],
                pixmap_hover=self.play_icons["pause"]["hover"],
                pixmap_pressed=self.play_icons["pause"]["clicked"]
            )

    def is_player_muted(self):
        return self.player.volume == 0

    def set_volume_icon(self, mute):
        if mute:
            self.volume_icon.setPixmap(self.volume_icons["mute"])
        else:
            self.volume_icon.setPixmap(self.volume_icons["base"])

    def set_volume_label_value(self, value):
        self.volume_label.setText(f"{value}%")

    def set_volume(self, value):
        self.current_volume = value
        self.player.set_volume(self.current_volume)
        self.set_volume_label_value(self.current_volume)
        self.volume_slider.setValue(self.player.volume)
        if self.current_volume > 0:
            self.unmute_volume = self.current_volume
        self.set_volume_icon(mute=(self.current_volume == 0))

    def update_seekbar(self):
        if self.bw.filename is None:
            self.seek_bar.setEnabled(False)
            self.seek_bar.setValue(0)
        else:
            self.seek_bar.setMaximum(self.bw.audio_length_ms)
            self.seek_bar.setEnabled(True)

    def seekbar_moved(self, position):
        self.player.set_position(position)

    def pause_player(self):
        self.player.pause()

    def play_player(self):
        self.player.play()

    def play_clicked(self):
        if self.player.is_playing():
            self.pause_player()
        else:
            self.play_player()

    def forward_clicked(self):
        self.player.forward()

    def back_clicked(self):
        self.player.back()

    def restart_clicked(self):
        self.player.restart()

    def toggle_mute(self):
        if self.is_player_muted():
            self.muted = False
            self.volume_slider.setValue(self.unmute_volume)
        else:
            self.muted = True
            self.volume_slider.setValue(0)

    def volume_icon_clicked(self, event):
        self.toggle_mute()

    def volume_slider_changed(self, value):
        self.set_volume(value)

    def set_file_savename(self, name=None):
        if name is None:
            self.file_savename = "Untitled"
        else:
            self.file_savename = name

    def open_file_clicked(self):
        self.pause_player()
        filename, filetype = QFileDialog.getOpenFileName(
            self, "Open File", self.last_load_location, "All Binary Files (*)"
        )
        if filename != "":
            self.player.open_file(filename=filename)
            file_path, file_title = os.path.split(filename)
            file_savename, file_ext = os.path.splitext(file_title)
            self.set_file_savename(file_savename)
            self.setWindowTitle(f"{constants.TITLE} | {file_title}")
            self.last_load_location = filename
            self.update_seekbar()
            self.export_menu.setEnabled(True)
            self.file_menu_close.setEnabled(True)

    def close_file_clicked(self):
        self.pause_player()
        self.player.close_file()
        self.set_file_savename()
        self.setWindowTitle(f"{constants.TITLE}")
        self.update_seekbar()
        self.export_menu.setEnabled(False)
        self.file_menu_close.setEnabled(False)

    def audio_settings_clicked(self):
        popup = dialogs.AudioSettings(
            num_channels=self.bw.num_channels,
            sample_bytes=self.bw.sample_bytes,
            sample_rate=self.bw.sample_rate,
            volume=self.bw.volume,
            parent=self
        )
        result = popup.exec()
        if result:
            audio_settings = popup.get_audio_settings()
            self.player.set_audio_settings(
                num_channels=audio_settings["num_channels"],
                sample_bytes=audio_settings["sample_bytes"],
                sample_rate=audio_settings["sample_rate"],
                volume=audio_settings["volume"]
            )
            self.update_seekbar()

    def video_settings_clicked(self):
        popup = dialogs.VideoSettings(
            bw=self.bw,
            width=self.bw.width, height=self.bw.height,
            color_format=self.bw.get_color_format_string(),
            flip_v=self.bw.flip_v, flip_h=self.bw.flip_h,
            alignment=self.bw.alignment,
            playhead_visible=self.bw.playhead_visible,
            parent=self
        )
        result = popup.exec()
        if result:
            vs = popup.get_video_settings()
            self.bw.set_dims(width=vs["width"], height=vs["height"])
            self.bw.set_color_format(vs["color_format"])
            self.bw.set_flip(flip_v=vs["flip_v"], flip_h=vs["flip_h"])
            self.bw.set_alignment(alignment=vs["alignment"])
            self.bw.set_playhead_visible(playhead_visible=vs["playhead_visible"])
            self.player.refresh_dims()
            self.player.update_image()
            QTimer.singleShot(10, self.resize_window)

    def player_settings_clicked(self):
        popup = dialogs.PlayerSettings(
            max_view_dim=self.player.max_dim,
            fps=self.player.fps,
            parent=self
        )
        result = popup.exec()
        if result:
            ps = popup.get_player_settings()
            self.player.set_fps(fps=ps["fps"])
            self.player.update_dims(max_dim=ps["max_view_dim"])
            QTimer.singleShot(10, self.resize_window)

    def export_image_clicked(self):
        if self.bw.audio_filename is None:
            QMessageBox.critical(self, "Error",
                "There is no file open in the viewer to export.\n\nPlease open a file and try again.",
                QMessageBox.Cancel)
            return
        popup = dialogs.ExportFrame(width=self.player.width, height=self.player.height, parent=self)
        result = popup.exec()
        if result:
            settings = popup.get_settings()
            filename, filetype = QFileDialog.getSaveFileName(
                self, "Export Image As...",
                os.path.join(self.last_save_location, f"{self.file_savename}{constants.ImageFormatCode.PNG.value}"),
                f"PNG (*{constants.ImageFormatCode.PNG.value});;JPEG (*{constants.ImageFormatCode.JPEG.value});;BMP (*{constants.ImageFormatCode.BITMAP.value})"
            )
            if filename != "":
                self.last_save_location = os.path.split(filename)[0]
                try:
                    self.renderer.export_frame(ms=self.player.get_position(), filename=filename,
                                               size=(settings["width"], settings["height"]),
                                               keep_aspect=settings["keep_aspect"])
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"An error occurred: {str(e)}", QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "Export Complete", "Export image successful!", QMessageBox.Ok)

    def export_audio_clicked(self):
        if self.bw.audio_filename is None:
            QMessageBox.critical(self, "Error",
                "There is no file open in the viewer to export.\n\nPlease open a file and try again.",
                QMessageBox.Cancel)
            return
        filename, filetype = QFileDialog.getSaveFileName(
            self, "Export Audio As...",
            os.path.join(self.last_save_location, f"{self.file_savename}{constants.AudioFormatCode.MP3.value}"),
            f"MP3 (*{constants.AudioFormatCode.MP3.value});;WAV (*{constants.AudioFormatCode.WAVE.value});;FLAC (*{constants.AudioFormatCode.FLAC.value})"
        )
        if filename != "":
            self.last_save_location = os.path.split(filename)[0]
            try:
                self.renderer.export_audio(filename=filename)
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"An error occurred: {str(e)}", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "Export Complete", "Export audio successful!", QMessageBox.Ok)

    def export_sequence_clicked(self):
        if self.bw.audio_filename is None:
            QMessageBox.critical(self, "Error",
                "There is no file open in the viewer to export.\n\nPlease open a file and try again.",
                QMessageBox.Cancel)
            return
        popup = dialogs.ExportSequence(width=self.player.width, height=self.player.height, parent=self)
        result = popup.exec()
        if result:
            settings = popup.get_settings()
            file_dir = QFileDialog.getExistingDirectory(self, "Export Image Sequence To...", self.last_save_location)
            if file_dir != "":
                self.last_save_location = os.path.split(file_dir)[0]
                frame_count = self.renderer.get_frame_count(fps=settings["fps"])
                pp = QProgressDialog("Exporting image sequence...", "Abort", 0, frame_count, self)
                pp.setWindowModality(Qt.WindowModal)
                pp.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
                pp.setWindowTitle("Exporting Images...")
                pp.setFixedSize(300, 100)
                try:
                    self.renderer.export_sequence(directory=file_dir, size=(settings["width"], settings["height"]),
                                                  fps=settings["fps"], keep_aspect=settings["keep_aspect"],
                                                  image_format=settings["format"], progress_dialog=pp)
                except Exception as e:
                    pp.cancel()
                    QMessageBox.critical(self, "Export Error", f"An error occurred: {str(e)}", QMessageBox.Ok)
                else:
                    if pp.wasCanceled():
                        QMessageBox.warning(self, "Export Aborted", "Export image sequence aborted!", QMessageBox.Ok)
                    else:
                        QMessageBox.information(self, "Export Complete", "Export image sequence successful!", QMessageBox.Ok)

    def export_video_clicked(self):
        if self.bw.audio_filename is None:
            QMessageBox.critical(self, "Error",
                "There is no file open in the viewer to export.\n\nPlease open a file and try again.",
                QMessageBox.Cancel)
            return
        popup = dialogs.ExportVideo(width=self.player.width, height=self.player.height, parent=self)
        result = popup.exec()
        if result:
            settings = popup.get_settings()
            filename, filetype = QFileDialog.getSaveFileName(
                self, "Export Video As...",
                os.path.join(self.last_save_location, f"{self.file_savename}{constants.VideoFormatCode.MP4.value}"),
                f"MP4 (*{constants.VideoFormatCode.MP4.value});;AVI (*{constants.VideoFormatCode.AVI.value})"
            )
            if filename != "":
                self.last_save_location = os.path.split(filename)[0]
                file_main_name, file_ext = os.path.splitext(os.path.split(filename)[1])
                file_ext = file_ext.lower()
                ep = dialogs.VideoEncoderSettings(video_format=constants.VideoFormatCode(file_ext), parent=self)
                er = ep.exec()
                if er:
                    es = ep.get_settings()
                    frame_count = self.renderer.get_frame_count(fps=settings["fps"])
                    pp = QProgressDialog("Rendering frames...", "Abort", 0, frame_count, self)
                    pp.setWindowModality(Qt.WindowModal)
                    pp.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
                    pp.setWindowTitle("Exporting Video...")
                    pp.setFixedSize(300, 100)
                    try:
                        self.renderer.export_video(filename=filename, size=(settings["width"], settings["height"]),
                                                   fps=settings["fps"], keep_aspect=settings["keep_aspect"],
                                                   progress_dialog=pp, codec=es["codec"].value,
                                                   audio_codec=es["audio_codec"].value,
                                                   bitrate=None, audio_bitrate=None, preset=es["preset"].value)
                    except Exception as e:
                        pp.cancel()
                        QMessageBox.critical(self, "Export Error", f"An error occurred: {str(e)}", QMessageBox.Ok)
                    else:
                        if pp.wasCanceled():
                            QMessageBox.warning(self, "Export Aborted", "Export video aborted!", QMessageBox.Ok)
                        else:
                            QMessageBox.information(self, "Export Complete", "Export video successful!", QMessageBox.Ok)

    def hotkeys_clicked(self):
        dialogs.HotkeysInfo(parent=self).exec()

    def about_clicked(self):
        dialogs.About(parent=self).exec()