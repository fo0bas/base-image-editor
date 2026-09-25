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
    QToolBar, QAction
)
from PyQt5.QtGui import (
    QPixmap, QImage, QPainter, QColor, QPen, QBrush, QFont,
    QIcon, QTransform, QFontDatabase, QFontMetrics, QPalette
)
from PyQt5.QtCore import (
    Qt, QPoint, QRect, QSize, pyqtSignal, QEvent, QTimer
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
    """Проверяет наличие рабочих папок и создаёт отсутствующие.
    Возвращает список путей, которые были созданы в этот раз."""
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
        f = QFont(font_family, font_size)
        m = QFontMetrics(f)
        self.base_w = m.horizontalAdvance(text) + 10
        self.base_h = m.height() + 6

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
        f = QFont(self.font_family, size)
        f.setBold(self.bold)
        f.setItalic(self.italic)
        target = self.rect()
        p.save()
        p.setOpacity(self.opacity)
        self._apply_transform(p, target)
        p.setFont(f)
        p.setPen(self.color)
        p.drawText(target, Qt.AlignLeft | Qt.AlignVCenter, self.text)
        p.restore()


# ============================================================
#                     ХОЛСТ
# ============================================================
class Canvas(QWidget):
    item_selected = pyqtSignal(object)
    document_changed = pyqtSignal()

    HANDLE = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAcceptDrops(True)
        self.doc_size = QSize(800, 600)
        self.bg_color = Qt.transparent
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

    def push_history(self):
        self.history.append([it.clone() for it in self.items])
        if len(self.history) > 100:
            self.history.pop(0)

    def undo(self):
        if not self.history:
            return
        self.items = self.history.pop()
        for it in self.items:
            it.selected = False
        self.selected_items = []
        self.item_selected.emit(None)
        self.update()
        self.document_changed.emit()

    def new_document(self, w, h):
        self.doc_size = QSize(w, h)
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
        w = m.horizontalAdvance(text) + 10
        h = m.height() + 6
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
        for it in self.items:
            it.draw(p)
        p.restore()

        p.setPen(QPen(QColor(120, 120, 120), 1))
        p.drawRect(dr)

        for it in self.selected_items:
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
        if event.button() == Qt.MiddleButton:
            self.mode = 'pan'
            self.pan_start = pos
            self.pan_offset_start = QPoint(self.pan_offset)
            return
        if event.button() != Qt.LeftButton:
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

        if self.mode == 'pan':
            self.pan_offset = self.pan_offset_start + (pos - self.pan_start)
            self.update()
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

        if self._handle_at(pos):
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if self.mode in ('move', 'resize'):
            self._check_all_out_of_bounds()
        self.mode = None
        self.resize_handle = None
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
        if key in (Qt.Key_Delete, Qt.Key_Backspace):
            self.delete_selected()
            event.accept()
            return
        if key == Qt.Key_Escape:
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


class TextDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить текст")
        self.setStyleSheet("background:#2b2b2b; color:#eee;")
        form = QFormLayout(self)
        self.text = QLineEdit("Ваш текст")
        self.text.setStyleSheet("background:#3a3a3a;color:#eee;padding:4px;")
        self.font = QFontComboBox()
        self.font.setStyleSheet("background:#3a3a3a;color:#eee;padding:4px;")
        self.size = QSpinBox()
        self.size.setRange(8, 300)
        self.size.setValue(36)
        self.size.setStyleSheet("background:#3a3a3a;color:#eee;padding:4px;")
        self.color = QColor(255, 255, 255)
        self.color_btn = QPushButton("Цвет текста")
        self.color_btn.setStyleSheet(
            "background:#3a3a3a;color:#eee;padding:6px;border-radius:4px;")
        self.color_btn.clicked.connect(self.pick_color)
        form.addRow("Текст:", self.text)
        form.addRow("Шрифт:", self.font)
        form.addRow("Размер:", self.size)
        form.addRow("", self.color_btn)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)

    def pick_color(self):
        c = QColorDialog.getColor(self.color, self, "Цвет текста")
        if c.isValid():
            self.color = c
            self.color_btn.setStyleSheet(
                f"background:{c.name()};color:#000;padding:6px;border-radius:4px;")

    def values(self):
        return (self.text.text(), self.font.currentFont().family(),
                self.size.value(), self.color)


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

        props_panel = QWidget()
        props_panel.setFixedWidth(220)
        props_panel.setStyleSheet("background:#2b2b2b;")
        pv = QVBoxLayout(props_panel)
        pv.setContentsMargins(10, 14, 10, 14)
        pv.setSpacing(8)

        lbl_props = QLabel("Свойства объекта")
        lbl_props.setStyleSheet(
            "color:#eee;font-size:14px;font-weight:bold;padding-bottom:6px;")
        pv.addWidget(lbl_props)

        self.settings_btn = QPushButton("  Настройки изображения")
        self.settings_btn.setIcon(make_icon("image"))
        self.settings_btn.setIconSize(QSize(22, 22))
        self.settings_btn.setStyleSheet(self._btn_style())
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self.open_image_settings)
        self.settings_btn.setVisible(False)
        pv.addWidget(self.settings_btn)

        self.props_label = QLabel("Объект не выбран")
        self.props_label.setStyleSheet("color:#999;font-size:11px;")
        self.props_label.setWordWrap(True)
        pv.addWidget(self.props_label)

        pv.addStretch()
        h.addWidget(props_panel)

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
            "Ctrl+V — вставить  •  Ctrl+C — копировать  •  "
            "Ctrl+A — выделить всё  •  Ctrl+Z — отменить  •  "
            "Del — удалить  •  Ctrl+колесо — зум")

        if _CREATED_DIRS:
            rel = ", ".join(os.path.relpath(d, BASE_DIR) for d in _CREATED_DIRS)
            self.status.showMessage(f"Созданы папки: {rel}")
            QTimer.singleShot(3000,
                              lambda: self.status.showMessage(_DEFAULT_HINT))
        else:
            self.status.showMessage(_DEFAULT_HINT)

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
            QToolButton:disabled { color: #666; }
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
        dlg = TextDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            text, family, size, color = dlg.values()
            if not text.strip():
                return
            self.canvas.add_text(text, family, size, color)
            self.status.showMessage("Текст добавлен")

    def save_canvas(self):
        if self.canvas.doc_size.width() == 0:
            return
        default = os.path.join(DONE_DIR, f"canvas_{int(time.time())}.png")
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить в done", default, "PNG (*.png);;JPEG (*.jpg)")
        if not path:
            return
        out = QImage(self.canvas.doc_size, QImage.Format_ARGB32)
        if self.canvas.bg_color != Qt.transparent and self.canvas.bg_color.alpha() > 0:
            out.fill(self.canvas.bg_color)
        else:
            out.fill(Qt.transparent)
        p = QPainter(out)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)
        for it in self.canvas.items:
            it.draw(p)
        p.end()
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
            return
        if len(self.canvas.selected_items) > 1:
            self.props_label.setText(
                f"Выбрано объектов: {len(self.canvas.selected_items)}")
            self.settings_btn.setVisible(False)
            return
        if item.kind == "image":
            self.settings_btn.setVisible(True)
            self.props_label.setText(
                f"Изображение\n"
                f"Source: {item.source_size.width()}x{item.source_size.height()}\n"
                f"Display: {item.display_size.width()}x{item.display_size.height()}\n"
                f"Scale: {item.scale:.2f}\n"
                f"Rotation: {item.rotation:.1f}°\n"
                f"Flip H: {'да' if item.flip_h else 'нет'}\n"
                f"Flip V: {'да' if item.flip_v else 'нет'}\n"
                f"Opacity: {int(item.opacity * 100)}%"
            )
        else:
            self.settings_btn.setVisible(False)
            self.props_label.setText(
                f"Текст: {item.text}\n"
                f"Шрифт: {item.font_family} {item.font_size}pt\n"
                f"Rotation: {item.rotation:.1f}°")


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