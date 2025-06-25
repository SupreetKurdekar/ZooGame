# ZooGame

This repository contains a simple two-player command line game written in Python.
Players compete to fill a 5x5 grid with animal tiles according to their secret
winning conditions.

Run the game with:

```bash
python3 game.py
```

You can also play against a simple computer opponent for debugging with:

```bash
python3 game.py ai
```

During each round a random animal tile is auctioned. Players bid chips and the
winner places the tile on the grid. A player wins by either forming their secret
sequence of three animals or fulfilling their condition card stating that one
animal must appear more times than another.

