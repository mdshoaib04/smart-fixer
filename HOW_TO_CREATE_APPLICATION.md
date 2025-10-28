# How to Create a Standalone SmartFixer Application

This document explains how to create a proper executable application with an icon for SmartFixer.

## Prerequisites

1. Python 3.11 or higher installed on your system
2. pip (Python package manager)

## Steps to Create the Application

### 1. Install Required Tools

Open a command prompt and run:

```bash
pip install pyinstaller
```

### 2. Create the Application Icon

The icon file has already been created for you in the project.

### 3. Create the Main Application Script

The main application script (`SmartFixer-App.py`) has been created for you.

### 4. Build the Executable

Run the following command:

```bash
pyinstaller --onefile --windowed --icon=icon.ico SmartFixer-App.py
```

This will create:
- A `dist` folder containing the executable application
- A `build` folder with temporary files (can be deleted after build)

### 5. Package the Application

To create a distributable package:

1. Copy the executable from the `dist` folder
2. Copy the `icon.ico` file
3. Create a ZIP file containing:
   - The executable
   - The icon file
   - A README.txt with installation instructions

## Application Features

The standalone application will:

1. Automatically start the SmartFixer server
2. Open your default web browser to `http://localhost:5000`
3. Run in the background until you close the command window
4. Have a proper application icon

## Distribution

To distribute the application:

1. Create a ZIP file with all necessary files
2. Users can extract the ZIP and run the executable directly
3. No Python installation required on the user's machine

## Troubleshooting

### If the application doesn't start:

1. Make sure no other instances of SmartFixer are running
2. Check that port 5000 is available
3. Try running the application as administrator

### If the browser doesn't open automatically:

1. Manually navigate to `http://localhost:5000` in your browser
2. Check that the server is running in the command window

### If you get an error about missing dependencies:

1. Install the missing packages with `pip install package_name`
2. Rebuild the application

## Customization

You can customize the build process by modifying the PyInstaller command:

- `--onefile`: Creates a single executable file
- `--windowed`: Hides the console window (Windows only)
- `--icon=icon.ico`: Sets the application icon
- `--name=SmartFixer`: Sets the name of the executable

For more options, run `pyinstaller --help`