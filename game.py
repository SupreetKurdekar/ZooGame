import random
from typing import List, Tuple, Optional

ANIMALS = ["Lion", "Monkey", "Elephant", "Giraffe", "Tiger"]
GRID_SIZE = 5

Board = List[List[Optional[str]]]


def display_board(board: Board) -> None:
    print("  " + " ".join(str(i) for i in range(GRID_SIZE)))
    for idx, row in enumerate(board):
        row_display = [tile[0] if tile else '.' for tile in row]
        print(f"{idx} " + " ".join(row_display))
    print()


def check_sequence(board: Board, sequence: List[str]) -> bool:
    seq_len = len(sequence)
    # rows
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - seq_len + 1):
            if board[r][c:c+seq_len] == sequence:
                return True
    # columns
    for c in range(GRID_SIZE):
        for r in range(GRID_SIZE - seq_len + 1):
            col_segment = [board[r+i][c] for i in range(seq_len)]
            if col_segment == sequence:
                return True
    # diagonals (top-left to bottom-right)
    for r in range(GRID_SIZE - seq_len + 1):
        for c in range(GRID_SIZE - seq_len + 1):
            diag_segment = [board[r+i][c+i] for i in range(seq_len)]
            if diag_segment == sequence:
                return True
    # diagonals (bottom-left to top-right)
    for r in range(seq_len - 1, GRID_SIZE):
        for c in range(GRID_SIZE - seq_len + 1):
            diag_segment = [board[r-i][c+i] for i in range(seq_len)]
            if diag_segment == sequence:
                return True
    return False


def check_condition(board: Board, more: str, less: str) -> bool:
    flat = [tile for row in board for tile in row if tile]
    return flat.count(more) > flat.count(less)


def choose_spot(board: Board) -> Tuple[int, int]:
    while True:
        try:
            coords = input("Choose spot as row,col: ")
            r, c = map(int, coords.split(','))
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and board[r][c] is None:
                return r, c
            print("Invalid spot. Try again.")
        except Exception:
            print("Invalid input. Use row,col format.")


def ai_bid(chips: int) -> int:
    """Return a simple bid for the computer player."""
    return random.randint(0, chips)


def choose_spot_ai(board: Board) -> Tuple[int, int]:
    """Return a random free spot on the board for the computer player."""
    available = [
        (r, c)
        for r in range(GRID_SIZE)
        for c in range(GRID_SIZE)
        if board[r][c] is None
    ]
    return random.choice(available)


def run_game(ai: bool = False) -> None:
    """Run a game. If ``ai`` is True, player 2 is computer controlled."""
    board: Board = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
    chips = {1: 10, 2: 10}
    seq = {1: random.sample(ANIMALS, 3), 2: random.sample(ANIMALS, 3)}
    cond = {}
    for player in (1, 2):
        more, less = random.sample(ANIMALS, 2)
        cond[player] = (more, less)
        print(f"\nPlayer {player} secret sequence: {seq[player]}")
        print(f"Player {player} condition: more {more} than {less}\n")

    current_round = 1
    while any(None in row for row in board):
        print(f"--- Round {current_round} ---")
        display_board(board)
        tile = random.choice(ANIMALS)
        print(f"Tile up for auction: {tile}")
        bids = {}
        for player in (1, 2):
            if ai and player == 2:
                bid = ai_bid(chips[player])
                print(f"Computer bids {bid} (chips left {chips[player]})")
                bids[player] = bid
            else:
                while True:
                    try:
                        bid = int(input(f"Player {player} bids (chips left {chips[player]}): "))
                        if 0 <= bid <= chips[player]:
                            bids[player] = bid
                            break
                        else:
                            print("Invalid bid.")
                    except ValueError:
                        print("Enter a number.")
        if bids[1] == bids[2]:
            winner = random.choice([1, 2])
            print(f"Tie! Player {winner} wins the auction by coin flip.")
        else:
            winner = 1 if bids[1] > bids[2] else 2
        chips[winner] -= bids[winner]
        print(f"Player {winner} wins and places the tile.")
        if ai and winner == 2:
            r, c = choose_spot_ai(board)
            print(f"Computer chooses spot {r},{c}")
        else:
            r, c = choose_spot(board)
        board[r][c] = tile

        for player in (1, 2):
            if check_sequence(board, seq[player]) or check_condition(board, *cond[player]):
                display_board(board)
                print(f"Player {player} wins!")
                return
        current_round += 1
    display_board(board)
    print("The board is full. It's a draw!")


if __name__ == "__main__":
    import sys
    ai_mode = len(sys.argv) > 1 and sys.argv[1].lower() == "ai"
    run_game(ai=ai_mode)
