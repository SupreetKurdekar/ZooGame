import pygame
import random
from typing import List, Tuple, Optional
from game import ANIMALS, GRID_SIZE, check_sequence, check_condition, choose_spot_ai, ai_bid

Board = List[List[Optional[str]]]

TILE_SIZE = 80
MARGIN = 10
AUCTION_HEIGHT = TILE_SIZE + MARGIN  # space above board to show next tile


def draw_board(screen: pygame.Surface, board: Board, font: pygame.font.Font) -> None:
    """Draw the game board on the left side of the screen."""
    for r, row in enumerate(board):
        for c, tile in enumerate(row):
            rect = pygame.Rect(MARGIN + c * TILE_SIZE,
                               AUCTION_HEIGHT + MARGIN + r * TILE_SIZE,
                               TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (245, 245, 220), rect)  # light tile
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)
            if tile:
                text = font.render(tile[0], True, (0, 0, 0))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)


def draw_next_tile(screen: pygame.Surface, tile: str, font: pygame.font.Font,
                   board_width: int) -> None:
    """Draw the tile that is currently up for auction above the board."""
    area = pygame.Rect(MARGIN, MARGIN, board_width, TILE_SIZE)
    pygame.draw.rect(screen, (220, 220, 220), area)
    pygame.draw.rect(screen, (0, 0, 0), area, 2)
    if tile:
        text = font.render(tile, True, (0, 0, 0))
        text_rect = text.get_rect(center=area.center)
        screen.blit(text, text_rect)


def choose_spot_visual(board: Board, board_width: int) -> Tuple[int, int]:
    """Wait for the player to click an empty spot and return its coordinates."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if (MARGIN <= x < MARGIN + board_width and
                        AUCTION_HEIGHT + MARGIN <= y < AUCTION_HEIGHT + MARGIN + GRID_SIZE * TILE_SIZE):
                    c = (x - MARGIN) // TILE_SIZE
                    r = (y - AUCTION_HEIGHT - MARGIN) // TILE_SIZE
                    if board[r][c] is None:
                        return r, c
        pygame.time.wait(10)


def draw_player_panel(screen: pygame.Surface, player: int, chips, seq, cond,
                      font: pygame.font.Font, rect: pygame.Rect,
                      text: str = "") -> None:
    """Draw a single player's info and a bid box."""
    pygame.draw.rect(screen, (220, 220, 220), rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2)
    padding = 5
    y = rect.y + padding

    lines = [
        f"Player {player}",
        f"Chips: {chips[player]}",
        f"Seq: {'-'.join(seq[player])}",
        f"Cond: more {cond[player][0]} than {cond[player][1]}",
        "",
    ]
    for line in lines:
        text_surf = font.render(line, True, (0, 0, 0))
        screen.blit(text_surf, (rect.x + padding, y))
        y += font.get_height() + 5

    box_h = font.get_height() + 10
    box_rect = pygame.Rect(rect.x + padding,
                           rect.bottom - box_h - padding,
                           rect.width - 2 * padding, box_h)
    pygame.draw.rect(screen, (255, 255, 255), box_rect)
    pygame.draw.rect(screen, (0, 0, 0), box_rect, 2)
    bid_surf = font.render(text, True, (0, 0, 0))
    screen.blit(bid_surf, (box_rect.x + 5, box_rect.y + 5))


def get_bid_input(screen: pygame.Surface, board: Board, tile: str, player: int,
                   chips, seq, cond, font_large, font_small, board_width,
                   rects, last_winner: str) -> int:
    """Return a bid entered via on-screen text box."""
    top_rect, middle_rect, bottom_rect = rects
    text = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if text == "":
                        print("Enter a number.")
                        continue
                    try:
                        bid_val = int(text)
                    except ValueError:
                        print("Enter a number.")
                        text = ""
                        continue
                    if 0 <= bid_val <= chips[player]:
                        return bid_val
                    print("Invalid bid.")
                    text = ""
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.unicode.isdigit():
                    text += event.unicode

        screen.fill((200, 200, 200))
        draw_next_tile(screen, tile, font_large, board_width)
        draw_board(screen, board, font_large)
        draw_middle_text(screen, last_winner, font_small, middle_rect)
        if player == 1:
            draw_player_panel(screen, 1, chips, seq, cond, font_small,
                              top_rect, text)
            pygame.draw.rect(screen, (200, 200, 200), bottom_rect)
        else:
            pygame.draw.rect(screen, (200, 200, 200), top_rect)
            draw_player_panel(screen, 2, chips, seq, cond, font_small,
                              bottom_rect, text)
        pygame.display.flip()
        pygame.time.wait(10)

def draw_middle_text(screen: pygame.Surface, message: str,
                     font: pygame.font.Font, rect: pygame.Rect) -> None:
    """Draw the bidding result in the center info panel."""
    pygame.draw.rect(screen, (220, 220, 220), rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2)
    if message:
        text_surf = font.render(message, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)


