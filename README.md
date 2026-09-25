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
Step 2. Clone the repository
bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
Or download the ZIP from GitHub and extract it.

Step 3. Create virtual environment (recommended)
bash
python -m venv .venv
Activate it:

Windows (PowerShell):

powershell
.venv\Scripts\activate
Windows (cmd):

cmd
.venv\Scripts\activate.bat
macOS / Linux:

bash
source .venv/bin/activate
Step 4. Install dependencies
bash
pip install -r requirements.txt
Or manually:

bash
pip install PyQt5 certifi
Step 5. Run
bash
python main.py
That's it. On the first launch you'll see:

text
[INIT] Созданы папки:
       - font
       - save
       - done
These are created automatically — no manual setup needed.

Optional: Add your own fonts
Drop any .ttf or .otf files into the font/ folder. They will appear in the text editor's font list on next launch.

Optional: Custom app icon
Place icon.png (512×512) and/or icon.ico in the project root.

icon.ico — preferred for Windows taskbar.

icon.png — fallback.

🎯 Features (Русский)
Холст и макеты
Создание холста любого размера — от 50×50 до 5000×5000 px, с готовыми пресетами (500×500, 1080×1080, 1920×1080, 1080×1920).

По умолчанию прозрачный холст — шахматный фон показывает прозрачность.

Свой цвет фона — выберите любой цвет с альфа-каналом (0–100% прозрачности), либо сбросьте обратно в прозрачный.

Объекты и редактирование
Добавление изображений — через диалог, перетаскиванием из проводника или вставкой из буфера (Ctrl+V для скриншотов).

Добавление текста — выбор из системных шрифтов + любые .ttf / .otf из папки font/. Поддержка русского и латиницы.

Выделение / перемещение / ресайз — клик по объекту выделяет его, перетаскивание двигает, угловые ручки — изменяют размер.

Мультивыделение — Ctrl+клик добавляет к выделению, Ctrl+A выделяет всё.

Слои — вперёд, назад, на передний план, на задний план.

Отразить и повернуть — зеркальное отражение по горизонтали / вертикали, поворот на любой угол (пресеты 15°, 30°, 45°, 90°, 180°, −90°).

Прозрачность и фильтры — яркость, контраст, насыщенность, индивидуальная прозрачность каждого объекта.

Поиск клипартов (Clipart.Free API)
Встроенная панель поиска — ищите миллионы CC0-клипартов прямо в приложении.

Постраничная выдача — 30 результатов на страницу, ленивая загрузка превью, 4 в ряд.

Вставка в один клик — клик по превью скачивает полноразмерный PNG и вставляет его на холст.

Локальное хранилище
Библиотека на основе папок — организуйте изображения в папки внутри save/.

Создание / удаление папок — правый клик по папке вызывает меню.

Превью — сетка со всеми изображениями и подсветкой при наведении.

Отмена и история
Безлимитная отмена — до 100 шагов (Ctrl+Z).

Копировать / вырезать / вставить — как для объектов холста, так и для содержимого системного буфера.

Дублировать — Ctrl+D.

Экспорт
Сохранение в папку done/ — экспорт финальной композиции в PNG или JPEG.

Сохранение прозрачности — если фон прозрачный, итоговый PNG тоже прозрачный.

UX
Тёмная тема — своя палитра, тёмные панели, синие акценты.

Своя иконка приложения — берётся icon.ico или icon.png из корня проекта, для Windows задаётся AppUserModelID (чтобы иконка была на панели задач, а не иконка Python).

Папки создаются автоматически — font/, save/, done/ создаются при первом запуске.

Клавиатурный workflow — у всех основных действий есть горячие клавиши.

⚙️ Установка и запуск (Русский)
Требования
Python 3.8 – 3.12 (на 3.13/3.14 может не быть готовых колёс для PyQt5).

Windows 10/11, macOS или Linux.

~150 МБ на диске для зависимостей.

Шаг 1. Установите Python
Скачайте с python.org.
При установке поставьте галочку «Add Python to PATH».

Проверка:

bash
python --version
Шаг 2. Клонируйте репозиторий
bash
git clone https://github.com/ВАШ_ЛОГИН/ВАШ_РЕПОЗИТОРИЙ.git
cd ВАШ_РЕПОЗИТОРИЙ
Или скачайте ZIP с GitHub и распакуйте.

Шаг 3. Создайте виртуальное окружение (рекомендуется)
bash
python -m venv .venv
Активируйте его:

Windows (PowerShell):

powershell
.venv\Scripts\activate
Windows (cmd):

cmd
.venv\Scripts\activate.bat
macOS / Linux:

bash
source .venv/bin/activate
Шаг 4. Установите зависимости
bash
pip install -r requirements.txt
Или вручную:

bash
pip install PyQt5 certifi
Шаг 5. Запустите
bash
python main.py
Готово. При первом запуске вы увидите:

text
[INIT] Созданы папки:
       - font
       - save
       - done
Папки создаются автоматически — вручную ничего настраивать не нужно.

Опционально: свои шрифты
Положите любые .ttf или .otf в папку font/. При следующем запуске они появятся в списке шрифтов редактора текста.

Опционально: своя иконка
Положите icon.png (512×512) и/или icon.ico в корень проекта.

icon.ico — лучше для панели задач Windows.

icon.png — запасной вариант.

📂 Project Structure / Структура проекта
text
project/
├── main.py             # Entry point — the whole app in one file
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── .gitignore          # Ignored files
├── icon.png            # App icon (optional)
├── icon.ico            # App icon for Windows taskbar (optional)
├── font/               # Put your .ttf / .otf fonts here
├── save/               # Local storage of added images (auto-created)
└── done/               # Exported results (auto-created)
text
проект/
├── main.py             # Точка входа — всё приложение в одном файле
├── requirements.txt    # Зависимости Python
├── README.md           # Этот файл
├── .gitignore          # Игнорируемые файлы
├── icon.png            # Иконка приложения (опционально)
├── icon.ico            # Иконка для панели задач Windows (опционально)
├── font/               # Сюда кладите свои .ttf / .otf шрифты
├── save/               # Локальное хранилище добавленных изображений (создаётся автоматически)
└── done/               # Экспортированные результаты (создаётся автоматически)
⌨️ Hotkeys / Горячие клавиши
Action / Действие	Windows / Linux	macOS
Copy / Копировать	Ctrl+C	Cmd+C
Cut / Вырезать	Ctrl+X	Cmd+X
Paste / Вставить	Ctrl+V	Cmd+V
Select all / Выделить всё	Ctrl+A	Cmd+A
Undo / Отменить	Ctrl+Z	Cmd+Z
Duplicate / Дублировать	Ctrl+D	Cmd+D
Delete / Удалить	Del / Backspace	Del
Deselect / Снять выделение	Esc	Esc
Zoom in/out / Зум	Ctrl + wheel	Cmd + wheel
Pan / Панорама	middle mouse / колёсико	middle mouse / колёсико
📝 License / Лицензия
MIT License — free to use, modify, and distribute.
MIT License — свободно использовать, изменять, распространять.

🤝 Contributing / Контрибьютинг
Pull requests are welcome. For major changes, please open an issue first.
Pull request'ы приветствуются. Для крупных изменений сначала откройте issue.

⭐ Credits / Благодарности
Built with PyQt5

Clipart search powered by Clipart.Free

SSL certificates by certifi

