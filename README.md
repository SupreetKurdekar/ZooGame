# ZooGame

This repository contains a simple two-player command line game written in Python.
Players compete to fill a 5x5 grid with animal tiles according to their secret
winning conditions.

## Setup

1. Install Python 3.7 or newer.
2. (Optional) Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required packages:
   ```bash
   pip install -r requirement.txt
   ```

Run the game with:

```bash
python3 game.py
```

You can also play against a simple computer opponent for debugging with:

```bash
python3 game.py ai
```

Alternatively you can launch a basic graphical version using pygame:

```bash
python3 visual_game.py
```

The visual mode also supports the `ai` argument to enable a computer opponent:

```bash
python3 visual_game.py ai
```

### Building a Windows Executable

If you want a standalone executable of the graphical version, install
`PyInstaller` and run it on a Windows machine:

```bash
pip install pyinstaller
pyinstaller --onefile visual_game.py
```

The resulting `visual_game.exe` will be located in the `dist` folder.

During each round a random animal tile is auctioned. Players bid chips and the
winner places the tile on the grid. A player wins by either forming their secret
sequence of three animals or fulfilling their condition card stating that one
animal must appear more times than another.

