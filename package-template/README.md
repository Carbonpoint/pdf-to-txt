# PDF to Text Converter

This repo contains a Python app that converts PDF files in a directory tree into text files in a cloned destination tree.

## App Overview

- Recursively scans a source directory for PDF files.
- Preserves subfolder structure in the destination directory.
- Writes `.txt` files next to the mirrored path for each `.pdf` file.
- Supports optional overwrite of existing text files.

## Usage

Install required dependencies from PowerShell using the workspace virtual environment:

```powershell
cd package-template
& ..\.venv\Scripts\python.exe -m pip install -e .
```

Run the converter from the package directory:

```powershell
cd package-template
& ..\.venv\Scripts\python.exe -m my_package
```

This app now defaults to the Zotero storage location and the Zotero text server output location:

- Source: `C:\Users\silverframe\Zotero\storage`
- Destination: `C:\Users\silverframe\Projects\zotero-text-server\txt`

If you still see `python` not found, install Python from https://www.python.org/downloads/ or enable the App Execution Alias for Python in Settings > Apps > Advanced app settings > App execution aliases.

Example missing-only run:

```powershell
cd package-template
& ..\.venv\Scripts\python.exe -m my_package
```

Example complete refresh run:

```powershell
cd package-template
& ..\.venv\Scripts\python.exe -m my_package --refresh
```

To override the default directories, pass `--source` and `--destination`:

```powershell
& ..\.venv\Scripts\python.exe -m my_package --source "C:\path\to\pdfs" --destination "C:\path\to\txt"
```

## Setup Instructions 

This sample makes use of Dev Containers, in order to leverage this setup, make sure you have [Docker installed](https://www.docker.com/products/docker-desktop).

The code in this repo aims to follow Python style guidelines as outlined in [PEP 8](https://peps.python.org/pep-0008/).

To successfully run this example, we recommend the following VS Code extensions:

- [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Python Debugger](https://marketplace.visualstudio.com/items?itemName=ms-python.debugpy)
- [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) 

In addition to these extension there a few settings that are also useful to enable. You can enable to following settings by opening the Settings editor (`Ctrl+,`) and searching for the following settings:

- Python > Analysis > **Type Checking Mode** : `basic`
- Python > Analysis > Inlay Hints: **Function Return Types** : `enable`
- Python > Analysis > Inlay Hints: **Variable Types** : `enable`

## Running the Sample
- Open the template folder in VS Code (**File** > **Open Folder...**)
- Open the Command Palette in VS Code (**View > Command Palette...**) and run the **Dev Container: Reopen in Container** command
- Run the app using the Run and Debug view
- To test, navigate to the Test Panel to configure your Python test or by triggering the **Python: Configure Tests** command from the Command Palette
- Run tests in the Test Panel or by clicking the Play Button next to the individual tests in the `test_date_time.py` and `test_developer.py` file
