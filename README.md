# 🎨 Mini Canva — Image Editor / Редактор изображений

A lightweight Canva-like image editor built with Python + PyQt5.
Simple, fast, offline-friendly, with built-in Clipart search.

Лёгкий редактор изображений в стиле Canva на Python + PyQt5.
Простой, быстрый, работает офлайн, со встроенным поиском клипартов.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📖 Table of Contents / Содержание

- [✨ Features (English)](#-features-english)
- [⚙️ Installation & Run (English)](#️-installation--run-english)
- [🎯 Features (Русский)](#-features-русский)
- [⚙️ Установка и запуск (Русский)](#️-установка-и-запуск-русский)
- [📂 Project Structure / Структура проекта](#-project-structure--структура-проекта)
- [⌨️ Hotkeys / Горячие клавиши](#️-hotkeys--горячие-клавиши)
- [📝 License / Лицензия](#-license--лицензия)

---

## ✨ Features (English)

### Canvas & Documents
- **Create custom canvas** — any size from 50×50 up to 5000×5000 px, with quick presets (500×500, 1080×1080, 1920×1080, 1080×1920).
- **Transparent canvas by default** — checkerboard pattern shows the transparency.
- **Custom background color** — pick any color with alpha channel (0–100% opacity), or reset back to transparent.

### Objects & Editing
- **Add images** — open via dialog, drag & drop from Explorer, or paste from clipboard (`Ctrl+V` for screenshots).
- **Add text** — choose from system fonts + any `.ttf` / `.otf` fonts placed in the `font/` folder. Russian and Latin scripts supported.
- **Select / move / resize** — click any object to select, drag to move, drag corner handles to resize.
- **Multi-selection** — `Ctrl+Click` to add to selection, `Ctrl+A` to select all.
- **Layers** — bring forward, send backward, bring to front, send to back.
- **Flip & Rotate** — mirror horizontally / vertically, rotate by any angle (with quick presets 15°, 30°, 45°, 90°, 180°, −90°).
- **Opacity & Filters** — brightness, contrast, saturation sliders, and per-object opacity.

### Clipart Search (Clipart.Free API)
- **Built-in search panel** — search millions of CC0 cliparts directly inside the app.
- **Paginated results** — 30 items per page, lazy thumbnail loading, 4 items per row.
- **One-click insert** — click any clipart to download the full-resolution PNG and insert it on the canvas.

### Local Storage
- **Folder-based library** — organize saved images into folders inside `save/`.
- **Create / delete folders** — right-click a folder for the context menu.
- **Preview thumbnails** — grid view of all images with hover highlight.

### Undo / History
- **Unlimited undo** — up to 100 steps (`Ctrl+Z`).
- **Copy / Cut / Paste** — for both canvas objects and system clipboard content.
- **Duplicate** — `Ctrl+D`.

### Export
- **Save to `done/`** — export final composition as PNG or JPEG.
- **Preserves transparency** — if background is transparent, the output PNG is transparent too.

### UX
- **Dark theme** — custom palette, dark panels, blue accents.
- **Custom app icon** — picks up `icon.ico` or `icon.png` from the project root, sets Windows AppUserModelID for a proper taskbar icon.
- **Auto-creates folders** — `font/`, `save/`, `done/` are created automatically on first launch.
- **Keyboard-first workflow** — all common actions have hotkeys.

---

## ⚙️ Installation & Run (English)

### Requirements
- **Python 3.8 – 3.12** recommended (Python 3.13/3.14 may lack prebuilt PyQt5 wheels).
- **Windows 10/11**, macOS, or Linux.
- ~150 MB disk space for dependencies.

### Step 1. Install Python
Download from [python.org](https://www.python.org/downloads/).
During installation, check **"Add Python to PATH"**.

Verify:
```bash
python --version


