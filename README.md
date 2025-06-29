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
python game.py
```

You'll be prompted to choose between a 1-player game (against the computer) or a
2-player game. You can still provide the optional `ai` argument to skip the
prompt and immediately start in single-player mode:

```bash
python game.py ai
```

Alternatively you can launch a basic graphical version using pygame:

```bash
python visual_game.py
```

When starting the graphical mode you'll first see a small menu where you can
choose between a 1-player game or a 2-player game. The `ai` argument can still
be used to bypass the menu and immediately start in single-player mode:

```bash
python visual_game.py ai
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

