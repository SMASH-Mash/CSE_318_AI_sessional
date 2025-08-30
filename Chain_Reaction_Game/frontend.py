import pygame
import sys
import math
import random
from backend import Board, HEURISTICS, minimax

ROWS, COLS = 9, 6
CELL_SIZE = 80
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE
PLAYER_COLORS = [(200, 0, 0), (0, 120, 255)]

def random_move(board, player):
    moves = board.get_valid_moves(player)
    if moves:
        return random.choice(moves)
    return None

def draw_board(screen, board):
    for y in range(HEIGHT):
        color_val = 30 + int(40 * math.sin(y / 60))
        color_val = max(0, min(255, color_val))
        blue_val = min(255, max(0, 60 + color_val // 2))
        pygame.draw.line(screen, (color_val, color_val, blue_val), (0, y), (WIDTH, y))
    for r in range(board.rows + 1):
        glow = 120 + int(40 * abs(math.sin(r)))
        glow = min(255, max(0, glow))
        pygame.draw.line(screen, (glow, glow, 180), (0, r * CELL_SIZE), (WIDTH, r * CELL_SIZE), 4)
    for c in range(board.cols + 1):
        glow = 120 + int(40 * abs(math.cos(c)))
        glow = min(255, max(0, glow))
        pygame.draw.line(screen, (glow, glow, 180), (c * CELL_SIZE, 0), (c * CELL_SIZE, HEIGHT), 4)
    for r in range(board.rows):
        for c in range(board.cols):
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            cell = board.grid[r][c]
            if (r + c) % 2 == 0:
                pygame.draw.rect(screen, (40, 60, 80), (x+2, y+2, CELL_SIZE-4, CELL_SIZE-4), border_radius=18)
            if cell.owner is not None and cell.count > 0:
                color = PLAYER_COLORS[cell.owner]
                for i in range(cell.count):
                    offset = (i - (cell.count-1)/2) * 18
                    orb_x = int(x + CELL_SIZE/2 + offset)
                    orb_y = int(y + CELL_SIZE/2)
                    pygame.draw.circle(screen, (30, 30, 30), (orb_x+4, orb_y+4), 18)
                    for glow_radius in range(22, 30, 2):
                        glow_color = (
                            min(color[0]+60,255),
                            min(color[1]+60,255),
                            min(color[2]+60,255),
                        )
                        pygame.draw.circle(screen, glow_color, (orb_x, orb_y), glow_radius, 2)
                    pygame.draw.circle(screen, color, (orb_x, orb_y), 18)
                    pygame.draw.circle(screen, (255,255,255), (orb_x-6, orb_y-6), 5)
    pygame.display.flip()

def get_cell_from_mouse(pos):
    mx, my = pos
    row = my // CELL_SIZE
    col = mx // CELL_SIZE
    return row, col

def draw_button(screen, rect, text, selected=False, color=None, anim=0):
    base_color = color if color else (180, 180, 180)
    if selected:
        pulse = int(40 * abs(math.sin(anim)))
        color = (min(base_color[0]+pulse,255), min(base_color[1]+pulse,255), min(base_color[2]+pulse,255))
        border_color = (60, 180, 60)
    else:
        color = base_color
        border_color = (100, 100, 100)
    pygame.draw.rect(screen, color, rect, border_radius=14)
    pygame.draw.rect(screen, border_color, rect, 4, border_radius=14)
    font = pygame.font.SysFont("arial", 36, bold=True)
    txt = font.render(text, True, (30, 30, 30))
    text_rect = txt.get_rect(center=rect.center)
    screen.blit(txt, text_rect)

def menu():
    pygame.init()
    screen = pygame.display.set_mode((700, 700))
    pygame.display.set_caption("Chain Reaction - Menu")
    clock = pygame.time.Clock()
    mode_colors = [(255, 200, 200), (200, 220, 255), (255, 255, 200)]
    depth_colors = [(255, 255, 200), (220, 255, 220), (200, 255, 255), (255, 220, 255), (255, 230, 200), (220, 220, 255)]
    heuristic_colors = [
        (255, 230, 230), (230, 255, 230), (230, 230, 255), (255, 255, 230), (230, 255, 255)
    ]
    game_modes = ["Human vs AI", "AI vs AI", "Random vs AI"]
    heuristics = [
        "Simple", "Cell Control", "Edge Priority", "Critical Mass", "Aggressive"
    ]
    ai_depths = [1, 2, 3, 4, 5, 6]
    selected_mode = 0
    selected_heuristic = 0
    selected_heuristic2 = 0
    selected_depth = 2
    anim = 0
    running = True
    while running:
        anim += 0.07
        screen.fill((245, 255, 245))
        font_title = pygame.font.SysFont("arial", 48, bold=True)
        font_label = pygame.font.SysFont("arial", 30, bold=True)
        for y in range(0, screen.get_height(), 4):
            color_val = 245 + int(10 * math.sin(anim + y/60))
            pygame.draw.rect(screen, (color_val, 255, 245), (0, y, screen.get_width(), 4))
        title = font_title.render("Chain Reaction", True, (0, 100, 0))
        shadow = font_title.render("Chain Reaction", True, (180, 255, 180))
        screen.blit(shadow, (screen.get_width()//2 - title.get_width()//2 + 4, 24 + int(2*math.sin(anim))))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 20))
        screen.blit(font_label.render("Select Game Mode", True, (0,0,0)), (40, 80))
        for i, mode in enumerate(game_modes):
            draw_button(
                screen,
                pygame.Rect(2 + i*232, 120, 232, 50),
                mode,
                selected_mode == i,
                color=mode_colors[i],
                anim=anim
            )
        screen.blit(font_label.render("Select AI Depth", True, (0,0,0)), (40, 190))
        for i, d in enumerate(ai_depths):
            draw_button(
                screen,
                pygame.Rect(40 + i*90, 230, 70, 45),
                str(d),
                selected_depth == d,
                color=depth_colors[i],
                anim=anim
            )
        # Heuristic(s)
        if selected_mode == 0 or selected_mode == 2:
            screen.blit(font_label.render("Select Heuristic", True, (0,0,0)), (40, 290))
            for i, h in enumerate(heuristics):
                draw_button(
                    screen,
                    pygame.Rect(40, 330 + i*50, 600, 45),
                    f"{i+1}: {h}",
                    selected_heuristic == i,
                    color=heuristic_colors[i],
                    anim=anim
                )
            start_y = 630
        elif selected_mode == 1:
            screen.blit(font_label.render("Select Heuristic (AI 1)", True, (0,0,0)), (40, 290))
            for i, h in enumerate(heuristics):
                draw_button(
                    screen,
                    pygame.Rect(40, 330 + i*40, 290, 35),
                    f"{i+1}: {h}",
                    selected_heuristic == i,
                    color=heuristic_colors[i],
                    anim=anim
                )
            screen.blit(font_label.render("Select Heuristic (AI 2)", True, (0,0,0)), (350, 290))
            for i, h in enumerate(heuristics):
                draw_button(
                    screen,
                    pygame.Rect(350, 330 + i*40, 290, 35),
                    f"{i+1}: {h}",
                    selected_heuristic2 == i,
                    color=heuristic_colors[i],
                    anim=anim
                )
            start_y = 530
        start_color = (200 + int(30*abs(math.sin(anim))), 255, 200 + int(30*abs(math.cos(anim))))
        draw_button(screen, pygame.Rect(200, start_y, 300, 50), "Start Game", False, color=start_color, anim=anim)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i in range(len(game_modes)):
                    if pygame.Rect(40 + i*210, 120, 200, 50).collidepoint(mx, my):
                        selected_mode = i
                for i, d in enumerate(ai_depths):
                    if pygame.Rect(40 + i*90, 230, 70, 45).collidepoint(mx, my):
                        selected_depth = d
                if selected_mode == 0 or selected_mode == 2:
                    for i in range(len(heuristics)):
                        if pygame.Rect(40, 330 + i*50, 600, 45).collidepoint(mx, my):
                            selected_heuristic = i
                    if pygame.Rect(200, 630, 300, 50).collidepoint(mx, my):
                        running = False
                elif selected_mode == 1:
                    for i in range(len(heuristics)):
                        if pygame.Rect(40, 330 + i*40, 290, 35).collidepoint(mx, my):
                            selected_heuristic = i
                        if pygame.Rect(350, 330 + i*40, 290, 35).collidepoint(mx, my):
                            selected_heuristic2 = i
                    if pygame.Rect(200, 530, 300, 50).collidepoint(mx, my):
                        running = False
        clock.tick(60)
    if selected_mode == 0 or selected_mode == 2:
        return selected_mode+1, selected_depth, selected_heuristic+1, selected_heuristic+1
    else:
        return selected_mode+1, selected_depth, selected_heuristic+1, selected_heuristic2+1

def board_to_file(board, move_type): 
    with open("gamestate.txt", "w") as f:
        f.write(f"{move_type}:\n")
        for r in range(ROWS):
            row = []
            for c in range(COLS):
                cell = board.grid[r][c]
                if cell.owner is None or cell.count == 0:
                    row.append("0")
                else:
                    color = "R" if cell.owner == 0 else "B"
                    row.append(f"{cell.count}{color}")
            f.write(" ".join(row) + "\n")
def file_to_board(filename):
    board = Board()
    with open(filename, "r") as f:
        lines = f.readlines()
        for r in range(ROWS):
            if r < len(lines) - 1:
                row_data = lines[r+1].strip().split()
                for c in range(COLS):
                    cell_data = row_data[c]
                    if cell_data == "0":
                        continue
                    count = int(cell_data[0])
                    owner = 0 if cell_data[-1] == 'R' else 1
                    board.grid[r][c].owner = owner
                    board.grid[r][c].count = count
        current_player = 0
        if lines[0].strip().startswith("AI"):
            current_player = 0
        else:
            current_player = 1    
    return board, current_player
def main(game_mode=1, ai_depth=3, heuristic1=1, heuristic2=1):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chain Reaction AI")
    clock = pygame.time.Clock()
    board = Board()
    running = True
    current_player = 0
    i = 0
    heuristic_func1 = HEURISTICS.get(heuristic1, HEURISTICS[1])
    heuristic_func2 = HEURISTICS.get(heuristic2, HEURISTICS[1])
    draw_board(screen, board)
    board_to_file(board, "Initial State")
    while running:
        if game_mode == 1 :
            board, current_player=file_to_board("gamestate.txt")
            draw_board(screen, board)
        if i==0:
            current_player = 0
        if i>1 and board.is_game_over():
            winner = board.get_winner()
            font = pygame.font.SysFont(None, 60)
            vic_msg = " wins"
            if game_mode == 1:
                if winner == 0:
                    vic_msg = "Human"+vic_msg
                elif winner == 1:
                    vic_msg = "AI"+vic_msg
            elif game_mode == 2:
                vic_msg = "AI-1"+vic_msg if winner == 0 else "AI-2"+vic_msg
            elif game_mode == 3:
                vic_msg = "Random"+vic_msg if winner == 0 else "AI"+vic_msg
            text = font.render(vic_msg, True, (250, 220, 255))
            screen.blit(text, (WIDTH//2-150, HEIGHT//2-30))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False
            continue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if game_mode==1 and current_player == 0 and event.type == pygame.MOUSEBUTTONDOWN:
                i+=1
                row, col = get_cell_from_mouse(event.pos)
                if 0 <= row < ROWS and 0 <= col < COLS and board.is_valid_move(row, col, current_player):
                    board.apply_move(row, col, current_player)
                    draw_board(screen, board)
                    board_to_file(board, "Human Move")
                    current_player = 1
        # AI vs AI
        if game_mode==2 and current_player == 0 and running and(i==0 or not board.is_game_over() ):
            i += 1
            _, move = minimax(board, ai_depth, -math.inf, math.inf, False, 1, 0, i, heuristic_func1)
            if move:
                board.apply_move(*move, current_player)
                board_to_file(board, "AI-1 Move")
            current_player = 1
            draw_board(screen, board)
        if game_mode==2 and current_player == 1 and running and(i==1 or not board.is_game_over()):
            _, move = minimax(board, ai_depth, -math.inf, math.inf, True, 1, 0, i, heuristic_func2)
            if move:
                board.apply_move(*move, current_player)
                board_to_file(board, "AI-2 Move")
            current_player = 0
            draw_board(screen, board)
        # Human vs AI
        if game_mode==1 and current_player == 1 and running and(i==1 or not board.is_game_over()):
            _, move = minimax(board, ai_depth, -math.inf, math.inf, True, 1, 0, i, heuristic_func1)
            if move:
                board.apply_move(*move, current_player)
                board_to_file(board, "AI Move")
            current_player = 0
            draw_board(screen, board)
        # Random move vs AI
        if game_mode==3 and current_player == 0 and running and (i==0 or not board.is_game_over()):
            i += 1
            move = random_move(board, 0)
            if move:
                board.apply_move(*move, current_player)
                board_to_file(board, "Random Move")
            current_player = 1
            draw_board(screen, board)
        if game_mode==3 and current_player == 1 and running and (i==1 or not board.is_game_over()):
            _, move = minimax(board, ai_depth, -math.inf, math.inf, True, 1, 0, i, heuristic_func1)
            if move:
                board.apply_move(*move, current_player)
                board_to_file(board, "AI Move")
            current_player = 0
            draw_board(screen, board)
        clock.tick(30)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    a, b, h1, h2 = menu()
    main(a, b, h1, h2)
