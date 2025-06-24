# OCR-Screen

![Logo](https://raw.githubusercontent.com/karanie/ocr-screen/refs/heads/master/icon.png)

Another low effort college student semester project.

This project provide a way to copy text from a screenshot.

## Installation and Usage

Run `install.bat` script as admin. Ignore the warning, I can assure you it's safe (i don't really know how to package python script and create the setup installer for windows. im not sorry).

To use the program, you will need to run `main.py` code. You can use `uv` like so,

```
uv run main.py
```

Or,

```
source .venv/bin/activate
python main.py
```

You cannot run the `main.py` directly. You need to enter the virtual environment of the projects, and then execute it from there.

## Uninstallation

Just nuke the project directory, and optionally uninstall `tesseract`, and `uv`.

## Configuration

Configuration can be done with the settings window that you can open via the menu on tray icon. The config consists of two main things:

* The users (idk why is that even exist)
* And profiles.

A user has one or many profiles. A profile define what hotkey it will read, how will it capture the text on your screen and the kind of model it will use. A profile cannot have more than one hotkey, you will need to create another profile to do that. Remember to always save or apply any changes to the settings.

The config is stored in SQLite `settings.db` file. You can decide to back it up and/or move it somewhere else.

### OCR Models

This program uses [Tesseract](https://github.com/tesseract-ocr/tesseract) and [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) version 2. You probably want to use Tesseract if you want a fast OCR. If you prefer accuracy you probably want PaddleOCR. PaddleOCR may have slow cold start however.

The language of the model can also be configured in the settings window.
