import sys
import os
import shutil
import json
import threading
import time
import ssl
from urllib.request import urlopen, Request
from urllib.parse import quote

# ---------- SSL fix ----------
try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()
    SSL_CTX.check_hostname = False
    SSL_CTX.verify_mode = ssl.CERT_NONE
    print("[WARN] certifi не установлен — SSL-проверка отключена.")

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QTabWidget,
    QScrollArea, QGridLayout, QFrame, QColorDialog, QSpinBox,
    QDialog, QDialogButtonBox, QFormLayout, QFontComboBox, QLineEdit,
    QSlider, QDoubleSpinBox, QInputDialog, QMenu, QComboBox,
    QToolBar, QAction, QTextEdit
)
from PyQt5.QtGui import (
    QPixmap, QImage, QPainter, QColor, QPen, QBrush, QFont,
    QIcon, QTransform, QFontDatabase, QFontMetrics, QPalette,
    QTextOption
)
from PyQt5.QtCore import (
    Qt, QPoint, QPointF, QRect, QRectF, QSize,
    pyqtSignal, QEvent, QTimer
)

# ---------- Пути ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "font")
SAVE_DIR = os.path.join(BASE_DIR, "save")
DONE_DIR = os.path.join(BASE_DIR, "done")
ICON_PATH = os.path.join(BASE_DIR, "icon.png")
ICON_ICO_PATH = os.path.join(BASE_DIR, "icon.ico")

REQUIRED_DIRS = [FONT_DIR, SAVE_DIR, DONE_DIR]


def ensure_dirs():
    created = []
    for d in REQUIRED_DIRS:
        if not os.path.isdir(d):
            try:
                os.makedirs(d, exist_ok=True)
                created.append(d)
            except Exception as e:
                print(f"[ERROR] Не удалось создать папку {d}: {e}")
    return created


_CREATED_DIRS = ensure_dirs()
if _CREATED_DIRS:
    print("[INIT] Созданы папки:")
    for d in _CREATED_DIRS:
        print(f"       - {os.path.relpath(d, BASE_DIR)}")
else:
    print("[INIT] Все рабочие папки уже на месте.")


IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')

CLIPART_API_KEY = "cf_75372eecad50fbf88761def00ac41c5fef641631"
CLIPART_BASE = "https://clipart.free/api/clipart/search"
CLIPART_USER_AGENT = "MiniCanva/1.0 (PyQt5)"


