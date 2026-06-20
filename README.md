# ComiConv 📚🔄
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/KyLaEga/MediaConverterPro/build.yml?branch=main&label=Build&logo=github)](https://github.com/KyLaEga/MediaConverterPro/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](#english) | [Русский](#русский)

---

<a name="english"></a>
## 🇬🇧 English

**ComiConv** is a powerful, cross-platform desktop application designed for the automated batch conversion of comics and images into **CBZ** and **PDF** formats.

Built with a modern UI (PySide6), it supports recursive processing of a huge number of files without requiring manual confirmations.

### 🎨 Features
- **Batch Processing**: Load dozens of archives (`.zip`, `.cbz`) or image folders — the program will automatically queue and convert them.
- **Multi-Selection Support**: You can select specific archives as well as entire directories for recursive scanning.
- **Bilingual Interface**: Full support for English and Russian (switching on the fly).
- **Light & Dark Themes**: An elegant `ThemeManager` design system that adapts to your preferences.
- **Multithreading**: The GUI never freezes, thanks to heavy logic processing in background threads (`QThread`).
- **Separate Output Paths**: Specify different directories for generating CBZ and PDF files. Uncheck a format if you don't need it.

### 📦 Download Ready-to-Use Application
We use **GitHub Actions** to automatically compile the project into native, ready-to-use applications.
You can download the latest built files in the **[Releases](https://github.com/KyLaEga/MediaConverterPro/releases)** section!
- 🍎 **macOS**: `ComiConv-macOS.zip` (extract and run `.app`)
- 🪟 **Windows**: `ComiConv-Windows.exe`
- 🐧 **Linux**: `ComiConv-Linux` (executable binary)

### 🚀 Local Usage (For Developers)
```bash
git clone https://github.com/KyLaEga/ComiConv.git
cd ComiConv
./start.sh
```

---

<a name="русский"></a>
## 🇷🇺 Русский

**ComiConv** — это мощное кроссплатформенное Desktop-приложение, созданное для автоматической пакетной конвертации комиксов и изображений в форматы **CBZ** и **PDF**.

Разработано с использованием современного интерфейса (PySide6) и поддерживает рекурсивную обработку огромного числа файлов без необходимости ручных подтверждений.

### 🎨 Особенности
- **Пакетная Обработка (Batch Processing)**: Загрузите десятки архивов (`.zip`, `.cbz`) или папок с изображениями — программа сама выстроит их в очередь и сконвертирует.
- **Поддержка Мультивыбора**: Можно выбирать как отдельные архивы, так и целые директории для рекурсивного поиска.
- **Двуязычный Интерфейс**: Полная поддержка русского и английского языков (переключение на лету).
- **Светлая и Темная Темы**: Элегантная дизайн-система, которая подстраивается под ваши предпочтения.
- **Многопоточность**: Графический интерфейс никогда не зависает благодаря вынесению тяжелой логики в фоновые потоки.
- **Раздельные пути вывода**: Укажите разные директории для генерации CBZ и PDF файлов. Если нужный формат вам не нужен — просто снимите галочку.

### 📦 Скачать Готовое Приложение
Мы используем **GitHub Actions** для автоматической компиляции проекта.
Вы можете скачать последние собранные файлы во вкладке **[Releases](https://github.com/KyLaEga/MediaConverterPro/releases)**!
- 🍎 **macOS**: `ComiConv-macOS.zip` (распакуйте и запустите `.app`)
- 🪟 **Windows**: `ComiConv-Windows.exe`
- 🐧 **Linux**: `ComiConv-Linux` (исполняемый бинарник)

### 🚀 Запуск из исходников (Для Разработчиков)
```bash
git clone https://github.com/KyLaEga/ComiConv.git
cd ComiConv
./start.sh
```
