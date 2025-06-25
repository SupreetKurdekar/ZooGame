import pygame
import random
from typing import List, Tuple, Optional
from game import ANIMALS, GRID_SIZE, check_sequence, check_condition, choose_spot, choose_spot_ai, ai_bid

Board = List[List[Optional[str]]]

TILE_SIZE = 80
MARGIN = 10


def draw_board(screen: pygame.Surface, board: Board, font: pygame.font.Font) -> None:
    """Draw the game board on the left side of the screen."""
    for r, row in enumerate(board):
        for c, tile in enumerate(row):
            rect = pygame.Rect(MARGIN + c * TILE_SIZE,
                               MARGIN + r * TILE_SIZE,
                               TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (245, 245, 220), rect)  # light tile
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)
            if tile:
                text = font.render(tile[0], True, (0, 0, 0))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)


def draw_info(screen: pygame.Surface, chips, seq, cond, font: pygame.font.Font, x: int) -> None:
    """Draw player information on the right side."""
    y = MARGIN
    for player in (1, 2):
        lines = [
            f"Player {player}",
            f"Chips: {chips[player]}",
            f"Seq: {'-'.join(seq[player])}",
            f"Cond: more {cond[player][0]} than {cond[player][1]}",
            ""
        ]
        for line in lines:
            text = font.render(line, True, (0, 0, 0))
            screen.blit(text, (x, y))
            y += font.get_height() + 5
        y += font.get_height()


def run_game_visual(ai: bool = False) -> None:
    pygame.init()
    board_width = GRID_SIZE * TILE_SIZE
    info_width = 300
    screen = pygame.display.set_mode((board_width + info_width + 3 * MARGIN,
                                      GRID_SIZE * TILE_SIZE + 2 * MARGIN))
    pygame.display.set_caption("Zoo Mahjong")
    font_large = pygame.font.SysFont(None, 48)
    font_small = pygame.font.SysFont(None, 24)

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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        screen.fill((200, 200, 200))
        draw_board(screen, board, font_large)
        draw_info(screen, chips, seq, cond, font_small,
                  board_width + 2 * MARGIN)
        pygame.display.flip()

        print(f"--- Round {current_round} ---")
        tile = random.choice(ANIMALS)
        print(f"Tile up for auction: {tile}")
        bids = {}
        for player in (1, 2):
            if ai and player == 2:
                bid = ai_bid(chips[player])
                print(f"Computer bids {bid} (chips left {chips[player]})")
            else:
                while True:
                    try:
                        bid = int(input(f"Player {player} bids (chips left {chips[player]}): "))
                        if 0 <= bid <= chips[player]:
                            break
                        else:
                            print("Invalid bid.")
                    except ValueError:
                        print("Enter a number.")
            bids[player] = bid

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

        if check_sequence(board, seq[winner]) or check_condition(board, *cond[winner]):
            screen.fill((200, 200, 200))
            draw_board(screen, board, font_large)
            draw_info(screen, chips, seq, cond, font_small,
                      board_width + 2 * MARGIN)
            pygame.display.flip()
            print(f"Player {winner} wins!")
            pygame.time.wait(2000)
            pygame.quit()
            return

        current_round += 1

    screen.fill((200, 200, 200))
    draw_board(screen, board, font_large)
    draw_info(screen, chips, seq, cond, font_small,
              board_width + 2 * MARGIN)
    pygame.display.flip()
    print("The board is full. It's a draw!")
    pygame.time.wait(2000)
    pygame.quit()


if __name__ == "__main__":
    import sys
    ai_mode = len(sys.argv) > 1 and sys.argv[1].lower() == "ai"
    run_game_visual(ai=ai_mode)
