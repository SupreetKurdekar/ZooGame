import os
import pygame
import random
from typing import List, Tuple, Optional, Dict
from game import (
    ANIMALS,
    GRID_SIZE,
    check_sequence,
    check_condition,
    choose_spot_ai,
    ai_bid,
)

Board = List[List[Optional[str]]]

TILE_SIZE = 80
MARGIN = 10
AUCTION_HEIGHT = TILE_SIZE + MARGIN  # space above board to show next tile

# Will be populated after pygame is initialized
ANIMAL_IMAGES: Dict[str, pygame.Surface] = {}


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
                img = ANIMAL_IMAGES.get(tile)
                if img:
                    img_rect = img.get_rect(center=rect.center)
                    screen.blit(img, img_rect)
                else:
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
        img = ANIMAL_IMAGES.get(tile)
        if img:
            img_rect = img.get_rect(center=area.center)
            screen.blit(img, img_rect)
        else:
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
    if text:
        bid_surf = font.render(text, True, (0, 0, 0))
    else:
        bid_surf = font.render("Enter bid here", True, (150, 150, 150))
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
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if text == "":
                        continue
                    try:
                        bid_val = int(text)
                    except ValueError:
                        text = ""
                        continue
                    if 0 <= bid_val <= chips[player]:
                        return bid_val
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
    # Buttons sit near the bottom so we have space for the title and rules
    one_rect = pygame.Rect(w // 2 - 190, h - 120, 180, 60)
    two_rect = pygame.Rect(w // 2 + 10, h - 120, 180, 60)

    title_font = pygame.font.SysFont("arial", 72)
    info_font = pygame.font.SysFont(None, 28)
    rules = [
        "Each round a random animal tile is auctioned.",
        "Players bid chips and the winner places the tile.",
        "Win by completing your secret sequence",
        "or by meeting your animal condition.",
    ]

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
        # Title
        title_surf = title_font.render("Zoo Mahjong", True, (0, 0, 0))
        screen.blit(title_surf, title_surf.get_rect(center=(w // 2, 70)))

        # Explanation and rules
        start_y = 140
        explain = info_font.render(
            "Bid on animals and fill the grid to win!", True, (0, 0, 0)
        )
        screen.blit(explain, explain.get_rect(center=(w // 2, start_y)))
        start_y += info_font.get_linesize() + 10
        for line in rules:
            line_surf = info_font.render(line, True, (0, 0, 0))
            screen.blit(line_surf, line_surf.get_rect(center=(w // 2, start_y)))
            start_y += info_font.get_linesize() + 5

        # Buttons
        pygame.draw.rect(screen, (180, 180, 180), one_rect)
        pygame.draw.rect(screen, (180, 180, 180), two_rect)
        pygame.draw.rect(screen, (0, 0, 0), one_rect, 2)
        pygame.draw.rect(screen, (0, 0, 0), two_rect, 2)

        text1 = info_font.render("1 Player", True, (0, 0, 0))
        text2 = info_font.render("2 Players", True, (0, 0, 0))
        screen.blit(text1, text1.get_rect(center=one_rect.center))
        screen.blit(text2, text2.get_rect(center=two_rect.center))
        pygame.display.flip()
        pygame.time.wait(10)


def show_game_over(screen: pygame.Surface, board: Board, message: str,
                   font_large: pygame.font.Font,
                   font_small: pygame.font.Font, board_width: int,
                   middle_rect: pygame.Rect) -> None:
    """Display the end screen and wait for the player to go back to the menu."""
    button_rect = pygame.Rect(screen.get_width() // 2 - 80,
                              screen.get_height() - 80, 160, 50)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    return
        screen.fill((200, 200, 200))
        draw_next_tile(screen, "", font_large, board_width)
        draw_board(screen, board, font_large)
        draw_middle_text(screen, message, font_small, middle_rect)
        pygame.draw.rect(screen, (180, 180, 180), button_rect)
        pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)
        text = font_small.render("Main Menu", True, (0, 0, 0))
        screen.blit(text, text.get_rect(center=button_rect.center))
        pygame.display.flip()
        pygame.time.wait(10)


def run_game_visual(ai: Optional[bool] = None) -> None:
    pygame.init()
    board_width = GRID_SIZE * TILE_SIZE
    info_width = 300
    screen_height = AUCTION_HEIGHT + GRID_SIZE * TILE_SIZE + 2 * MARGIN
    screen = pygame.display.set_mode(
        (board_width + info_width + 3 * MARGIN, screen_height)
    )
    pygame.display.set_caption("Zoo Mahjong")
    font_large = pygame.font.SysFont(None, 48)
    font_small = pygame.font.SysFont(None, 24)

    global ANIMAL_IMAGES
    ANIMAL_IMAGES = {}
    for animal in ANIMALS:
        path = os.path.join("images", f"{animal.lower()}.png")
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(
                img, (TILE_SIZE - 10, TILE_SIZE - 10)
            )
            ANIMAL_IMAGES[animal] = img
        except pygame.error:
            pass

    top_rect = pygame.Rect(board_width + 2 * MARGIN, MARGIN, info_width, 150)
    bottom_rect = pygame.Rect(
        board_width + 2 * MARGIN, screen_height - 150 - MARGIN, info_width, 150
    )
    middle_height = bottom_rect.top - top_rect.bottom - MARGIN
    middle_rect = pygame.Rect(
        board_width + 2 * MARGIN, top_rect.bottom + MARGIN, info_width, middle_height
    )

    while True:
        if ai is None:
            ai_mode = select_ai_mode(screen, font_large)
            screen.fill((200, 200, 200))
            pygame.display.flip()
        else:
            ai_mode = ai
            ai = None

        board: Board = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        chips = {1: 10, 2: 10}
        seq = {1: random.sample(ANIMALS, 3), 2: random.sample(ANIMALS, 3)}
        cond = {}
        for player in (1, 2):
            more, less = random.sample(ANIMALS, 2)
            cond[player] = (more, less)

        current_round = 1
        last_winner = ""
        tile = None
        while any(None in row for row in board):
            tile = random.choice(ANIMALS)

            bids = {}
            for player in (1, 2):
                if ai_mode and player == 2:
                    bid = ai_bid(chips[player])
                else:
                    bid = get_bid_input(
                        screen,
                        board,
                        tile,
                        player,
                        chips,
                        seq,
                        cond,
                        font_large,
                        font_small,
                        board_width,
                        (top_rect, middle_rect, bottom_rect),
                        last_winner,
                    )
                bids[player] = bid

            if bids[1] == bids[2]:
                winner = random.choice([1, 2])
            else:
                winner = 1 if bids[1] > bids[2] else 2
            chips[winner] -= bids[winner]
            last_winner = f"Player {winner} won the bid"
            screen.fill((200, 200, 200))
            draw_next_tile(screen, tile, font_large, board_width)
            draw_board(screen, board, font_large)
            draw_middle_text(screen, last_winner, font_small, middle_rect)
            if not (ai_mode and winner == 2):
                panel_rect = top_rect if winner == 1 else bottom_rect
                draw_player_panel(
                    screen, winner, chips, seq, cond, font_small, panel_rect
                )
            pygame.display.flip()
            if ai_mode and winner == 2:
                r, c = choose_spot_ai(board)
            else:
                r, c = choose_spot_visual(board, board_width)
            board[r][c] = tile

            if check_sequence(board, seq[winner]) or check_condition(
                board, *cond[winner]
            ):
                show_game_over(
                    screen,
                    board,
                    f"Player {winner} wins!",
                    font_large,
                    font_small,
                    board_width,
                    middle_rect,
                )
                break

            current_round += 1
        else:
            show_game_over(
                screen,
                board,
                "It's a draw!",
                font_large,
                font_small,
                board_width,
                middle_rect,
            )


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1].lower() == "ai":
        run_game_visual(ai=True)
    else:
        run_game_visual(ai=None)