def select_ai_mode(screen: pygame.Surface,
                   font: pygame.font.Font) -> bool:
    """Return True for a 1-player game, False for 2 players."""
    w, h = screen.get_size()
    one_rect = pygame.Rect(w // 2 - 160, h // 2 - 40, 140, 60)
    two_rect = pygame.Rect(w // 2 + 20, h // 2 - 40, 140, 60)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if one_rect.collidepoint(event.pos):
                    return True
                if two_rect.collidepoint(event.pos):
                    return False

        screen.fill((220, 220, 220))
        pygame.draw.rect(screen, (180, 180, 180), one_rect)
        pygame.draw.rect(screen, (180, 180, 180), two_rect)
        pygame.draw.rect(screen, (0, 0, 0), one_rect, 2)
        pygame.draw.rect(screen, (0, 0, 0), two_rect, 2)

        text1 = font.render("1 Player", True, (0, 0, 0))
        text2 = font.render("2 Players", True, (0, 0, 0))
        screen.blit(text1, text1.get_rect(center=one_rect.center))
        screen.blit(text2, text2.get_rect(center=two_rect.center))
        pygame.display.flip()
        pygame.time.wait(10)


def run_game_visual(ai: Optional[bool] = None) -> None:
    pygame.init()
    board_width = GRID_SIZE * TILE_SIZE
    info_width = 300
    screen_height = AUCTION_HEIGHT + GRID_SIZE * TILE_SIZE + 2 * MARGIN
    screen = pygame.display.set_mode((board_width + info_width + 3 * MARGIN,
                                      screen_height))
    pygame.display.set_caption("Zoo Mahjong")
    font_large = pygame.font.SysFont(None, 48)
    font_small = pygame.font.SysFont(None, 24)

    top_rect = pygame.Rect(board_width + 2 * MARGIN, MARGIN, info_width, 150)
    bottom_rect = pygame.Rect(board_width + 2 * MARGIN,
                              screen_height - 150 - MARGIN,
                              info_width, 150)
    middle_height = bottom_rect.top - top_rect.bottom - MARGIN
    middle_rect = pygame.Rect(board_width + 2 * MARGIN,
                              top_rect.bottom + MARGIN,
                              info_width, middle_height)

    if ai is None:
        ai = select_ai_mode(screen, font_large)
        screen.fill((200, 200, 200))
        pygame.display.flip()

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
    last_winner = ""
    tile = None
    while any(None in row for row in board):
        tile = random.choice(ANIMALS)
        print(f"--- Round {current_round} ---")
        print(f"Tile up for auction: {tile}")

        bids = {}
        for player in (1, 2):
            if ai and player == 2:
                bid = ai_bid(chips[player])
                print(f"Computer bids {bid} (chips left {chips[player]})")
            else:
                bid = get_bid_input(screen, board, tile, player, chips, seq, cond,
                                    font_large, font_small, board_width,
                                    (top_rect, middle_rect, bottom_rect),
                                    last_winner)
            bids[player] = bid

        if bids[1] == bids[2]:
            winner = random.choice([1, 2])
            print(f"Tie! Player {winner} wins the auction by coin flip.")
        else:
            winner = 1 if bids[1] > bids[2] else 2
        chips[winner] -= bids[winner]
        last_winner = f"Player {winner} won the bid"
        print(f"Player {winner} wins and places the tile.")
        screen.fill((200, 200, 200))
        draw_next_tile(screen, tile, font_large, board_width)
        draw_board(screen, board, font_large)
        draw_middle_text(screen, last_winner, font_small, middle_rect)
        if not (ai and winner == 2):
            panel_rect = top_rect if winner == 1 else bottom_rect
            draw_player_panel(screen, winner, chips, seq, cond,
                              font_small, panel_rect)
        pygame.display.flip()
        if ai and winner == 2:
            r, c = choose_spot_ai(board)
            print(f"Computer chooses spot {r},{c}")
        else:
            print("Click an empty spot to place the tile.")
            r, c = choose_spot_visual(board, board_width)
        board[r][c] = tile

        if check_sequence(board, seq[winner]) or check_condition(board, *cond[winner]):
            screen.fill((200, 200, 200))
            draw_next_tile(screen, "", font_large, board_width)
            draw_board(screen, board, font_large)
            draw_middle_text(screen, f"Player {winner} wins!", font_small,
                             middle_rect)
            pygame.display.flip()
            print(f"Player {winner} wins!")
            pygame.time.wait(2000)
            pygame.quit()
            return

        current_round += 1

    screen.fill((200, 200, 200))
    draw_next_tile(screen, "", font_large, board_width)
    draw_board(screen, board, font_large)
    draw_middle_text(screen, "It's a draw!", font_small, middle_rect)
    pygame.display.flip()
    print("The board is full. It's a draw!")
    pygame.time.wait(2000)
    pygame.quit()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1].lower() == "ai":
        run_game_visual(ai=True)
    else:
        run_game_visual(ai=None)
