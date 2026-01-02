#!/bin/bash
# Checks if PyInstaller is installed, then builds the executable
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller could not be found, installing..."
    if ! command -v pipx &> /dev/null
    then
        echo "pipx could not be found, using pip"
        pip install --user pyinstaller
    else
        pipx install pyinstaller
    fi
fi
pyinstaller --onefile --clean --name noapi run.py
if [ $? -eq 0 ]; then
    cp dist/noapi .
    echo "Build successful!"
else
    echo "Build failed!"
fi