# ============================================================
#                     ИКОНКИ
# ============================================================
def make_icon(name, size=28, color="#e0e0e0"):
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(color), 2))
    p.setBrush(Qt.NoBrush)
    s = size
    if name == "new":
        p.drawRect(4, 4, s - 8, s - 8)
        p.drawLine(s // 2, 8, s // 2, s - 8)
        p.drawLine(8, s // 2, s - 8, s // 2)
    elif name == "image":
        p.drawRect(4, 6, s - 8, s - 12)
        p.drawLine(4, s - 8, s // 2, s // 2)
        p.drawLine(s // 2, s // 2, s - 6, s - 8)
        p.setBrush(QColor(color))
        p.drawEllipse(s - 12, 10, 4, 4)
    elif name == "text":
        p.setFont(QFont("Arial", size - 10, QFont.Bold))
        p.drawText(pix.rect(), Qt.AlignCenter, "T")
    elif name == "save":
        p.drawRect(6, 4, s - 12, s - 8)
        p.drawRect(9, 4, s - 18, 8)
        p.drawRect(10, s - 12, s - 20, 6)
    elif name == "copy":
        p.drawRect(6, 8, s - 14, s - 14)
        p.setBrush(Qt.NoBrush)
        p.drawRect(10, 4, s - 14, s - 14)
    elif name == "front":
        p.drawRect(4, 4, s - 10, s - 10)
        p.setBrush(QColor(color))
        p.drawRect(10, 10, s - 10, s - 10)
    elif name == "back":
        p.setBrush(QColor(color))
        p.drawRect(4, 4, s - 10, s - 10)
        p.setBrush(Qt.NoBrush)
        p.drawRect(10, 10, s - 10, s - 10)
    elif name == "delete":
        p.drawLine(6, 6, s - 6, s - 6)
        p.drawLine(s - 6, 6, 6, s - 6)
    elif name == "store":
        p.drawRect(4, 8, s - 8, s - 12)
        p.drawLine(4, 12, s - 4, 12)
        p.drawLine(s // 2, 4, s // 2, 8)
    elif name == "folder":
        p.drawRect(4, 9, s - 8, s - 14)
        p.drawLine(4, 9, 11, 9)
        p.drawLine(11, 9, 14, 5)
        p.drawLine(14, 5, s - 4, 5)
        p.drawLine(s - 4, 5, s - 4, 9)
    elif name == "paste":
        p.drawRect(6, 6, s - 12, s - 12)
        p.drawRect(9, 3, s - 18, 6)
        p.drawLine(10, s // 2, s - 10, s // 2)
        p.drawLine(10, s // 2 + 6, s - 10, s // 2 + 6)
    elif name == "color":
        p.setBrush(QColor("#5a9cff"))
        p.drawEllipse(4, 4, s - 8, s - 8)
        p.setBrush(QColor("#f2c94c"))
        p.drawEllipse(s - 14, 4, 10, 10)
        p.setBrush(QColor("#eb5757"))
        p.drawEllipse(s - 14, s - 14, 10, 10)
    elif name == "color_off":
        p.setBrush(QColor("#3a3a3a"))
        p.drawEllipse(4, 4, s - 8, s - 8)
        p.setPen(QPen(QColor("#eb5757"), 2))
        p.drawLine(6, 6, s - 6, s - 6)
    elif name == "flip_h":
        p.drawLine(6, s // 2, s - 6, s // 2)
        p.drawLine(6, s // 2, 11, s // 2 - 4)
        p.drawLine(6, s // 2, 11, s // 2 + 4)
        p.drawLine(s - 6, s // 2, s - 11, s // 2 - 4)
        p.drawLine(s - 6, s // 2, s - 11, s // 2 + 4)
        p.drawLine(s // 2, 6, s // 2, s - 6)
    elif name == "flip_v":
        p.drawLine(s // 2, 6, s // 2, s - 6)
        p.drawLine(s // 2, 6, s // 2 - 4, 11)
        p.drawLine(s // 2, 6, s // 2 + 4, 11)
        p.drawLine(s // 2, s - 6, s // 2 - 4, s - 11)
        p.drawLine(s // 2, s - 6, s // 2 + 4, s - 11)
        p.drawLine(6, s // 2, s - 6, s // 2)
    elif name == "rotate":
        p.drawArc(6, 6, s - 12, s - 12, 30 * 16, 270 * 16)
        p.setBrush(QColor(color))
        p.drawPolygon(QPoint(s - 6, 6), QPoint(s - 12, 10), QPoint(s - 6, 14))
    elif name == "brush":
        p.save()
        p.translate(s // 2, s // 2)
        p.rotate(-45)
        p.translate(-s // 2, -s // 2)
        p.drawRect(s // 2 - 3, 4, 6, s - 16)
        p.setBrush(QColor(color))
        p.drawPolygon(
            QPoint(s // 2 - 3, s - 12),
            QPoint(s // 2 + 3, s - 12),
            QPoint(s // 2 + 1, s - 5),
            QPoint(s // 2 - 1, s - 5),
        )
        p.restore()
        p.setPen(QPen(QColor(color), 3))
        p.drawLine(4, s - 5, s - 10, s - 5)
    elif name == "eraser":
        p.save()
        p.translate(s // 2, s // 2)
        p.rotate(-30)
        p.translate(-s // 2, -s // 2)
        p.setBrush(QColor("#f2c94c"))
        p.drawPolygon(
            QPoint(6, s - 10),
            QPoint(s - 10, s - 10),
            QPoint(s - 6, s - 20),
            QPoint(10, s - 20),
        )
        p.setBrush(QColor("#d9d9d9"))
        p.drawPolygon(
            QPoint(6, s - 10),
            QPoint(s - 10, s - 10),
            QPoint(s - 12, s - 6),
            QPoint(8, s - 6),
        )
        p.restore()
    p.end()
    return QIcon(pix)


def make_info_icon(size=48, color="#5a9cff"):
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(color), 3))
    p.setBrush(QBrush(QColor(40, 60, 90, 200)))
    p.drawEllipse(3, 3, size - 6, size - 6)
    f = QFont("Georgia", int(size * 0.6), QFont.Bold)
    p.setFont(f)
    p.setPen(QColor(color))
    p.drawText(pix.rect(), Qt.AlignCenter, "i")
    p.end()
    return QIcon(pix)


# ============================================================
#                     БАЗОВЫЙ ЭЛЕМЕНТ
# ============================================================
class BaseItem:
    def __init__(self, pos: QPoint, display_size: QSize):
        self.pos = QPoint(pos)
        self.display_size = QSize(display_size)
        self.rotation = 0.0
        self.opacity = 1.0
        self.selected = False
        self.flip_h = False
        self.flip_v = False
        self.kind = "base"

    def rect(self) -> QRect:
        return QRect(self.pos, self.display_size)

    def contains(self, pt: QPoint) -> bool:
        return self.rect().contains(pt)

    def clone(self):
        raise NotImplementedError

    def draw(self, p: QPainter):
        raise NotImplementedError

    def _apply_transform(self, p: QPainter, target: QRect):
        if self.rotation == 0 and not self.flip_h and not self.flip_v:
            return
        cx = target.x() + target.width() / 2
        cy = target.y() + target.height() / 2
        p.translate(cx, cy)
        if self.rotation != 0:
            p.rotate(self.rotation)
        if self.flip_h or self.flip_v:
            p.scale(-1 if self.flip_h else 1,
                    -1 if self.flip_v else 1)
        p.translate(-cx, -cy)

    def bounding_rect(self) -> QRect:
        if self.rotation == 0:
            return self.rect()
        cx = self.pos.x() + self.display_size.width() / 2
        cy = self.pos.y() + self.display_size.height() / 2
        t = QTransform().translate(cx, cy).rotate(self.rotation).translate(-cx, -cy)
        return t.mapToPolygon(self.rect()).boundingRect()


# ============================================================
#                     IMAGE ITEM
# ============================================================
class ImageItem(BaseItem):
    def __init__(self, source_image: QImage, pos: QPoint, display_size: QSize):
        super().__init__(pos, display_size)
        self.kind = "image"
        self.source_image = source_image
        self.source_size = QSize(source_image.width(), source_image.height())
        self.processed_image = None
        self._processed_key = None
        self.rotation = 0.0
        self.opacity = 1.0
        self.crop = None
        self.filters = {"brightness": 0, "contrast": 0, "saturation": 0, "blur": 0}

    @property
    def scale(self) -> float:
        if self.source_size.width() == 0:
            return 1.0
        return self.display_size.width() / self.source_size.width()

    def _filters_key(self):
        c = self.crop
        crop_key = (c.x(), c.y(), c.width(), c.height()) if c else None
        return (tuple(sorted(self.filters.items())), crop_key)

    def _rebuild_processed(self):
        key = self._filters_key()
        if self._processed_key == key and self.processed_image is not None:
            return
        img = self.source_image
        if self.crop is not None:
            img = img.copy(self.crop.intersected(
                QRect(0, 0, img.width(), img.height())))
        b = self.filters.get("brightness", 0)
        c = self.filters.get("contrast", 0)
        s = self.filters.get("saturation", 0)
        if b != 0 or c != 0 or s != 0:
            img = img.convertToFormat(QImage.Format_ARGB32)
            cf = (259 * (c + 255)) / (255 * (259 - c)) if c != 0 else 1.0
            sb = 1.0 + (s / 100.0)
            for y in range(img.height()):
                for x in range(img.width()):
                    px = img.pixel(x, y)
                    a = (px >> 24) & 0xFF
                    r = (px >> 16) & 0xFF
                    g = (px >> 8) & 0xFF
                    bl = px & 0xFF
                    r += b
                    g += b
                    bl += b
                    if c != 0:
                        r = int(cf * (r - 128) + 128)
                        g = int(cf * (g - 128) + 128)
                        bl = int(cf * (bl - 128) + 128)
                    if s != 0:
                        gray = 0.299 * r + 0.587 * g + 0.114 * bl
                        r = gray + (r - gray) * sb
                        g = gray + (g - gray) * sb
                        bl = gray + (bl - gray) * sb
                    r = max(0, min(255, int(r)))
                    g = max(0, min(255, int(g)))
                    bl = max(0, min(255, int(bl)))
                    img.setPixel(x, y, (a << 24) | (r << 16) | (g << 8) | bl)
        self.processed_image = img
        self._processed_key = key

    def contains(self, pt: QPoint) -> bool:
        if self.rotation == 0:
            return self.rect().contains(pt)
        return self.bounding_rect().contains(pt)

    def clone(self):
        it = ImageItem(self.source_image, QPoint(self.pos), QSize(self.display_size))
        it.rotation = self.rotation
        it.opacity = self.opacity
        it.flip_h = self.flip_h
        it.flip_v = self.flip_v
        it.crop = QRect(self.crop) if self.crop else None
        it.filters = dict(self.filters)
        it.processed_image = self.processed_image
        it._processed_key = self._processed_key
        return it

    def draw(self, p: QPainter):
        self._rebuild_processed()
        if self.processed_image is None:
            return
        target = self.rect()
        pix = QPixmap.fromImage(self.processed_image)
        scaled = pix.scaled(target.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        dx = target.x() + (target.width() - scaled.width()) // 2
        dy = target.y() + (target.height() - scaled.height()) // 2
        p.save()
        p.setOpacity(self.opacity)
        self._apply_transform(p, target)
        p.drawPixmap(dx, dy, scaled)
        p.restore()


# ============================================================
#                     TEXT ITEM
# ============================================================
class TextItem(BaseItem):
    def __init__(self, text, font_family, font_size, color, pos, display_size):
        super().__init__(pos, display_size)
        self.kind = "text"
        self.text = text
        self.font_family = font_family
        self.font_size = font_size
        self.color = color
        self.bold = False
        self.italic = False
        self._recalc_base()

    def _make_font(self, size=None):
        f = QFont(self.font_family, size if size else self.font_size)
        f.setBold(self.bold)
        f.setItalic(self.italic)
        return f

    def _recalc_base(self):
        f = self._make_font()
        m = QFontMetrics(f)
        lines = self.text.split("\n") if self.text else [""]
        max_w = max((m.horizontalAdvance(line) for line in lines), default=0)
        line_h = m.lineSpacing()
        total_h = line_h * len(lines)
        self.base_w = max_w + 10
        self.base_h = total_h + 6

    def clone(self):
        it = TextItem(self.text, self.font_family, self.font_size,
                      QColor(self.color), QPoint(self.pos),
                      QSize(self.display_size))
        it.bold = self.bold
        it.italic = self.italic
        it.rotation = self.rotation
        it.opacity = self.opacity
        it.flip_h = self.flip_h
        it.flip_v = self.flip_v
        return it

    def contains(self, pt: QPoint) -> bool:
        if self.rotation == 0:
            return self.rect().contains(pt)
        return self.bounding_rect().contains(pt)

    def draw(self, p: QPainter):
        scale = self.display_size.width() / self.base_w if self.base_w else 1.0
        size = max(6, int(self.font_size * scale))
        f = self._make_font(size)
        target = self.rect()
        p.save()
        p.setOpacity(self.opacity)
        self._apply_transform(p, target)
        p.setFont(f)
        p.setPen(self.color)
        opt = QTextOption(Qt.AlignLeft | Qt.AlignVCenter)
        opt.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        p.drawText(QRectF(target), self.text, opt)
        p.restore()

    def set_text_inline(self, new_text: str):
        if new_text == self.text:
            return
        old_base_w = self.base_w
        self.text = new_text
        self._recalc_base()
        if old_base_w > 0 and self.base_w > 0:
            ratio_w = self.base_w / old_base_w
            new_w = max(10, int(self.display_size.width() * ratio_w))
        else:
            new_w = self.base_w
        if self.base_w > 0:
            scale = new_w / self.base_w
            new_h = max(10, int(self.base_h * scale))
        else:
            new_h = self.base_h
        self.display_size = QSize(new_w, new_h)

    def apply_edit(self, text=None, font_family=None, font_size=None,
                   color=None, bold=None, italic=None):
        old_base_w = self.base_w
        if text is not None:
            self.text = text
        if font_family is not None:
            self.font_family = font_family
        if font_size is not None:
            self.font_size = font_size
        if color is not None:
            self.color = QColor(color)
        if bold is not None:
            self.bold = bold
        if italic is not None:
            self.italic = italic

        self._recalc_base()

        if old_base_w > 0 and self.base_w > 0:
            ratio = self.base_w / old_base_w
            new_w = max(10, int(self.display_size.width() * ratio))
            new_h = max(10, int(new_w * self.base_h / self.base_w))
            self.display_size = QSize(new_w, new_h)
        else:
            self.display_size = QSize(self.base_w, self.base_h)


# ============================================================
#                     ХОЛСТ
# ============================================================
class Canvas(QWidget):
    item_selected = pyqtSignal(object)
    document_changed = pyqtSignal()
    request_edit_text = pyqtSignal(object)

    HANDLE = 10
    DOUBLE_CLICK_MS = 350

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        self.doc_size = QSize(800, 600)
        self.bg_color = Qt.transparent

        self.paint_layer = QImage(self.doc_size, QImage.Format_ARGB32)
        self.paint_layer.fill(Qt.transparent)

        self.items = []
        self.selected_items = []
        self.mode = None
        self.pan_start = QPoint()
        self.pan_offset = QPoint()
        self.pan_offset_start = QPoint()
        self.zoom = 1.0
        self.resize_item = None
        self.resize_handle = None
        self.resize_start_rect = None
        self.resize_start_pos = QPoint()
        self.resize_snapshot_done = False
        self.move_start_positions = {}
        self.move_start_mouse = QPoint()
        self.move_snapshot_done = False
        self.history = []
        self.clipboard = []
        self._last_click_time = 0
        self._last_click_item = None
        self._last_click_pos = QPoint()

        self.inline_edit = None
        self.inline_item = None
        self._inline_committing = False

        self.tool = "select"
        self.brush_color = QColor(255, 80, 80)
        self.brush_width = 15
        self.eraser_width = 25
        self._stroke_active = False
        self._stroke_last_pt = None
        self._stroke_snapshot_taken = False

    # ---- инструменты ----
    def set_tool(self, tool: str):
        self.commit_inline_edit()
        self.tool = tool
        if tool == "brush":
            self.setCursor(Qt.CrossCursor)
        elif tool == "eraser":
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        self.update()

    def set_brush_color(self, color: QColor):
        self.brush_color = QColor(color)

    def set_brush_width(self, w: int):
        self.brush_width = max(1, min(30, int(w)))

    def set_eraser_width(self, w: int):
        self.eraser_width = max(10, min(50, int(w)))

    # ---- рисование / ластик ----
    def _start_stroke(self, doc_pt: QPointF):
        if not self._stroke_snapshot_taken:
            self.push_history()
            self._stroke_snapshot_taken = True
        self._stroke_active = True
        self._stroke_last_pt = doc_pt
        self._draw_segment(doc_pt, doc_pt)

    def _end_stroke(self):
        self._stroke_active = False
        self._stroke_last_pt = None
        self._stroke_snapshot_taken = False

    def _draw_segment(self, pt1: QPointF, pt2: QPointF):
        painter = QPainter(self.paint_layer)
        painter.setRenderHint(QPainter.Antialiasing, True)
        if self.tool == "brush":
            pen = QPen(self.brush_color, self.brush_width,
                       Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        elif self.tool == "eraser":
            pen = QPen(QColor(0, 0, 0, 255), self.eraser_width,
                       Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
        else:
            painter.end()
            return
        painter.setPen(pen)
        painter.drawLine(pt1, pt2)
        painter.end()
        self.update()

    # ---- inline-редактирование ----
    def start_inline_edit(self, item: TextItem):
        if self.inline_edit is not None:
            self.commit_inline_edit()
        if item is None or item.kind != "text":
            return

        self.inline_item = item
        self.inline_edit = QTextEdit(self)
        self.inline_edit.setPlainText(item.text)
        self.inline_edit.setStyleSheet(
            "QTextEdit{background:#1e2a3a;color:#fff;"
            "border:2px solid #5a9cff;border-radius:4px;"
            "padding:2px 6px;selection-background-color:#5a9cff;}")

        scale = self.zoom
        font_size_px = max(8, int(item.font_size *
                                  item.display_size.width() /
                                  max(1, item.base_w) * scale))
        f = QFont(item.font_family)
        f.setPixelSize(font_size_px)
        f.setBold(item.bold)
        f.setItalic(item.italic)
        self.inline_edit.setFont(f)
        self.inline_edit.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        dr = self.doc_rect()
        x = int(item.pos.x() * self.zoom) + dr.x()
        y = int(item.pos.y() * self.zoom) + dr.y()
        w = max(180, int(item.display_size.width() * self.zoom) + 40)
        h = max(40, int(item.display_size.height() * self.zoom) + 20)
        self.inline_edit.setGeometry(x, y, w, h)

        self.inline_edit.setFocus()
        self.inline_edit.selectAll()
        self.inline_edit.focusOutEvent = self._inline_focus_out
        self.inline_edit.show()

    def _inline_focus_out(self, event):
        QTimer.singleShot(0, self.commit_inline_edit)
        QTextEdit.focusOutEvent(self.inline_edit, event)

    def commit_inline_edit(self):
        if self._inline_committing:
            return
        self._inline_committing = True
        try:
            if self.inline_edit is None or self.inline_item is None:
                return
            new_text = self.inline_edit.toPlainText()
            item = self.inline_item
            if new_text.strip() and new_text != item.text:
                self.push_history()
                item.set_text_inline(new_text)
                self.document_changed.emit()
            self.inline_edit.hide()
            self.inline_edit.deleteLater()
            self.inline_edit = None
            self.inline_item = None
            self.setFocus()
            self.update()
        finally:
            self._inline_committing = False

    def cancel_inline_edit(self):
        if self.inline_edit is None:
            return
        self._inline_committing = True
        try:
            self.inline_edit.hide()
            self.inline_edit.deleteLater()
            self.inline_edit = None
            self.inline_item = None
            self.setFocus()
            self.update()
        finally:
            self._inline_committing = False

    def _handle_inline_key(self, event):
        if self.inline_edit is None:
            return False
        key = event.key()
        mods = event.modifiers()
        if key == Qt.Key_Escape:
            self.cancel_inline_edit()
            return True
        if key in (Qt.Key_Return, Qt.Key_Enter) and (mods & Qt.ControlModifier):
            self.commit_inline_edit()
            return True
        return False

    # ---- контекстное меню ----
    def _show_context_menu(self, pos):
        if self.inline_edit is not None:
            return
        if self.tool in ("brush", "eraser"):
            return
        dpt = self.widget_to_doc(pos)
        clicked = None
        for it in reversed(self.items):
            if it.contains(dpt):
                clicked = it
                break
        if clicked is None:
            return
        if clicked not in self.selected_items:
            self.select_single(clicked)

        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu{background:#2b2b2b;color:#eee;border:1px solid #3a3a3a;}"
            "QMenu::item:selected{background:#5a9cff;color:#fff;}")

        if clicked.kind == "text":
            act_inline = menu.addAction("Редактировать на холсте")
            act_inline.triggered.connect(lambda: self.start_inline_edit(clicked))
            act_edit = menu.addAction("Настройки текста (F2)")
            act_edit.triggered.connect(
                lambda: self.request_edit_text.emit(clicked))
        if clicked.kind == "image":
            act_edit = menu.addAction("Настройки изображения (F2)")
            act_edit.triggered.connect(
                lambda: self.request_edit_text.emit(("image_settings", clicked)))
        menu.addSeparator()
        act_front = menu.addAction("На передний план")
        act_front.triggered.connect(self.bring_to_front)
        act_back = menu.addAction("На задний план")
        act_back.triggered.connect(self.send_to_back)
        menu.addSeparator()
        act_dup = menu.addAction("Дублировать (Ctrl+D)")
        act_dup.triggered.connect(self.duplicate_selected)
        act_del = menu.addAction("Удалить (Del)")
        act_del.triggered.connect(self.delete_selected)

        menu.exec_(self.mapToGlobal(pos))

    # ---- история ----
    def push_history(self):
        self.history.append({
            "items": [it.clone() for it in self.items],
            "paint": self.paint_layer.copy(),
        })
        if len(self.history) > 100:
            self.history.pop(0)

    def undo(self):
        if not self.history:
            return
        snap = self.history.pop()
        self.items = snap["items"]
        self.paint_layer = snap["paint"]
        for it in self.items:
            it.selected = False
        self.selected_items = []
        self.item_selected.emit(None)
        self.update()
        self.document_changed.emit()

    def new_document(self, w, h):
        self.commit_inline_edit()
        self.doc_size = QSize(w, h)
        self.paint_layer = QImage(self.doc_size, QImage.Format_ARGB32)
        self.paint_layer.fill(Qt.transparent)
        self.items.clear()
        self.selected_items = []
        self.zoom = 1.0
        self.pan_offset = QPoint()
        self.history.clear()
        self.update()
        self.document_changed.emit()

    def set_bg_color(self, color: QColor):
        self.bg_color = QColor(color)
        self.update()
        self.document_changed.emit()

    def reset_bg_color(self):
        self.bg_color = Qt.transparent
        self.update()
        self.document_changed.emit()

    def doc_rect(self) -> QRect:
        return QRect(self.pan_offset,
                     QSize(int(self.doc_size.width() * self.zoom),
                           int(self.doc_size.height() * self.zoom)))

    def widget_to_doc(self, pt: QPoint) -> QPoint:
        r = self.doc_rect()
        return QPoint(int((pt.x() - r.x()) / self.zoom),
                      int((pt.y() - r.y()) / self.zoom))

    def widget_to_doc_f(self, pt: QPoint) -> QPointF:
        r = self.doc_rect()
        return QPointF((pt.x() - r.x()) / self.zoom,
                       (pt.y() - r.y()) / self.zoom)

    def _check_out_of_bounds(self, it):
        if it is None or it not in self.items:
            return
        r = it.bounding_rect()
        obj_area = max(1, r.width() * r.height())
        inter = r.intersected(QRect(0, 0, self.doc_size.width(),
                                    self.doc_size.height()))
        inter_area = max(0, inter.width()) * max(0, inter.height())
        if inter_area / obj_area < 0.10:
            self.items.remove(it)
            if it in self.selected_items:
                self.selected_items.remove(it)
            if not self.selected_items:
                self.item_selected.emit(None)
            self.update()
            self.document_changed.emit()

    def _check_all_out_of_bounds(self):
        for it in list(self.items):
            self._check_out_of_bounds(it)

    def add_image(self, path):
        img = QImage(path)
        if img.isNull():
            return
        max_w = int(self.doc_size.width() * 0.7)
        max_h = int(self.doc_size.height() * 0.7)
        dw, dh = img.width(), img.height()
        if dw > max_w or dh > max_h:
            k = min(max_w / dw, max_h / dh)
            dw, dh = int(dw * k), int(dh * k)
        pos = QPoint(int(self.doc_size.width() / 2 - dw / 2),
                     int(self.doc_size.height() / 2 - dh / 2))
        item = ImageItem(img, pos, QSize(dw, dh))
        self.push_history()
        self.items.append(item)
        self.select_single(item)
        try:
            base = os.path.basename(path)
            dst = os.path.join(SAVE_DIR, base)
            if not os.path.exists(dst):
                shutil.copy(path, dst)
        except Exception:
            pass
        self.update()
        self.document_changed.emit()

    def add_text(self, text, font_family="Arial", font_size=36,
                 color=QColor(255, 255, 255)):
        f = QFont(font_family, font_size)
        m = QFontMetrics(f)
        lines = text.split("\n") if text else [""]
        max_w = max((m.horizontalAdvance(line) for line in lines), default=0)
        line_h = m.lineSpacing()
        w = max_w + 10
        h = line_h * len(lines) + 6
        pos = QPoint(int(self.doc_size.width() / 2 - w / 2),
                     int(self.doc_size.height() / 2 - h / 2))
        item = TextItem(text, font_family, font_size, color, pos, QSize(w, h))
        self.push_history()
        self.items.append(item)
        self.select_single(item)
        self.update()
        self.document_changed.emit()

    def select_single(self, item):
        for it in self.items:
            it.selected = False
        self.selected_items = []
        if item:
            item.selected = True
            self.selected_items = [item]
        self.item_selected.emit(item)
        self.update()

    def select_all(self):
        for it in self.items:
            it.selected = True
        self.selected_items = list(self.items)
        self.item_selected.emit(self.selected_items[0]
                                if self.selected_items else None)
        self.update()

    def delete_selected(self):
        if not self.selected_items:
            return
        if self.inline_item in self.selected_items:
            self.cancel_inline_edit()
        self.push_history()
        for it in self.selected_items:
            if it in self.items:
                self.items.remove(it)
        self.selected_items = []
        self.item_selected.emit(None)
        self.update()
        self.document_changed.emit()

    def copy_selected(self):
        self.clipboard = [it.clone() for it in self.selected_items]

    def cut_selected(self):
        if not self.selected_items:
            return
        self.copy_selected()
        self.delete_selected()

    def paste(self):
        if not self.clipboard:
            return
        self.push_history()
        new_items = []
        for it in self.clipboard:
            c = it.clone()
            c.pos = c.pos + QPoint(20, 20)
            new_items.append(c)
            self.items.append(c)
        for it in self.items:
            it.selected = False
        self.selected_items = new_items
        for it in new_items:
            it.selected = True
        self.item_selected.emit(new_items[0] if new_items else None)
        self.update()
        self.document_changed.emit()

    def paste_from_system_clipboard(self) -> bool:
        clipboard = QApplication.clipboard()
        mime = clipboard.mimeData()

        if mime.hasImage():
            img = clipboard.image()
            if img.isNull():
                return False
            img = img.convertToFormat(QImage.Format_ARGB32)
            max_w = int(self.doc_size.width() * 0.7)
            max_h = int(self.doc_size.height() * 0.7)
            dw, dh = img.width(), img.height()
            if dw > max_w or dh > max_h:
                k = min(max_w / dw, max_h / dh)
                dw, dh = int(dw * k), int(dh * k)
            pos = QPoint(int(self.doc_size.width() / 2 - dw / 2),
                         int(self.doc_size.height() / 2 - dh / 2))
            item = ImageItem(img, pos, QSize(dw, dh))
            self.push_history()
            self.items.append(item)
            self.select_single(item)
            try:
                fname = f"paste_{int(time.time() * 1000)}.png"
                img.save(os.path.join(SAVE_DIR, fname))
            except Exception:
                pass
            self.update()
            self.document_changed.emit()
            return True

        if mime.hasUrls():
            handled = False
            for url in mime.urls():
                path = url.toLocalFile()
                if path.lower().endswith(IMAGE_EXTS) and os.path.isfile(path):
                    self.add_image(path)
                    handled = True
            if handled:
                return True

        if mime.hasText():
            text = clipboard.text().strip()
            if not text:
                return False
            if len(text) > 300:
                text = text[:300] + "..."
            self.add_text(text, "Arial", 36, QColor(255, 255, 255))
            return True

        return False

    def duplicate_selected(self):
        if not self.selected_items:
            return
        self.push_history()
        new_items = []
        for it in self.selected_items:
            c = it.clone()
            c.pos = c.pos + QPoint(20, 20)
            new_items.append(c)
            self.items.append(c)
        for it in self.items:
            it.selected = False
        self.selected_items = new_items
        for it in new_items:
            it.selected = True
        self.item_selected.emit(new_items[0] if new_items else None)
        self.update()
        self.document_changed.emit()

    def flip_selected_horizontal(self):
        if not self.selected_items:
            return
        self.push_history()
        for it in self.selected_items:
            it.flip_h = not it.flip_h
        self.update()
        self.document_changed.emit()

    def flip_selected_vertical(self):
        if not self.selected_items:
            return
        self.push_history()
        for it in self.selected_items:
            it.flip_v = not it.flip_v
        self.update()
        self.document_changed.emit()

    def rotate_selected(self, angle_deg):
        if not self.selected_items:
            return
        self.push_history()
        for it in self.selected_items:
            it.rotation = (it.rotation + angle_deg) % 360
        self.update()
        self.document_changed.emit()

    def bring_forward(self):
        if not self.selected_items:
            return
        self.push_history()
        for it in self.selected_items:
            i = self.items.index(it)
            if i < len(self.items) - 1:
                self.items[i], self.items[i + 1] = self.items[i + 1], self.items[i]
        self.update()
        self.document_changed.emit()

    def send_backward(self):
        if not self.selected_items:
            return
        self.push_history()
        for it in reversed(self.selected_items):
            i = self.items.index(it)
            if i > 0:
                self.items[i], self.items[i - 1] = self.items[i - 1], self.items[i]
        self.update()
        self.document_changed.emit()

    def bring_to_front(self):
        if not self.selected_items:
            return
        self.push_history()
        for it in self.selected_items:
            self.items.remove(it)
            self.items.append(it)
        self.update()
        self.document_changed.emit()

    def send_to_back(self):
        if not self.selected_items:
            return
        self.push_history()
        for it in reversed(self.selected_items):
            self.items.remove(it)
            self.items.insert(0, it)
        self.update()
        self.document_changed.emit()

    def render_to_image(self) -> QImage:
        """Собирает полное изображение холста (фон + слой кисти + объекты)."""
        out = QImage(self.doc_size, QImage.Format_ARGB32)
        if self.bg_color != Qt.transparent and self.bg_color.alpha() > 0:
            out.fill(self.bg_color)
        else:
            out.fill(Qt.transparent)
        p = QPainter(out)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)
        p.drawImage(0, 0, self.paint_layer)
        for it in self.items:
            it.draw(p)
        p.end()
        return out

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(30, 30, 30))
        dr = self.doc_rect()

        cell = 16
        cols = dr.width() // cell + 1
        rows = dr.height() // cell + 1
        for y in range(rows):
            for x in range(cols):
                c = QColor(60, 60, 60) if (x + y) % 2 == 0 else QColor(45, 45, 45)
                p.fillRect(dr.x() + x * cell, dr.y() + y * cell,
                           min(cell, dr.width() - x * cell),
                           min(cell, dr.height() - y * cell), c)

        if self.bg_color != Qt.transparent and self.bg_color.alpha() > 0:
            p.fillRect(dr, self.bg_color)

        p.save()
        p.translate(dr.topLeft())
        p.scale(self.zoom, self.zoom)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)

        p.drawImage(0, 0, self.paint_layer)

        for it in self.items:
            if it is self.inline_item:
                continue
            it.draw(p)
        p.restore()

        p.setPen(QPen(QColor(120, 120, 120), 1))
        p.drawRect(dr)

        if self.tool in ("brush", "eraser"):
            cur = self.mapFromGlobal(self.cursor().pos())
            if self.rect().contains(cur):
                width = self.brush_width if self.tool == "brush" else self.eraser_width
                radius = max(2, int(width * self.zoom / 2))
                p.setBrush(Qt.NoBrush)
                if self.tool == "brush":
                    p.setPen(QPen(QColor(200, 200, 200, 200), 1))
                else:
                    p.setPen(QPen(QColor(242, 201, 76, 220), 1, Qt.DashLine))
                p.drawEllipse(cur, radius, radius)

        for it in self.selected_items:
            if it is self.inline_item:
                continue
            br = it.bounding_rect()
            r = QRect(int(br.x() * self.zoom) + dr.x(),
                      int(br.y() * self.zoom) + dr.y(),
                      int(br.width() * self.zoom),
                      int(br.height() * self.zoom))
            p.setPen(QPen(QColor(80, 160, 255), 2, Qt.DashLine))
            p.setBrush(Qt.NoBrush)
            p.drawRect(r)
            p.setPen(QPen(QColor(80, 160, 255), 2))
            p.setBrush(QBrush(QColor(80, 160, 255)))
            h = self.HANDLE
            for pt in [r.topLeft(), r.topRight(), r.bottomLeft(), r.bottomRight()]:
                p.drawRect(pt.x() - h // 2, pt.y() - h // 2, h, h)

    def _handle_at(self, widget_pt):
        if not self.selected_items:
            return None
        dr = self.doc_rect()
        h = self.HANDLE
        for it in self.selected_items:
            if it is self.inline_item:
                continue
            br = it.bounding_rect()
            r = QRect(int(br.x() * self.zoom) + dr.x(),
                      int(br.y() * self.zoom) + dr.y(),
                      int(br.width() * self.zoom),
                      int(br.height() * self.zoom))
            pts = {'tl': r.topLeft(), 'tr': r.topRight(),
                   'bl': r.bottomLeft(), 'br': r.bottomRight()}
            for k, pt in pts.items():
                if abs(widget_pt.x() - pt.x()) <= h and abs(widget_pt.y() - pt.y()) <= h:
                    return (it, k)
        return None

    def mousePressEvent(self, event):
        pos = event.pos()
        self.setFocus()

        if self.inline_edit is not None:
            if not self.inline_edit.geometry().contains(pos):
                self.commit_inline_edit()

        if event.button() == Qt.MiddleButton:
            self.mode = 'pan'
            self.pan_start = pos
            self.pan_offset_start = QPoint(self.pan_offset)
            return

        if event.button() != Qt.LeftButton:
            return

        if self.tool in ("brush", "eraser"):
            dpt = self.widget_to_doc_f(pos)
            self._start_stroke(dpt)
            return

        h = self._handle_at(pos)
        if h:
            it, key = h
            self.mode = 'resize'
            self.resize_handle = key
            self.resize_start_rect = QRect(it.pos, it.display_size)
            self.resize_start_pos = pos
            self.resize_item = it
            self.resize_snapshot_done = False
            return

        dpt = self.widget_to_doc(pos)
        clicked = None
        for it in reversed(self.items):
            if it.contains(dpt):
                clicked = it
                break

        ctrl = event.modifiers() & Qt.ControlModifier

        now = int(time.time() * 1000)
        is_double = (clicked is not None
                     and clicked is self._last_click_item
                     and (now - self._last_click_time) < self.DOUBLE_CLICK_MS)

        if is_double and clicked.kind == "text":
            self._last_click_time = 0
            self._last_click_item = None
            self.select_single(clicked)
            self.start_inline_edit(clicked)
            return

        self._last_click_time = now
        self._last_click_item = clicked
        self._last_click_pos = dpt

        if clicked:
            if ctrl:
                if clicked in self.selected_items:
                    clicked.selected = False
                    self.selected_items.remove(clicked)
                else:
                    clicked.selected = True
                    self.selected_items.append(clicked)
                self.item_selected.emit(
                    clicked if clicked in self.selected_items
                    else (self.selected_items[0] if self.selected_items else None))
            else:
                if clicked not in self.selected_items:
                    self.select_single(clicked)
            self.mode = 'move'
            self.drag_offset = dpt - clicked.pos
            self.move_start_positions = {id(it): QPoint(it.pos)
                                         for it in self.selected_items}
            self.move_start_mouse = dpt
            self.move_snapshot_done = False
        else:
            if not ctrl:
                self.select_single(None)
            self.mode = None

    def mouseMoveEvent(self, event):
        pos = event.pos()

        if self.inline_edit is not None:
            return

        if self.mode == 'pan':
            self.pan_offset = self.pan_offset_start + (pos - self.pan_start)
            self.update()
            return

        if self.tool in ("brush", "eraser") and self._stroke_active:
            dpt = self.widget_to_doc_f(pos)
            if self._stroke_last_pt is not None:
                self._draw_segment(self._stroke_last_pt, dpt)
            self._stroke_last_pt = dpt
            return

        if self.mode == 'move' and self.selected_items:
            if not self.move_snapshot_done:
                self.push_history()
                self.move_snapshot_done = True
            dpt = self.widget_to_doc(pos)
            delta = dpt - self.move_start_mouse
            for it in self.selected_items:
                it.pos = self.move_start_positions[id(it)] + delta
            self.update()
            self.document_changed.emit()
            return

        if self.mode == 'resize' and self.selected_items:
            if not self.resize_snapshot_done:
                self.push_history()
                self.resize_snapshot_done = True
            it = self.resize_item
            sr = self.resize_start_rect
            delta = pos - self.resize_start_pos
            dx = int(delta.x() / self.zoom)
            dy = int(delta.y() / self.zoom)
            h = self.resize_handle
            x = sr.x()
            y = sr.y()
            w = sr.width()
            hh = sr.height()
            if h == 'br':
                w += dx
                hh += dy
            elif h == 'tl':
                x += dx
                y += dy
                w -= dx
                hh -= dy
            elif h == 'tr':
                y += dy
                w += dx
                hh -= dy
            elif h == 'bl':
                x += dx
                w -= dx
                hh += dy
            if w < 10:
                w = 10
            if hh < 10:
                hh = 10
            it.pos = QPoint(x, y)
            it.display_size = QSize(w, hh)
            self.update()
            self.document_changed.emit()
            return

        if self.tool in ("brush", "eraser"):
            self.update()
            return

        if self._handle_at(pos):
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if self.tool in ("brush", "eraser") and self._stroke_active:
            self._end_stroke()
            self.document_changed.emit()
            return
        if self.mode in ('move', 'resize'):
            self._check_all_out_of_bounds()
        self.mode = None
        self.resize_handle = None
        if self.tool == "select":
            self.setCursor(Qt.ArrowCursor)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            old_zoom = self.zoom
            delta = event.angleDelta().y() / 120
            if delta > 0:
                self.zoom = min(5.0, self.zoom * 1.1)
            else:
                self.zoom = max(0.1, self.zoom / 1.1)
            cursor = event.pos()
            r = self.doc_rect()
            rel_x = (cursor.x() - r.x()) / old_zoom
            rel_y = (cursor.y() - r.y()) / old_zoom
            self.pan_offset = QPoint(int(cursor.x() - rel_x * self.zoom),
                                     int(cursor.y() - rel_y * self.zoom))
            self.update()
        else:
            delta = event.angleDelta().y()
            self.pan_offset = self.pan_offset + QPoint(0, int(delta / 3))
            self.update()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(IMAGE_EXTS):
                self.add_image(path)

    def keyPressEvent(self, event):
        if self.inline_edit is not None:
            if self._handle_inline_key(event):
                event.accept()
                return
            event.ignore()
            return

        ctrl = bool(event.modifiers() & Qt.ControlModifier)
        key = event.key()
        if ctrl and key == Qt.Key_C:
            self.copy_selected()
            event.accept()
            return
        if ctrl and key == Qt.Key_X:
            self.cut_selected()
            event.accept()
            return
        if ctrl and key == Qt.Key_V:
            if self.paste_from_system_clipboard():
                event.accept()
                return
            self.paste()
            event.accept()
            return
        if ctrl and key == Qt.Key_A:
            self.select_all()
            event.accept()
            return
        if ctrl and key == Qt.Key_Z:
            self.undo()
            event.accept()
            return
        if ctrl and key == Qt.Key_D:
            self.duplicate_selected()
            event.accept()
            return
        if key == Qt.Key_F2:
            if len(self.selected_items) == 1:
                sel = self.selected_items[0]
                if sel.kind == "text":
                    self.request_edit_text.emit(sel)
                    event.accept()
                    return
                elif sel.kind == "image":
                    self.request_edit_text.emit(("image_settings", sel))
                    event.accept()
                    return
        if key in (Qt.Key_Delete, Qt.Key_Backspace):
            self.delete_selected()
            event.accept()
            return
        if key == Qt.Key_Escape:
            if self.tool in ("brush", "eraser"):
                self.set_tool("select")
            else:
                self.select_single(None)
            event.accept()
            return
        super().keyPressEvent(event)


# ============================================================
#                     ДИАЛОГИ
# ============================================================
class NewDocDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новый макет")
        self.setStyleSheet("background:#2b2b2b; color:#eee;")
        form = QFormLayout(self)
        self.w = QSpinBox()
        self.w.setRange(50, 5000)
        self.w.setValue(500)
        self.h = QSpinBox()
        self.h.setRange(50, 5000)
        self.h.setValue(500)
        self.w.setStyleSheet("background:#3a3a3a;color:#eee;padding:4px;")
        self.h.setStyleSheet("background:#3a3a3a;color:#eee;padding:4px;")
        form.addRow("Ширина (px):", self.w)
        form.addRow("Высота (px):", self.h)
        presets = QHBoxLayout()
        for name, (ww, hh) in [("500x500", (500, 500)),
                               ("1080x1080", (1080, 1080)),
                               ("1920x1080", (1920, 1080)),
                               ("1080x1920", (1080, 1920))]:
            b = QPushButton(name)
            b.setStyleSheet(
                "background:#3a3a3a;color:#eee;padding:6px;border-radius:4px;")
            b.clicked.connect(lambda _, a=ww, b_=hh:
                              (self.w.setValue(a), self.h.setValue(b_)))
            presets.addWidget(b)
        form.addRow("Шаблоны:", presets)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)

    def values(self):
        return self.w.value(), self.h.value()


class TextEditDialog(QDialog):
    def __init__(self, parent=None, item: TextItem = None):
        super().__init__(parent)
        self.item = item
        self.setWindowTitle("Редактирование текста" if item
                            else "Добавить текст")
        self.setMinimumWidth(420)
        self.setStyleSheet("background:#2b2b2b; color:#eee;")
        form = QFormLayout(self)

        if item:
            init_text = item.text
            init_family = item.font_family
            init_size = item.font_size
            init_color = QColor(item.color)
            init_bold = item.bold
            init_italic = item.italic
        else:
            init_text = "Ваш текст"
            init_family = "Arial"
            init_size = 36
            init_color = QColor(255, 255, 255)
            init_bold = False
            init_italic = False

        self.text = QTextEdit()
        self.text.setPlainText(init_text)
        self.text.setFixedHeight(80)
        self.text.setStyleSheet(
            "background:#3a3a3a;color:#eee;padding:6px;"
            "border:1px solid #4a4a4a;border-radius:4px;")
        self.text.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        self.font = QFontComboBox()
        self.font.setStyleSheet("background:#3a3a3a;color:#eee;padding:4px;")
        self.font.setCurrentFont(QFont(init_family))

        self.size = QSpinBox()
        self.size.setRange(8, 500)
        self.size.setValue(init_size)
        self.size.setStyleSheet("background:#3a3a3a;color:#eee;padding:4px;")

        self.color = init_color
        self.color_btn = QPushButton("Цвет текста")
        self.color_btn.setStyleSheet(
            f"background:{self.color.name()};color:#000;"
            "padding:6px;border-radius:4px;font-weight:bold;")
        self.color_btn.clicked.connect(self.pick_color)

        style_row = QHBoxLayout()
        self.bold_btn = QPushButton("Ж")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setChecked(init_bold)
        self.bold_btn.setFixedWidth(40)
        self.bold_btn.setStyleSheet(
            "QPushButton{background:#3a3a3a;color:#eee;padding:6px;border-radius:4px;}"
            "QPushButton:checked{background:#5a9cff;color:#fff;font-weight:bold;}")
        self.bold_btn.setFont(QFont("Arial", 12, QFont.Bold))

        self.italic_btn = QPushButton("К")
        self.italic_btn.setCheckable(True)
        self.italic_btn.setChecked(init_italic)
        self.italic_btn.setFixedWidth(40)
        self.italic_btn.setStyleSheet(
            "QPushButton{background:#3a3a3a;color:#eee;padding:6px;border-radius:4px;}"
            "QPushButton:checked{background:#5a9cff;color:#fff;}")
        f = QFont("Arial", 12)
        f.setItalic(True)
        self.italic_btn.setFont(f)

        style_row.addWidget(QLabel("Стиль:"))
        style_row.addWidget(self.bold_btn)
        style_row.addWidget(self.italic_btn)
        style_row.addStretch()

        form.addRow("Текст:", self.text)
        form.addRow("Шрифт:", self.font)
        form.addRow("Размер:", self.size)
        form.addRow("", self.color_btn)
        form.addRow("", style_row)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)

    def pick_color(self):
        c = QColorDialog.getColor(self.color, self, "Цвет текста")
        if c.isValid():
            self.color = c
            self.color_btn.setStyleSheet(
                f"background:{c.name()};color:#000;"
                "padding:6px;border-radius:4px;font-weight:bold;")

    def values(self):
        return {
            "text": self.text.toPlainText(),
            "font_family": self.font.currentFont().family(),
            "font_size": self.size.value(),
            "color": self.color,
            "bold": self.bold_btn.isChecked(),
            "italic": self.italic_btn.isChecked(),
        }


class RotateDialog(QDialog):
    def __init__(self, parent=None, initial=45.0):
        super().__init__(parent)
        self.setWindowTitle("Повернуть объект")
        self.setStyleSheet("background:#2b2b2b; color:#eee;")
        form = QFormLayout(self)
        self.angle = QDoubleSpinBox()
        self.angle.setRange(-360, 360)
        self.angle.setValue(initial)
        self.angle.setDecimals(1)
        self.angle.setSingleStep(5.0)
        self.angle.setStyleSheet("background:#3a3a3a;color:#eee;padding:4px;")
        form.addRow("Угол (°):", self.angle)
        presets = QHBoxLayout()
        for a in (15, 30, 45, 90, 180, -90):
            b = QPushButton(f"{a}°")
            b.setStyleSheet(
                "background:#3a3a3a;color:#eee;padding:4px 8px;border-radius:4px;")
            b.clicked.connect(lambda _, v=a: self.angle.setValue(v))
            presets.addWidget(b)
        form.addRow("Пресеты:", presets)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)

    def value(self):
        return self.angle.value()


class ImageSettingsDialog(QDialog):
    def __init__(self, item: ImageItem, parent=None):
        super().__init__(parent)
        self.item = item
        self.setWindowTitle("Настройки изображения")
        self.setStyleSheet("background:#2b2b2b; color:#eee;")
        form = QFormLayout(self)

        def slider_row(label, minv, maxv, val):
            row = QHBoxLayout()
            s = QSlider(Qt.Horizontal)
            s.setRange(minv, maxv)
            s.setValue(val)
            s.setStyleSheet(
                "QSlider::groove:horizontal{height:6px;background:#3a3a3a;}"
                "QSlider::handle:horizontal{background:#5a9cff;width:12px;"
                "margin:-4px 0;border-radius:6px;}")
            lbl = QLabel(str(val))
            lbl.setFixedWidth(40)
            lbl.setStyleSheet("color:#ccc;")
            s.valueChanged.connect(lambda v, l=lbl: l.setText(str(v)))
            row.addWidget(s)
            row.addWidget(lbl)
            form.addRow(label, row)
            return s

        self.brightness = slider_row("Яркость", -100, 100,
                                     item.filters.get("brightness", 0))
        self.contrast = slider_row("Контраст", -100, 100,
                                   item.filters.get("contrast", 0))
        self.saturation = slider_row("Насыщенность", -100, 100,
                                     item.filters.get("saturation", 0))
        self.rotation = QDoubleSpinBox()
        self.rotation.setRange(-360, 360)
        self.rotation.setValue(item.rotation)
        self.rotation.setStyleSheet("background:#3a3a3a;color:#eee;padding:4px;")
        form.addRow("Поворот (°):", self.rotation)
        op_row = QHBoxLayout()
        self.opacity = QSlider(Qt.Horizontal)
        self.opacity.setRange(0, 100)
        self.opacity.setValue(int(item.opacity * 100))
        self.opacity.setStyleSheet(
            "QSlider::groove:horizontal{height:6px;background:#3a3a3a;}"
            "QSlider::handle:horizontal{background:#5a9cff;width:12px;"
            "margin:-4px 0;border-radius:6px;}")
        op_lbl = QLabel(f"{int(item.opacity * 100)}%")
        op_lbl.setFixedWidth(40)
        op_lbl.setStyleSheet("color:#ccc;")
        self.opacity.valueChanged.connect(lambda v: op_lbl.setText(f"{v}%"))
        op_row.addWidget(self.opacity)
        op_row.addWidget(op_lbl)
        form.addRow("Прозрачность:", op_row)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)

    def apply(self):
        self.item.filters["brightness"] = self.brightness.value()
        self.item.filters["contrast"] = self.contrast.value()
        self.item.filters["saturation"] = self.saturation.value()
        self.item.rotation = self.rotation.value()
        self.item.opacity = self.opacity.value() / 100.0
        self.item._processed_key = None


class BrushSettingsDialog(QDialog):
    def __init__(self, parent=None, color=None, width=15, apply_mode=False):
        super().__init__(parent)
        self.setWindowTitle("Кисть")
        self.setStyleSheet("background:#2b2b2b; color:#eee;")
        self.setMinimumWidth(320)
        form = QFormLayout(self)

        if apply_mode:
            hint = QLabel("Настройте кисть и нажмите ОК, чтобы начать рисовать")
            hint.setStyleSheet("color:#5a9cff;font-size:11px;")
            hint.setWordWrap(True)
            form.addRow("", hint)

        self.color = QColor(color) if color else QColor(255, 80, 80)
        self.color_btn = QPushButton("Цвет кисти")
        self.color_btn.setStyleSheet(
            f"background:{self.color.name()};color:#000;"
            "padding:8px;border-radius:4px;font-weight:bold;")
        self.color_btn.clicked.connect(self.pick_color)
        form.addRow("", self.color_btn)

        row = QHBoxLayout()
        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setRange(1, 30)
        self.width_slider.setValue(width)
        self.width_slider.setStyleSheet(
            "QSlider::groove:horizontal{height:6px;background:#3a3a3a;}"
            "QSlider::handle:horizontal{background:#5a9cff;width:14px;"
            "margin:-4px 0;border-radius:7px;}")
        self.width_lbl = QLabel(f"{width} px")
        self.width_lbl.setFixedWidth(50)
        self.width_lbl.setStyleSheet("color:#ccc;")
        self.width_slider.valueChanged.connect(
            lambda v: self.width_lbl.setText(f"{v} px"))
        row.addWidget(self.width_slider)
        row.addWidget(self.width_lbl)
        form.addRow("Толщина:", row)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)

    def pick_color(self):
        c = QColorDialog.getColor(self.color, self, "Цвет кисти")
        if c.isValid():
            self.color = c
            self.color_btn.setStyleSheet(
                f"background:{c.name()};color:#000;"
                "padding:8px;border-radius:4px;font-weight:bold;")

    def values(self):
        return self.color, self.width_slider.value()


class EraserSettingsDialog(QDialog):
    def __init__(self, parent=None, width=25, apply_mode=False):
        super().__init__(parent)
        self.setWindowTitle("Ластик")
        self.setStyleSheet("background:#2b2b2b; color:#eee;")
        self.setMinimumWidth(320)
        form = QFormLayout(self)

        if apply_mode:
            hint = QLabel("Настройте толщину и нажмите ОК, чтобы начать стирать")
            hint.setStyleSheet("color:#f2c94c;font-size:11px;")
            hint.setWordWrap(True)
            form.addRow("", hint)

        row = QHBoxLayout()
        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setRange(10, 50)
        self.width_slider.setValue(width)
        self.width_slider.setStyleSheet(
            "QSlider::groove:horizontal{height:6px;background:#3a3a3a;}"
            "QSlider::handle:horizontal{background:#f2c94c;width:14px;"
            "margin:-4px 0;border-radius:7px;}")
        self.width_lbl = QLabel(f"{width} px")
        self.width_lbl.setFixedWidth(50)
        self.width_lbl.setStyleSheet("color:#ccc;")
        self.width_slider.valueChanged.connect(
            lambda v: self.width_lbl.setText(f"{v} px"))
        row.addWidget(self.width_slider)
        row.addWidget(self.width_lbl)
        form.addRow("Толщина:", row)

        hint2 = QLabel("Ластик удаляет только линии, нарисованные кистью.")
        hint2.setStyleSheet("color:#888;font-size:11px;")
        hint2.setWordWrap(True)
        form.addRow("", hint2)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)

    def value(self):
        return self.width_slider.value()


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Горячие клавиши и справка")
        self.resize(640, 720)
        self.setStyleSheet("background:#232323; color:#eee;")

        v = QVBoxLayout(self)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(12)

        title = QLabel("Mini Canva — справка")
        title.setStyleSheet("color:#fff;font-size:20px;font-weight:bold;")
        v.addWidget(title)

        subtitle = QLabel("Все горячие клавиши и возможности редактора")
        subtitle.setStyleSheet("color:#9aa;font-size:12px;")
        v.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:#1e1e1e;border:none;border-radius:6px;")

        inner = QWidget()
        inner.setStyleSheet("background:#1e1e1e;")
        gv = QVBoxLayout(inner)
        gv.setContentsMargins(14, 14, 14, 14)
        gv.setSpacing(6)

        sections = [
            ("Работа с макетом", [
                ("Новый макет", "—", "Создать холст любого размера"),
                ("Сохранить", "—", "Сохранить результат в папку done/"),
                ("Копировать холст", "—", "Всё изображение в буфер обмена"),
                ("Цвет фона", "—", "Выбрать цвет фона макета (с альфой)"),
                ("Прозрачный фон", "—", "Сбросить фон на прозрачный"),
            ]),
            ("Кисть и ластик", [
                ("Кисть", "кнопка",
                 "Откроются настройки: цвет + толщина 1–30 px"),
                ("Ластик", "кнопка",
                 "Откроются настройки: толщина 10–50 px"),
                ("Отменить штрих", "Ctrl + Z", "Каждый штрих — один шаг"),
                ("Выйти из режима", "Esc", "Вернуться в выделение"),
            ]),
            ("Текст", [
                ("Двойной клик по тексту", "2x ЛКМ",
                 "Редактировать на холсте"),
                ("Новая строка", "Enter", "Перенос строки"),
                ("Применить inline", "Ctrl + Enter", "Сохранить и закрыть"),
                ("Применить", "клик вне поля", "Автосохранение"),
                ("Отменить inline", "Esc", "Вернуть исходный текст"),
                ("Расширенные настройки", "F2 / ПКМ",
                 "Шрифт, размер, цвет, жирный / курсив"),
            ]),
            ("Объекты", [
                ("Копировать", "Ctrl + C", "Копировать выделенное"),
                ("Вырезать", "Ctrl + X", "Вырезать в буфер"),
                ("Вставить", "Ctrl + V", "Вставить из буфера"),
                ("Выделить всё", "Ctrl + A", "Выделить все объекты"),
                ("Дублировать", "Ctrl + D", "Дублировать"),
                ("Удалить", "Del / Backspace", "Удалить объект"),
                ("Снять выделение", "Esc", "Снять выделение"),
                ("Отменить", "Ctrl + Z", "Отменить действие"),
            ]),
            ("Перемещение и масштаб", [
                ("Перемещение", "ЛКМ + drag", "Двигать объект"),
                ("Ресайз", "угловые ручки", "Изменить размер"),
                ("Мультивыделение", "Ctrl + клик", "Добавить в выделение"),
                ("Зум", "Ctrl + колесо", "Приблизить / отдалить"),
                ("Панорама", "Средняя кнопка / колесо", "Прокрутить холст"),
            ]),
            ("Стили и слои", [
                ("Слои", "кнопки в панели", "Вперёд / Назад / На передний / На задний"),
                ("Отразить гориз.", "кнопка", "Отразить по горизонтали"),
                ("Отразить верт.", "кнопка", "Отразить по вертикали"),
                ("Повернуть", "кнопка", "Повернуть на заданный угол"),
            ]),
            ("Полезно", [
                ("Drag & Drop", "перетащить файл", "Добавить изображение"),
                ("Скриншот", "Win + Shift + S → Ctrl+V", "Вставить скриншот"),
                ("Свои шрифты", "папка font/", "Кладите .ttf/.otf"),
                ("Clipart.Free", "вкладка Хранилище", "Поиск клипартов"),
            ]),
        ]

        for section_title, rows in sections:
            head = QLabel(section_title)
            head.setStyleSheet(
                "color:#5a9cff;font-size:13px;font-weight:bold;"
                "padding:10px 0 4px 0;")
            gv.addWidget(head)

            for label, keys, desc in rows:
                row = QFrame()
                row.setStyleSheet(
                    "QFrame{background:#262626;border-radius:4px;}")
                rl = QHBoxLayout(row)
                rl.setContentsMargins(10, 6, 10, 6)
                rl.setSpacing(10)

                lbl_name = QLabel(label)
                lbl_name.setStyleSheet("color:#eee;font-size:12px;")
                lbl_name.setFixedWidth(180)

                lbl_keys = QLabel(keys)
                lbl_keys.setStyleSheet(
                    "color:#5a9cff;font-family:Consolas,monospace;"
                    "font-size:12px;font-weight:bold;")
                lbl_keys.setFixedWidth(180)

                lbl_desc = QLabel(desc)
                lbl_desc.setStyleSheet("color:#999;font-size:11px;")
                lbl_desc.setWordWrap(True)

                rl.addWidget(lbl_name)
                rl.addWidget(lbl_keys)
                rl.addWidget(lbl_desc, 1)
                gv.addWidget(row)

        gv.addStretch()
        scroll.setWidget(inner)
        v.addWidget(scroll, 1)

        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet(
            "background:#5a9cff;color:#fff;padding:8px 24px;"
            "border-radius:6px;font-weight:bold;font-size:13px;")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        v.addLayout(btn_row)


# ============================================================
#            СОБЫТИЯ ДЛЯ ФОНОВОЙ ЗАГРУЗКИ
# ============================================================
class _ThumbnailEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, pix):
        super().__init__(_ThumbnailEvent.EVENT_TYPE)
        self.pix = pix


class _SearchResultEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, items, error=None, page=1):
        super().__init__(_SearchResultEvent.EVENT_TYPE)
        self.items = items
        self.error = error
        self.page = page


class _DownloadedEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, data, title):
        super().__init__(_DownloadedEvent.EVENT_TYPE)
        self.data = data
        self.title = title


class _ThumbButton(QPushButton):
    thumb_loaded = pyqtSignal(QPixmap)

    def event(self, ev):
        if ev.type() == _ThumbnailEvent.EVENT_TYPE:
            self.thumb_loaded.emit(ev.pix)
            return True
        return super().event(ev)


# ============================================================
#            КЛИПАРТ-ПОИСК (Clipart.Free API)
# ============================================================
class ClipartSearchWidget(QWidget):
    add_to_canvas = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#1e1e1e;")
        self.current_page = 1
        self.current_query = ""
        self.current_category = ""
        self.last_results = []

        v = QVBoxLayout(self)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(8)

        title = QLabel("Поиск клипартов (Clipart.Free)")
        title.setStyleSheet("color:#eee;font-size:15px;font-weight:bold;")
        v.addWidget(title)

        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Например: cat silhouette")
        self.search_input.setStyleSheet(
            "background:#3a3a3a;color:#eee;padding:6px;"
            "border:1px solid #4a4a4a;border-radius:4px;")
        self.search_input.returnPressed.connect(self.do_search)
        search_btn = QPushButton("Найти")
        search_btn.setStyleSheet(
            "background:#5a9cff;color:#fff;padding:6px 14px;"
            "border-radius:4px;font-weight:bold;")
        search_btn.clicked.connect(self.do_search)
        search_row.addWidget(self.search_input, 1)
        search_row.addWidget(search_btn)
        v.addLayout(search_row)

        cat_row = QHBoxLayout()
        cat_lbl = QLabel("Категория:")
        cat_lbl.setStyleSheet("color:#aaa;font-size:11px;")
        self.category_combo = QComboBox()
        self.category_combo.addItem("Все", "")
        for cat in ["animals", "nature", "people", "food", "transport",
                    "sports", "education", "business", "holidays"]:
            self.category_combo.addItem(cat, cat)
        self.category_combo.setStyleSheet(
            "background:#3a3a3a;color:#eee;padding:4px;border-radius:4px;")
        cat_row.addWidget(cat_lbl)
        cat_row.addWidget(self.category_combo, 1)
        v.addLayout(cat_row)

        self.status_label = QLabel("Введите запрос и нажмите «Найти»")
        self.status_label.setStyleSheet("color:#888;font-size:11px;")
        v.addWidget(self.status_label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background:#1e1e1e;border:none;")
        self.scroll_inner = QWidget()
        self.scroll_inner.setStyleSheet("background:#1e1e1e;")
        self.grid = QGridLayout(self.scroll_inner)
        self.grid.setSpacing(6)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll.setWidget(self.scroll_inner)
        v.addWidget(self.scroll, 1)

        page_row = QHBoxLayout()
        self.prev_btn = QPushButton("<- Назад")
        self.next_btn = QPushButton("Вперёд ->")
        for b in (self.prev_btn, self.next_btn):
            b.setStyleSheet(
                "background:#353535;color:#e6e6e6;padding:6px;"
                "border:1px solid #3f3f3f;border-radius:4px;")
            b.setCursor(Qt.PointingHandCursor)
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)
        self.page_label = QLabel("Страница 1")
        self.page_label.setStyleSheet("color:#aaa;")
        self.page_label.setAlignment(Qt.AlignCenter)
        page_row.addWidget(self.prev_btn)
        page_row.addWidget(self.page_label, 1)
        page_row.addWidget(self.next_btn)
        v.addLayout(page_row)

        self.update_pagination_buttons()

    def do_search(self):
        q = self.search_input.text().strip()
        if not q:
            return
        self.current_query = q
        self.current_category = self.category_combo.currentData() or ""
        self.current_page = 1
        self.fetch_results()

    def fetch_results(self):
        self.status_label.setText(
            f"Загрузка... стр. {self.current_page}, «{self.current_query}»")
        self.status_label.setStyleSheet("color:#5a9cff;font-size:11px;")

        while self.grid.count():
            w = self.grid.takeAt(0).widget()
            if w:
                w.deleteLater()

        q = self.current_query
        cat = self.current_category
        page = self.current_page

        def worker():
            items = []
            error = None
            try:
                params = [
                    f"q={quote(q)}",
                    f"page={page}",
                    f"key={CLIPART_API_KEY}",
                    "order=popularity",
                ]
                if cat:
                    params.append(f"category={quote(cat)}")
                url = CLIPART_BASE + "?" + "&".join(params)

                req = Request(url, headers={
                    "User-Agent": CLIPART_USER_AGENT,
                    "Accept": "application/json",
                })
                with urlopen(req, timeout=20, context=SSL_CTX) as resp:
                    raw = resp.read().decode("utf-8", errors="replace")
                data = json.loads(raw)
                items = data.get("results", []) or []
            except Exception as e:
                error = str(e)

            QApplication.instance().postEvent(
                self, _SearchResultEvent(items, error, page))

        threading.Thread(target=worker, daemon=True).start()

    def event(self, ev):
        if ev.type() == _SearchResultEvent.EVENT_TYPE:
            if ev.error:
                self.status_label.setText(f"Ошибка: {ev.error[:80]}")
                self.status_label.setStyleSheet("color:#eb5757;font-size:11px;")
            else:
                self.last_results = ev.items
                self._render_results(ev.items)
                self.status_label.setText(
                    f"Найдено: {len(ev.items)} (стр. {ev.page})")
                self.status_label.setStyleSheet("color:#6fcf97;font-size:11px;")
            self.update_pagination_buttons()
            return True

        if ev.type() == _DownloadedEvent.EVENT_TYPE:
            import tempfile
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tmp.write(ev.data)
            tmp.close()
            self.add_to_canvas.emit(tmp.name, ev.title)
            return True

        return super().event(ev)

    def _render_results(self, items):
        cols = 4
        for i, item in enumerate(items):
            tile = self._make_tile(item)
            if tile:
                self.grid.addWidget(tile, i // cols, i % cols)

    def _pick_thumb_url(self, item):
        pngs = item.get("png_urls") or {}
        for size in ("400", "300", "200", "800"):
            if size in pngs:
                return pngs[size]
        if pngs:
            try:
                key = min(pngs.keys(), key=lambda k: int(k))
                return pngs[key]
            except Exception:
                pass
        return item.get("thumbnail") or item.get("thumb") or None

    def _pick_full_url(self, item):
        pngs = item.get("png_urls") or {}
        for size in ("1600", "1200", "800", "400"):
            if size in pngs:
                return pngs[size]
        if pngs:
            try:
                key = max(pngs.keys(), key=lambda k: int(k))
                return pngs[key]
            except Exception:
                pass
        return item.get("png_url") or item.get("preview_url") or None

    def _make_tile(self, item):
        title = (item.get("title") or item.get("name") or "Clipart").strip()
        thumb_url = self._pick_thumb_url(item)
        full_url = self._pick_full_url(item)

        btn = _ThumbButton()
        btn.setFixedSize(110, 110)
        btn.setStyleSheet(
            "QPushButton{background:#2b2b2b;border:1px solid #3a3a3a;"
            "border-radius:6px;color:#888;font-size:10px;}"
            "QPushButton:hover{border:1px solid #5a9cff;}")
        btn.setText("...")
        btn.setToolTip(f"{title}\n{full_url or ''}")
        btn.thumb_loaded.connect(self._apply_thumb)

        if thumb_url:
            self._load_thumbnail_async(btn, thumb_url)

        if full_url:
            btn.clicked.connect(
                lambda _, u=full_url, t=title: self._download_full(u, t))
        return btn

    def _apply_thumb(self, pix):
        btn = self.sender()
        if btn is None or pix.isNull():
            return
        btn.setIcon(QIcon(pix))
        btn.setIconSize(QSize(100, 100))
        btn.setText("")

    def _load_thumbnail_async(self, btn, url):
        def worker():
            try:
                req = Request(url, headers={"User-Agent": CLIPART_USER_AGENT})
                with urlopen(req, timeout=15, context=SSL_CTX) as resp:
                    data = resp.read()
                pix = QPixmap()
                pix.loadFromData(data)
                if not pix.isNull():
                    pix = pix.scaled(100, 100, Qt.KeepAspectRatio,
                                     Qt.SmoothTransformation)
                    QApplication.instance().postEvent(btn, _ThumbnailEvent(pix))
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def _download_full(self, url, title):
        self.status_label.setText(f"Скачивание: {title[:40]}...")
        self.status_label.setStyleSheet("color:#5a9cff;font-size:11px;")

        def worker():
            try:
                req = Request(url, headers={"User-Agent": CLIPART_USER_AGENT})
                with urlopen(req, timeout=30, context=SSL_CTX) as resp:
                    data = resp.read()
                QApplication.instance().postEvent(
                    self, _DownloadedEvent(data, title))
            except Exception as e:
                print("Clipart download error:", e)

        threading.Thread(target=worker, daemon=True).start()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.fetch_results()

    def next_page(self):
        self.current_page += 1
        self.fetch_results()

    def update_pagination_buttons(self):
        self.prev_btn.setEnabled(self.current_page > 1)
        self.page_label.setText(f"Страница {self.current_page}")


# ============================================================
#                     ХРАНИЛИЩЕ + ПОИСК
# ============================================================
class StorageWidget(QWidget):
    add_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#232323;")
        h = QHBoxLayout(self)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        left = QWidget()
        left.setStyleSheet("background:#232323;")
        lv = QVBoxLayout(left)
        lv.setContentsMargins(10, 10, 10, 10)

        top = QHBoxLayout()
        title = QLabel("Хранилище")
        title.setStyleSheet("color:#eee;font-size:16px;font-weight:bold;")
        top.addWidget(title)
        top.addStretch()
        btn_new_folder = QPushButton("+ Папка")
        btn_new_folder.setStyleSheet(
            "background:#3a3a3a;color:#eee;padding:6px 12px;border-radius:4px;")
        btn_new_folder.clicked.connect(self.create_folder)
        top.addWidget(btn_new_folder)
        btn_refresh = QPushButton("Обновить")
        btn_refresh.setStyleSheet(
            "background:#3a3a3a;color:#eee;padding:6px 12px;border-radius:4px;")
        btn_refresh.clicked.connect(self.refresh)
        top.addWidget(btn_refresh)
        lv.addLayout(top)

        nav = QHBoxLayout()
        self.up_btn = QPushButton("^ Вверх")
        self.up_btn.setStyleSheet(
            "background:#353535;color:#e6e6e6;padding:4px 10px;"
            "border:1px solid #3f3f3f;border-radius:4px;")
        self.up_btn.clicked.connect(self.go_up)
        self.up_btn.setEnabled(False)
        nav.addWidget(self.up_btn)
        self.breadcrumb = QLabel("save")
        self.breadcrumb.setStyleSheet("color:#5a9cff;font-size:12px;")
        nav.addWidget(self.breadcrumb, 1)
        lv.addLayout(nav)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background:#1e1e1e;border:none;")
        self.inner = QWidget()
        self.inner.setStyleSheet("background:#1e1e1e;")
        self.grid = QGridLayout(self.inner)
        self.grid.setSpacing(10)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll.setWidget(self.inner)
        lv.addWidget(self.scroll)

        self.clipart_search = ClipartSearchWidget()
        self.clipart_search.add_to_canvas.connect(self._on_clipart_ready)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color:#3a3a3a;")

        h.addWidget(left, 1)
        h.addWidget(sep)
        h.addWidget(self.clipart_search, 1)

        self.current_subpath = ""
        self.refresh()

    def current_dir(self):
        return (os.path.join(SAVE_DIR, self.current_subpath)
                if self.current_subpath else SAVE_DIR)

    def create_folder(self):
        name, ok = QInputDialog.getText(self, "Новая папка", "Имя папки:")
        if not ok or not name.strip():
            return
        name = name.strip()
        for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            name = name.replace(ch, '_')
        new_path = os.path.join(self.current_dir(), name)
        try:
            os.makedirs(new_path, exist_ok=True)
            self.refresh()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось создать папку: {e}")

    def go_up(self):
        if not self.current_subpath:
            return
        parts = self.current_subpath.split(os.sep)
        self.current_subpath = os.sep.join(parts[:-1]) if len(parts) > 1 else ""
        self.refresh()

    def refresh(self):
        self.breadcrumb.setText("save" + (os.sep + self.current_subpath
                                          if self.current_subpath else ""))
        self.up_btn.setEnabled(bool(self.current_subpath))
        while self.grid.count():
            w = self.grid.takeAt(0).widget()
            if w:
                w.deleteLater()
        cur = self.current_dir()
        if not os.path.exists(cur):
            return
        entries = sorted(os.listdir(cur))
        folders = [e for e in entries if os.path.isdir(os.path.join(cur, e))]
        files = [e for e in entries if e.lower().endswith(IMAGE_EXTS)]
        tiles = []
        for name in folders:
            tiles.append(self._make_folder_tile(name))
        for name in files:
            tiles.append(self._make_tile(os.path.join(cur, name)))
        cols = 2
        for i, tile in enumerate(tiles):
            self.grid.addWidget(tile, i // cols, i % cols)

    def _make_folder_tile(self, name):
        btn = QPushButton()
        btn.setFixedSize(150, 170)
        btn.setStyleSheet(
            "QPushButton{background:#2b2b2b;border:1px solid #3a3a3a;"
            "border-radius:6px;color:#ccc;}"
            "QPushButton:hover{border:1px solid #f2c94c;}")
        pix = QPixmap(80, 80)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor("#f2c94c"), 3))
        p.setBrush(QColor("#f2c94c"))
        p.drawRect(10, 30, 60, 40)
        p.drawLine(10, 30, 25, 30)
        p.drawLine(25, 30, 32, 22)
        p.drawLine(32, 22, 70, 22)
        p.drawLine(70, 22, 70, 30)
        p.end()
        btn.setIcon(QIcon(pix))
        btn.setIconSize(QSize(80, 80))
        btn.setText(name[:18])
        btn.clicked.connect(lambda _, n=name: self.open_folder(n))
        btn.setContextMenuPolicy(Qt.CustomContextMenu)
        btn.customContextMenuRequested.connect(
            lambda pos, b=btn, n=name: self._folder_menu(b, pos, n))
        return btn

    def open_folder(self, name):
        self.current_subpath = (os.path.join(self.current_subpath, name)
                                if self.current_subpath else name)
        self.refresh()

    def _folder_menu(self, btn, pos, name):
        menu = QMenu(self)
        act_open = menu.addAction("Открыть")
        act_delete = menu.addAction("Удалить папку")
        action = menu.exec_(btn.mapToGlobal(pos))
        if action == act_open:
            self.open_folder(name)
        elif action == act_delete:
            self._delete_folder(name)

    def _delete_folder(self, name):
        path = os.path.join(self.current_dir(), name)
        reply = QMessageBox.question(
            self, "Удалить папку",
            f"Удалить папку «{name}» со всем содержимым?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                shutil.rmtree(path)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def _make_tile(self, path):
        btn = QPushButton()
        btn.setFixedSize(150, 170)
        btn.setStyleSheet(
            "QPushButton{background:#2b2b2b;border:1px solid #3a3a3a;"
            "border-radius:6px;color:#ccc;}"
            "QPushButton:hover{border:1px solid #5a9cff;}")
        btn.setToolTip(os.path.basename(path))
        pix = QPixmap(path).scaled(140, 130, Qt.KeepAspectRatio,
                                   Qt.SmoothTransformation)
        btn.setIcon(QIcon(pix))
        btn.setIconSize(QSize(140, 130))
        btn.setText(os.path.basename(path)[:18])
        btn.clicked.connect(lambda _, p=path: self.add_requested.emit(p))
        btn.setContextMenuPolicy(Qt.CustomContextMenu)
        btn.customContextMenuRequested.connect(
            lambda pos, b=btn, p=path: self._file_menu(b, pos, p))
        return btn

    def _file_menu(self, btn, pos, path):
        menu = QMenu(self)
        act_delete = menu.addAction("Удалить файл")
        action = menu.exec_(btn.mapToGlobal(pos))
        if action == act_delete:
            try:
                os.remove(path)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def _on_clipart_ready(self, tmp_path, title):
        try:
            safe = "".join(c for c in title if c.isalnum() or c in " -_")[:40].strip()
            if not safe:
                safe = "clipart"
            fname = f"{safe}_{int(time.time())}.png"
            dst = os.path.join(SAVE_DIR, fname)
            shutil.move(tmp_path, dst)
            self.add_requested.emit(dst)
            self.refresh()
            self.clipart_search.status_label.setText(f"Добавлено: {fname}")
            self.clipart_search.status_label.setStyleSheet(
                "color:#6fcf97;font-size:11px;")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))


# ============================================================
#                     ГЛАВНОЕ ОКНО
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Canva — редактор изображений")
        self.resize(1500, 850)
        self.setStyleSheet(self._style())

        icon_file = ICON_ICO_PATH if os.path.exists(ICON_ICO_PATH) else ICON_PATH
        if os.path.exists(icon_file):
            self.setWindowIcon(QIcon(icon_file))

        self.fonts = self._load_fonts()
        self.canvas = Canvas()
        self.canvas.item_selected.connect(self.on_item_selected)
        self.canvas.request_edit_text.connect(self._on_request_edit)

        self._build_toolbar()

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #232323; }
            QTabBar::tab { background: #2b2b2b; color: #ccc; padding: 8px 16px; }
            QTabBar::tab:selected { background: #3a3a3a; color: #fff; }
        """)

        editor = QWidget()
        editor.setStyleSheet("background:#232323;")
        h = QHBoxLayout(editor)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        left_col = QWidget()
        left_col.setFixedWidth(220)
        left_col.setStyleSheet("background:#2b2b2b;")
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(10, 14, 10, 10)
        left_layout.setSpacing(8)

        lbl_props = QLabel("Свойства объекта")
        lbl_props.setStyleSheet(
            "color:#eee;font-size:14px;font-weight:bold;padding-bottom:6px;")
        left_layout.addWidget(lbl_props)

        self.settings_btn = QPushButton("  Настройки изображения")
        self.settings_btn.setIcon(make_icon("image"))
        self.settings_btn.setIconSize(QSize(22, 22))
        self.settings_btn.setStyleSheet(self._btn_style())
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self.open_image_settings)
        self.settings_btn.setVisible(False)
        left_layout.addWidget(self.settings_btn)

        self.edit_text_btn = QPushButton("  Настройки текста (F2)")
        self.edit_text_btn.setIcon(make_icon("text"))
        self.edit_text_btn.setIconSize(QSize(22, 22))
        self.edit_text_btn.setStyleSheet(self._btn_style())
        self.edit_text_btn.setCursor(Qt.PointingHandCursor)
        self.edit_text_btn.clicked.connect(self.open_text_edit)
        self.edit_text_btn.setVisible(False)
        left_layout.addWidget(self.edit_text_btn)

        self.props_label = QLabel("Объект не выбран")
        self.props_label.setStyleSheet("color:#999;font-size:11px;")
        self.props_label.setWordWrap(True)
        left_layout.addWidget(self.props_label)

        left_layout.addStretch()

        info_row = QHBoxLayout()
        info_row.setContentsMargins(0, 0, 0, 0)
        self.info_btn = QPushButton()
        self.info_btn.setIcon(make_info_icon(40))
        self.info_btn.setIconSize(QSize(40, 40))
        self.info_btn.setFixedSize(46, 46)
        self.info_btn.setStyleSheet(
            "QPushButton{background:transparent;border:none;}"
            "QPushButton:hover{background:#353535;border-radius:23px;}")
        self.info_btn.setCursor(Qt.PointingHandCursor)
        self.info_btn.setToolTip("Горячие клавиши и справка")
        self.info_btn.clicked.connect(self.show_help)

        self.info_label = QLabel("Справка")
        self.info_label.setStyleSheet("color:#888;font-size:11px;")
        self.info_label.setCursor(Qt.PointingHandCursor)
        self.info_label.mousePressEvent = lambda ev: self.show_help()

        info_row.addWidget(self.info_btn)
        info_row.addWidget(self.info_label, 1)
        left_layout.addLayout(info_row)

        h.addWidget(left_col)

        canvas_wrap = QWidget()
        canvas_wrap.setStyleSheet("background:#1e1e1e;")
        cw = QVBoxLayout(canvas_wrap)
        cw.setContentsMargins(0, 0, 0, 0)
        cw.addWidget(self.canvas)
        h.addWidget(canvas_wrap, 1)

        self.storage = StorageWidget()
        self.storage.add_requested.connect(self.add_image_from_storage)

        self.tabs.addTab(editor, make_icon("image"), "Редактор")
        self.tabs.addTab(self.storage, make_icon("store"), "Хранилище")

        self.setCentralWidget(self.tabs)

        self.status = self.statusBar()
        self.status.setStyleSheet("background:#2b2b2b;color:#aaa;")

        _DEFAULT_HINT = (
            "Двойной клик по тексту — редактировать  •  Кисть/Ластик — рисование  •  "
            "Ctrl+Z — отменить  •  Ctrl+колесо — зум")

        if _CREATED_DIRS:
            rel = ", ".join(os.path.relpath(d, BASE_DIR) for d in _CREATED_DIRS)
            self.status.showMessage(f"Созданы папки: {rel}")
            QTimer.singleShot(3000,
                              lambda: self.status.showMessage(_DEFAULT_HINT))
        else:
            self.status.showMessage(_DEFAULT_HINT)

    def open_text_edit(self):
        sel = self.canvas.selected_items
        if len(sel) != 1 or sel[0].kind != "text":
            return
        item = sel[0]
        dlg = TextEditDialog(self, item=item)
        if dlg.exec_() == QDialog.Accepted:
            vals = dlg.values()
            if not vals["text"].strip():
                return
            self.canvas.push_history()
            item.apply_edit(
                text=vals["text"],
                font_family=vals["font_family"],
                font_size=vals["font_size"],
                color=vals["color"],
                bold=vals["bold"],
                italic=vals["italic"],
            )
            self.canvas.select_single(item)
            self.status.showMessage("Текст обновлён")

    def _on_request_edit(self, payload):
        if isinstance(payload, tuple) and payload and payload[0] == "image_settings":
            item = payload[1]
            dlg = ImageSettingsDialog(item, self)
            if dlg.exec_() == QDialog.Accepted:
                dlg.apply()
                self.canvas.update()
                self.canvas.document_changed.emit()
            return
        item = payload
        dlg = TextEditDialog(self, item=item)
        if dlg.exec_() == QDialog.Accepted:
            vals = dlg.values()
            if not vals["text"].strip():
                return
            self.canvas.push_history()
            item.apply_edit(
                text=vals["text"],
                font_family=vals["font_family"],
                font_size=vals["font_size"],
                color=vals["color"],
                bold=vals["bold"],
                italic=vals["italic"],
            )
            self.canvas.select_single(item)
            self.status.showMessage("Текст обновлён")

    def show_help(self):
        dlg = HelpDialog(self)
        dlg.exec_()

    # ---------- BRUSH / ERASER: клик открывает настройки ----------
    def on_brush_action(self):
        """Клик по кнопке Кисть: открываем диалог, потом активируем."""
        was_active = self.canvas.tool == "brush"
        dlg = BrushSettingsDialog(self,
                                  color=self.canvas.brush_color,
                                  width=self.canvas.brush_width,
                                  apply_mode=True)
        if dlg.exec_() != QDialog.Accepted:
            # отмена: возвращаем состояние кнопки
            self.act_brush.setChecked(was_active)
            if was_active:
                self.activate_brush()
            else:
                self.deactivate_tools()
            return
        color, width = dlg.values()
        self.canvas.set_brush_color(color)
        self.canvas.set_brush_width(width)
        self.act_eraser.setChecked(False)
        self.act_brush.setChecked(True)
        self.activate_brush()

    def on_eraser_action(self):
        """Клик по кнопке Ластик: открываем диалог, потом активируем."""
        was_active = self.canvas.tool == "eraser"
        dlg = EraserSettingsDialog(self,
                                   width=self.canvas.eraser_width,
                                   apply_mode=True)
        if dlg.exec_() != QDialog.Accepted:
            self.act_eraser.setChecked(was_active)
            if was_active:
                self.activate_eraser()
            else:
                self.deactivate_tools()
            return
        w = dlg.value()
        self.canvas.set_eraser_width(w)
        self.act_brush.setChecked(False)
        self.act_eraser.setChecked(True)
        self.activate_eraser()

    def activate_brush(self):
        self.canvas.set_tool("brush")
        self.status.showMessage(
            f"Кисть активна • цвет: {self.canvas.brush_color.name()} • "
            f"толщина: {self.canvas.brush_width} px")

    def activate_eraser(self):
        self.canvas.set_tool("eraser")
        self.status.showMessage(
            f"Ластик активен • толщина: {self.canvas.eraser_width} px")

    def deactivate_tools(self):
        self.canvas.set_tool("select")
        self.status.showMessage("Режим выделения")

    def _build_toolbar(self):
        tb = QToolBar("Инструменты")
        tb.setMovable(False)
        tb.setIconSize(QSize(22, 22))
        tb.setStyleSheet("""
            QToolBar {
                background: #2b2b2b;
                border-bottom: 1px solid #3a3a3a;
                padding: 6px;
                spacing: 4px;
            }
            QToolButton {
                background: #353535;
                color: #e6e6e6;
                border: 1px solid #3f3f3f;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                margin: 0 2px;
            }
            QToolButton:hover { background: #404040; border: 1px solid #5a9cff; }
            QToolButton:pressed { background: #2c2c2c; }
            QToolButton:checked { background: #5a9cff; color: #fff;
                                  border: 1px solid #5a9cff; }
        """)
        self.addToolBar(tb)
        self.toolbar = tb

        def add_action(text, icon_name, slot, tooltip=None):
            act = QAction(make_icon(icon_name), f"  {text}", self)
            act.triggered.connect(slot)
            if tooltip:
                act.setToolTip(tooltip)
            tb.addAction(act)
            return act

        add_action("Новый макет", "new", self.new_doc)
        add_action("Изображение", "image", self.open_image)
        add_action("Сохранить", "save", self.save_canvas)
        add_action("Копировать", "copy", self.copy_canvas_to_clipboard,
                   "Скопировать всё содержимое холста в буфер обмена")
        add_action("Текст", "text", self.add_text)
        add_action("Цвет фона", "color", self.choose_bg_color)
        add_action("Прозрачный фон", "color_off", self.reset_bg_color)

        tb.addSeparator()

        add_action("Вперёд", "front", self.canvas.bring_forward)
        add_action("Назад", "back", self.canvas.send_backward)
        add_action("На передний", "front", self.canvas.bring_to_front)
        add_action("На задний", "back", self.canvas.send_to_back)

        tb.addSeparator()

        add_action("Отразить гориз.", "flip_h", self.canvas.flip_selected_horizontal)
        add_action("Отразить верт.", "flip_v", self.canvas.flip_selected_vertical)
        add_action("Повернуть", "rotate", self.rotate_selected)

        tb.addSeparator()

        # ---- Кисть ----
        self.act_brush = QAction(make_icon("brush"), "  Кисть", self)
        self.act_brush.setCheckable(True)
        self.act_brush.setToolTip("Кисть (откроется диалог настроек)")
        self.act_brush.triggered.connect(self.on_brush_action)
        tb.addAction(self.act_brush)

        # ---- Ластик ----
        self.act_eraser = QAction(make_icon("eraser"), "  Ластик", self)
        self.act_eraser.setCheckable(True)
        self.act_eraser.setToolTip("Ластик (откроется диалог настроек)")
        self.act_eraser.triggered.connect(self.on_eraser_action)
        tb.addAction(self.act_eraser)

    def copy_canvas_to_clipboard(self):
        """Копирует всё содержимое холста в системный буфер обмена."""
        try:
            img = self.canvas.render_to_image()
            QApplication.clipboard().setImage(img)
            self.status.showMessage(
                f"Скопировано в буфер обмена ({img.width()}×{img.height()})")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось скопировать: {e}")

    def choose_bg_color(self):
        current = self.canvas.bg_color
        if current == Qt.transparent:
            current = QColor(255, 255, 255)
        c = QColorDialog.getColor(current, self,
                                  "Выберите цвет фона макета",
                                  QColorDialog.ShowAlphaChannel)
        if c.isValid():
            self.canvas.set_bg_color(c)
            self.status.showMessage(
                f"Фон макета: {c.name()} (alpha={c.alpha()})")

    def reset_bg_color(self):
        self.canvas.reset_bg_color()
        self.status.showMessage("Фон макета сброшен на прозрачный")

    def rotate_selected(self):
        if not self.canvas.selected_items:
            self.status.showMessage("Сначала выделите объект")
            return
        dlg = RotateDialog(self, initial=45.0)
        if dlg.exec_() == QDialog.Accepted:
            angle = dlg.value()
            self.canvas.rotate_selected(angle)
            self.status.showMessage(f"Поворот на {angle}°")

    def _style(self):
        return """
            QMainWindow { background: #232323; }
            QToolTip { background:#3a3a3a; color:#eee; border:1px solid #555; }
            QStatusBar { background:#2b2b2b; color:#aaa; }
        """

    def _btn_style(self):
        return """
            QPushButton {
                background: #353535; color: #e6e6e6;
                border: 1px solid #3f3f3f; border-radius: 6px;
                padding: 8px 10px; text-align: left; font-size: 12px;
            }
            QPushButton:hover { background: #404040; border: 1px solid #5a9cff; }
            QPushButton:pressed { background: #2c2c2c; }
        """

    def _load_fonts(self):
        families = set()
        for f in QFontDatabase().families():
            families.add(f)
        for f in os.listdir(FONT_DIR):
            if f.lower().endswith(('.ttf', '.otf')):
                fid = QFontDatabase.addApplicationFont(os.path.join(FONT_DIR, f))
                if fid != -1:
                    for fam in QFontDatabase.applicationFontFamilies(fid):
                        families.add(fam)
        priority = ["Arial", "Times New Roman", "Courier New", "Verdana",
                    "Georgia", "Tahoma", "Comic Sans MS", "Impact",
                    "Trebuchet MS", "Segoe UI", "DejaVu Sans", "Liberation Sans"]
        result = [p for p in priority if p in families]
        for f in sorted(families):
            if f not in result:
                result.append(f)
        return result[:40]

    def new_doc(self):
        dlg = NewDocDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            w, h = dlg.values()
            self.canvas.new_document(w, h)
            self.status.showMessage(f"Создан макет {w}x{h}")

    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть изображение", "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif *.webp)")
        if path:
            self.canvas.add_image(path)
            self.storage.refresh()
            self.status.showMessage(f"Добавлено: {os.path.basename(path)}")

    def add_image_from_storage(self, path):
        self.canvas.add_image(path)
        self.status.showMessage(f"Из хранилища: {os.path.basename(path)}")

    def add_text(self):
        dlg = TextEditDialog(self, item=None)
        if dlg.exec_() == QDialog.Accepted:
            vals = dlg.values()
            if not vals["text"].strip():
                return
            self.canvas.add_text(
                vals["text"], vals["font_family"],
                vals["font_size"], vals["color"])
            if self.canvas.selected_items:
                item = self.canvas.selected_items[0]
                if item.kind == "text":
                    item.bold = vals["bold"]
                    item.italic = vals["italic"]
                    item._recalc_base()
                    item.display_size = QSize(item.base_w, item.base_h)
                    self.canvas.update()
            self.status.showMessage("Текст добавлен")

    def save_canvas(self):
        if self.canvas.doc_size.width() == 0:
            return
        self.canvas.commit_inline_edit()
        default = os.path.join(DONE_DIR, f"canvas_{int(time.time())}.png")
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить в done", default, "PNG (*.png);;JPEG (*.jpg)")
        if not path:
            return
        out = self.canvas.render_to_image()
        out.save(path)
        self.status.showMessage(f"Сохранено в done: {path}")

    def open_image_settings(self):
        sel = self.canvas.selected_items
        if len(sel) != 1 or sel[0].kind != "image":
            return
        item = sel[0]
        dlg = ImageSettingsDialog(item, self)
        if dlg.exec_() == QDialog.Accepted:
            dlg.apply()
            self.canvas.update()
            self.canvas.document_changed.emit()

    def on_item_selected(self, item):
        if item is None:
            self.props_label.setText("Объект не выбран")
            self.settings_btn.setVisible(False)
            self.edit_text_btn.setVisible(False)
            return
        if len(self.canvas.selected_items) > 1:
            self.props_label.setText(
                f"Выбрано объектов: {len(self.canvas.selected_items)}")
            self.settings_btn.setVisible(False)
            self.edit_text_btn.setVisible(False)
            return
        if item.kind == "image":
            self.settings_btn.setVisible(True)
            self.edit_text_btn.setVisible(False)
            self.props_label.setText(
                f"Изображение\n"
                f"Source: {item.source_size.width()}x{item.source_size.height()}\n"
                f"Display: {item.display_size.width()}x{item.display_size.height()}\n"
                f"Scale: {item.scale:.2f}\n"
                f"Rotation: {item.rotation:.1f}°\n"
                f"Opacity: {int(item.opacity * 100)}%\n"
                f"Двойной клик или F2 — настройки")
        else:
            self.settings_btn.setVisible(False)
            self.edit_text_btn.setVisible(True)
            self.props_label.setText(
                f"Текст: {item.text}\n"
                f"Шрифт: {item.font_family}\n"
                f"Размер: {item.font_size}pt\n"
                f"Rotation: {item.rotation:.1f}°\n"
                f"Двойной клик — править на холсте\n"
                f"F2 — расширенные настройки")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    icon_file = ICON_ICO_PATH if os.path.exists(ICON_ICO_PATH) else ICON_PATH
    if os.path.exists(icon_file):
        app.setWindowIcon(QIcon(icon_file))
        if sys.platform == "win32":
            import ctypes
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    "MiniCanva.Editor.App.1")
            except Exception:
                pass

    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(35, 35, 35))
    pal.setColor(QPalette.WindowText, QColor(230, 230, 230))
    pal.setColor(QPalette.Base, QColor(30, 30, 30))
    pal.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    pal.setColor(QPalette.Text, QColor(230, 230, 230))
    pal.setColor(QPalette.Button, QColor(53, 53, 53))
    pal.setColor(QPalette.ButtonText, QColor(230, 230, 230))
    pal.setColor(QPalette.Highlight, QColor(80, 160, 255))
    pal.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(pal)

    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
