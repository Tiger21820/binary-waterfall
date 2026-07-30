import math
from PyQt5.QtCore import QSize, Qt, QRect, QRectF, QPoint, QPointF
from PyQt5.QtWidgets import QAbstractButton, QSlider, QStyle, QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont, QFontMetrics

from . import constants


# ==============================================================================
# Material Design 3 Helpers
# ==============================================================================

class M3Style:
    """Shared rendering helpers for M3 components."""

    @staticmethod
    def draw_ripple(painter, rect, color, press_state=0.0):
        """Draw a simple ripple overlay."""
        pass  # Future: animated ripple effect

    @staticmethod
    def draw_elevated_surface(painter, rect, bg_color, radius, elevation=1):
        """Draw a surface with M3 elevation (simplified as solid fill)."""
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(bg_color)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

    @staticmethod
    def draw_filled_button(painter, rect, bg_color, text, text_color, radius, font=None):
        """Draw an M3 filled button."""
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(bg_color)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        if font:
            painter.setFont(font)
        painter.setPen(QColor(text_color))
        painter.drawText(rect, Qt.AlignCenter, text)


# ==============================================================================
# M3 Icon Button
# ==============================================================================
# Replaces ImageButton with an M3-style icon button using image resources.
class M3IconButton(QAbstractButton):
    """Material Design 3 icon button.

    Uses existing PNG image resources but displays them with
    M3-consistent sizing and hover/press state indication.
    The button has a 40x40dp touch target with the icon scaled to 24x24dp.

    States:
      - Enabled / Disabled
      - Resting / Hovered / Pressed
    """

    def __init__(self,
                 pixmap,
                 pixmap_hover=None,
                 pixmap_pressed=None,
                 scale=1.0,
                 parent=None,
                 tooltip=None
                 ):
        super().__init__(parent)
        self._scale = scale
        self._pixmap = pixmap
        self._pixmap_hover = pixmap_hover or pixmap
        self._pixmap_pressed = pixmap_pressed or pixmap_hover or pixmap
        self._icon_size = round(24 * scale)
        self._touch_size = round(40 * scale)

        self.setFixedSize(self._touch_size, self._touch_size)
        self.setCursor(Qt.PointingHandCursor)

        if tooltip:
            self.setToolTip(tooltip)

        self.pressed.connect(self.update)
        self.released.connect(self.update)

    def change_pixmaps(self, pixmap, pixmap_hover, pixmap_pressed):
        self._pixmap = pixmap
        self._pixmap_hover = pixmap_hover or pixmap
        self._pixmap_pressed = pixmap_pressed or self._pixmap_hover or pixmap
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        cx = rect.center().x()
        cy = rect.center().y()

        # --- State fill (hover/press) ---
        if self.isDown():
            fill_color = QColor(constants.COLORS["primary"])
            fill_color.setAlpha(30)
            painter.setBrush(QBrush(fill_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, constants.SHAPES["full"], constants.SHAPES["full"])
        elif self.underMouse():
            fill_color = QColor(constants.COLORS["on_surface"])
            fill_color.setAlpha(15)
            painter.setBrush(QBrush(fill_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, constants.SHAPES["full"], constants.SHAPES["full"])

        # --- Icon ---
        if self.isDown():
            pix = self._pixmap_pressed
        elif self.underMouse():
            pix = self._pixmap_hover
        else:
            pix = self._pixmap

        # Scale icon to touch size
        scaled = pix.scaled(
            self._icon_size, self._icon_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        icon_x = cx - scaled.width() // 2
        icon_y = cy - scaled.height() // 2
        painter.drawPixmap(icon_x, icon_y, scaled)

    def sizeHint(self):
        return QSize(self._touch_size, self._touch_size)


# ==============================================================================
# M3 Seeking Slider (SeekBar replacement)
# ==============================================================================
# An M3 continuous slider for seeking through audio.
# Features:
#   - Active track (primary) / Inactive track (surface variant)
#   - Thumb with hover/active state ring
#   - Click-to-seek on track
class M3SeekBar(QSlider):
    """Material Design 3 seeking slider.

    Horizontal only. Supports click-to-seek, drag-to-seek,
    and visual feedback on hover/press.
    """

    TRACK_HEIGHT = 4
    THUMB_RADIUS = 6
    THUMB_HOVER_RADIUS = 12
    THUMB_ACTIVE_RADIUS = 14

    def __init__(self, position_changed_function=None, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self._position_changed_function = position_changed_function
        self._hovered = False
        self._dragging = False

        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(0)

        self.setMouseTracking(True)

    def set_position_changed_function(self, fn):
        self._position_changed_function = fn

    def _value_from_pos(self, x):
        w = self.width() - 2 * constants.SHAPES["small"]
        if w <= 0:
            return self.minimum()
        ratio = (x - constants.SHAPES["small"]) / w
        ratio = max(0.0, min(1.0, ratio))
        return round(self.minimum() + ratio * (self.maximum() - self.minimum()))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            value = self._value_from_pos(event.x())
            self._set_value_safe(value)
            self.update()

    def mouseMoveEvent(self, event):
        if self._dragging:
            value = self._value_from_pos(event.x())
            self._set_value_safe(value)
            self.update()
        else:
            # Hover detection
            dx = abs(event.x() - self._thumb_x())
            self._hovered = dx < constants.SHAPES["large"]
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
            self.update()
            event.accept()

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def _thumb_x(self):
        if self.maximum() <= self.minimum():
            return self.width() // 2
        ratio = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
        margin = constants.SHAPES["small"]
        return margin + ratio * (self.width() - 2 * margin)

    def _set_value_safe(self, value):
        value = max(self.minimum(), min(self.maximum(), value))
        self.setValue(value)
        if self._position_changed_function:
            self._position_changed_function(value)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        margin = constants.SHAPES["small"]
        track_y = h // 2
        thumb_x = self._thumb_x()
        track_left = margin
        track_right = w - margin
        track_w = track_right - track_left

        if track_w <= 0:
            return

        ratio = (self.value() - self.minimum()) / max(1, (self.maximum() - self.minimum()))
        active_end = track_left + ratio * track_w

        # --- Inactive track (right side of thumb) ---
        inactive_color = QColor(constants.COLORS["surface_container_highest"])
        painter.setBrush(QBrush(inactive_color))
        painter.setPen(Qt.NoPen)
        inactive_rect = QRect(
            round(active_end), track_y - self.TRACK_HEIGHT // 2,
            round(track_right - active_end), self.TRACK_HEIGHT
        )
        painter.drawRoundedRect(inactive_rect, self.TRACK_HEIGHT / 2, self.TRACK_HEIGHT / 2)

        # --- Active track (left side of thumb) ---
        active_color = QColor(constants.COLORS["primary"])
        painter.setBrush(QBrush(active_color))
        active_rect = QRect(
            round(track_left), track_y - self.TRACK_HEIGHT // 2,
            round(active_end - track_left), self.TRACK_HEIGHT
        )
        painter.drawRoundedRect(active_rect, self.TRACK_HEIGHT / 2, self.TRACK_HEIGHT / 2)

        # --- Thumb ---
        thumb_color = QColor(constants.COLORS["primary"])

        if self._dragging:
            # Outer glow ring
            ring_color = QColor(thumb_color)
            ring_color.setAlpha(40)
            painter.setBrush(QBrush(ring_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(
                round(thumb_x - self.THUMB_ACTIVE_RADIUS),
                track_y - self.THUMB_ACTIVE_RADIUS,
                self.THUMB_ACTIVE_RADIUS * 2,
                self.THUMB_ACTIVE_RADIUS * 2,
                self.THUMB_ACTIVE_RADIUS,
                self.THUMB_ACTIVE_RADIUS
            )
        elif self._hovered:
            ring_color = QColor(thumb_color)
            ring_color.setAlpha(20)
            painter.setBrush(QBrush(ring_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(
                round(thumb_x - self.THUMB_HOVER_RADIUS),
                track_y - self.THUMB_HOVER_RADIUS,
                self.THUMB_HOVER_RADIUS * 2,
                self.THUMB_HOVER_RADIUS * 2,
                self.THUMB_HOVER_RADIUS,
                self.THUMB_HOVER_RADIUS
            )

        # Thumb dot
        painter.setBrush(QBrush(thumb_color))
        painter.setPen(QPen(QColor(constants.COLORS["surface"]), 2))
        painter.drawEllipse(QPoint(round(thumb_x), track_y), self.THUMB_RADIUS, self.THUMB_RADIUS)

    def sizeHint(self):
        return QSize(200, constants.SHAPES["large"] + 2 * self.THUMB_ACTIVE_RADIUS)


# ==============================================================================
# M3 Volume Slider
# ==============================================================================
# Vertical slider for volume control, M3 style.
class M3VolumeSlider(QSlider):
    """Material Design 3 vertical volume slider."""

    TRACK_WIDTH = 4
    THUMB_RADIUS = 6
    THUMB_HOVER_RADIUS = 12

    def __init__(self, parent=None):
        super().__init__(Qt.Vertical, parent)
        self._hovered = False
        self._dragging = False
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(100)
        self.setMouseTracking(True)

    def _value_from_pos(self, y):
        h = self.height() - 2 * constants.SHAPES["small"]
        if h <= 0:
            return self.minimum()
        # In vertical slider: bottom = min, top = max
        ratio = 1.0 - (y - constants.SHAPES["small"]) / h
        ratio = max(0.0, min(1.0, ratio))
        return round(self.minimum() + ratio * (self.maximum() - self.minimum()))

    def _thumb_y(self):
        if self.maximum() <= self.minimum():
            return self.height() // 2
        ratio = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
        margin = constants.SHAPES["small"]
        # bottom = min, top = max
        return self.height() - margin - ratio * (self.height() - 2 * margin)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            value = self._value_from_pos(event.y())
            self.setValue(max(self.minimum(), min(self.maximum(), value)))
            self.update()

    def mouseMoveEvent(self, event):
        if self._dragging:
            value = self._value_from_pos(event.y())
            self.setValue(max(self.minimum(), min(self.maximum(), value)))
            self.update()
        else:
            dy = abs(event.y() - self._thumb_y())
            self._hovered = dy < constants.SHAPES["large"]
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
            self.update()
            event.accept()

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        margin = constants.SHAPES["small"]
        track_x = w // 2
        thumb_y = self._thumb_y()
        track_top = margin
        track_bottom = h - margin
        track_len = track_bottom - track_top

        if track_len <= 0:
            return

        ratio = (self.value() - self.minimum()) / max(1, (self.maximum() - self.minimum()))
        # bottom = min (0), top = max (100)
        active_top = track_bottom - ratio * track_len

        # --- Inactive track (above thumb) ---
        inactive_color = QColor(constants.COLORS["surface_container_highest"])
        painter.setBrush(QBrush(inactive_color))
        painter.setPen(Qt.NoPen)
        inactive_rect = QRectF(
            track_x - self.TRACK_WIDTH / 2, track_top,
            self.TRACK_WIDTH, active_top - track_top
        )
        painter.drawRoundedRect(inactive_rect, self.TRACK_WIDTH / 2, self.TRACK_WIDTH / 2)

        # --- Active track (below thumb) ---
        active_color = QColor(constants.COLORS["primary"])
        painter.setBrush(QBrush(active_color))
        active_rect = QRectF(
            track_x - self.TRACK_WIDTH / 2, active_top,
            self.TRACK_WIDTH, track_bottom - active_top
        )
        painter.drawRoundedRect(active_rect, self.TRACK_WIDTH / 2, self.TRACK_WIDTH / 2)

        # --- Thumb ---
        thumb_color = QColor(constants.COLORS["primary"])

        if self._dragging:
            ring_color = QColor(thumb_color)
            ring_color.setAlpha(40)
            painter.setBrush(QBrush(ring_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                QPointF(track_x, thumb_y),
                self.THUMB_HOVER_RADIUS, self.THUMB_HOVER_RADIUS
            )
        elif self._hovered:
            ring_color = QColor(thumb_color)
            ring_color.setAlpha(20)
            painter.setBrush(QBrush(ring_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                QPointF(track_x, thumb_y),
                self.THUMB_HOVER_RADIUS, self.THUMB_HOVER_RADIUS
            )

        painter.setBrush(QBrush(thumb_color))
        painter.setPen(QPen(QColor(constants.COLORS["surface"]), 2))
        painter.drawEllipse(QPointF(track_x, thumb_y), self.THUMB_RADIUS, self.THUMB_RADIUS)

    def sizeHint(self):
        return QSize(2 * self.THUMB_HOVER_RADIUS + 2 * constants.SHAPES["small"], 100)


# ==============================================================================
# Backward-compatible aliases
# ==============================================================================
ImageButton = M3IconButton
SeekBar = M3SeekBar