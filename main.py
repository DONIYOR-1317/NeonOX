import pygame
import sys
import random

# 1. Sozlamalar
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Ranglar
BG_COLOR = (15, 15, 25)
LINE_COLOR = (40, 40, 70)
X_COLOR = (255, 0, 127)
O_COLOR = (0, 255, 240)
TEXT_COLOR = (255, 255, 255)

BOARD_SIZE = int(WIDTH * 0.85)
SQUARE_SIZE = BOARD_SIZE // 3
OFFSET_X = (WIDTH - BOARD_SIZE) // 2
OFFSET_Y = (HEIGHT - BOARD_SIZE) // 2

font_big = pygame.font.SysFont('Arial', int(WIDTH * 0.1), bold=True)
font_med = pygame.font.SysFont('Arial', int(WIDTH * 0.06), bold=True)

# O'yin holati
board = [[None]*3 for _ in range(3)]
player = 'X'
game_over = False
winner = None
game_mode = "PvP"
difficulty = 1
game_state = "MAIN_MENU"

# --- ICONS ---
def draw_players_icon(x, y):
    # Birinchi o'yinchi
    pygame.draw.circle(screen, TEXT_COLOR, (x + 20, y + 30), 10)
    pygame.draw.rect(screen, TEXT_COLOR, (x + 10, y + 42, 20, 20), border_radius=5)
    # Ikkinchi o'yinchi (biroz orqaroqda va yonida)
    pygame.draw.circle(screen, (200, 200, 200), (x + 45, y + 30), 10)
    pygame.draw.rect(screen, (200, 200, 200), (x + 35, y + 42, 20, 20), border_radius=5)

def draw_robot_icon(x, y):
    pygame.draw.rect(screen, O_COLOR, (x + 20, y + 25, 30, 25), border_radius=3) # Bosh
    pygame.draw.rect(screen, O_COLOR, (x + 25, y + 20, 20, 5)) # Antenna
    pygame.draw.circle(screen, BG_COLOR, (x + 28, y + 35), 4) # Ko'z
    pygame.draw.circle(screen, BG_COLOR, (x + 42, y + 35), 4) # Ko'z

# --- BOT LOGIKASI ---
def check_winner(b):
    for r in range(3):
        if b[r][0] == b[r][1] == b[r][2] and b[r][0] is not None: return b[r][0]
    for c in range(3):
        if b[0][c] == b[1][c] == b[2][c] and b[0][c] is not None: return b[0][c]
    if b[0][0] == b[1][1] == b[2][2] and b[0][0] is not None: return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] and b[0][2] is not None: return b[0][2]
    if all(all(row) for row in b): return "Tie"
    return None

def minimax(b, depth, is_maximizing):
    res = check_winner(b)
    if res == 'O': return 1
    if res == 'X': return -1
    if res == "Tie": return 0
    if is_maximizing:
        best = -float('inf')
        for r in range(3):
            for c in range(3):
                if b[r][c] is None:
                    b[r][c] = 'O'; v = minimax(b, depth+1, False); b[r][c] = None
                    best = max(v, best)
        return best
    else:
        best = float('inf')
        for r in range(3):
            for c in range(3):
                if b[r][c] is None:
                    b[r][c] = 'X'; v = minimax(b, depth+1, True); b[r][c] = None
                    best = min(v, best)
        return best

def bot_move():
    empty = [(r, c) for r in range(3) for c in range(3) if board[r][c] is None]
    
    # 1. OSON DARAJA (Faqat random)
    if difficulty == 0:
        return random.choice(empty) if empty else None
    
    # 2. O'RTACHA DARAJA (Ba'zida yutishni ko'radi, ba'zida xato qiladi)
    if difficulty == 1:
        if random.random() < 0.4: # 40% ehtimol bilan random yuradi
            return random.choice(empty)
    
    # 3. YENGILMAS (Minimax)
    best_s = -float('inf'); move = None
    for r in range(3):
        for c in range(3):
            if board[r][c] is None:
                board[r][c] = 'O'; s = minimax(board, 0, False); board[r][c] = None
                if s > best_s: best_s = s; move = (r, c)
    return move

# --- MENYU ---
def draw_button(text, y_pos, icon_type=None):
    rect = pygame.Rect(WIDTH//2 - 250, y_pos, 500, 100)
    pygame.draw.rect(screen, (40, 40, 70), rect, border_radius=15)
    txt_surf = font_med.render(text, True, TEXT_COLOR)
    screen.blit(txt_surf, (WIDTH//2 - txt_surf.get_width()//2 + 40, y_pos + 25))
    if icon_type == "players": draw_players_icon(WIDTH//2 - 230, y_pos + 15)
    elif icon_type == "robot": draw_robot_icon(WIDTH//2 - 230, y_pos + 15)
    return rect

def restart():
    global board, player, game_over, winner
    board = [[None]*3 for _ in range(3)]
    player = 'X'; game_over = False; winner = None

# --- ASOSIY SIKL ---
while True:
    screen.fill(BG_COLOR)
    if game_state == "MAIN_MENU":
        title = font_big.render("NEON X-O", True, O_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//5))
        start_btn = draw_button("BOSHLASH", HEIGHT//2)
    elif game_state == "MODE_MENU":
        pvp_btn = draw_button("2 O'YINCHI", HEIGHT//2 - 80, "players")
        pve_btn = draw_button("BOT BILAN", HEIGHT//2 + 60, "robot")
    elif game_state == "DIFF_MENU":
        d0 = draw_button("OSON", HEIGHT//2 - 120)
        d1 = draw_button("QIYIN (O'RTA)", HEIGHT//2)
        d2 = draw_button("YENGILMAS", HEIGHT//2 + 120)
    elif game_state == "PLAYING":
        # Doska
        for i in range(1, 3):
            pygame.draw.line(screen, LINE_COLOR, (OFFSET_X, OFFSET_Y + i*SQUARE_SIZE), (OFFSET_X+BOARD_SIZE, OFFSET_Y + i*SQUARE_SIZE), 8)
            pygame.draw.line(screen, LINE_COLOR, (OFFSET_X + i*SQUARE_SIZE, OFFSET_Y), (OFFSET_X+i*SQUARE_SIZE, OFFSET_Y+BOARD_SIZE), 8)
        # Figuralar
        for r in range(3):
            for c in range(3):
                cx, cy = OFFSET_X + c*SQUARE_SIZE + SQUARE_SIZE//2, OFFSET_Y + r*SQUARE_SIZE + SQUARE_SIZE//2
                if board[r][c] == 'O': pygame.draw.circle(screen, O_COLOR, (cx, cy), SQUARE_SIZE//3, 10)
                if board[r][c] == 'X':
                    s = SQUARE_SIZE//4
                    pygame.draw.line(screen, X_COLOR, (cx-s, cy-s), (cx+s, cy+s), 15); pygame.draw.line(screen, X_COLOR, (cx+s, cy-s), (cx-s, cy+s), 15)
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 200)); screen.blit(overlay, (0,0))
            msg = font_big.render("DURANG!" if winner == "Tie" else f"G'OLIB: {winner}", True, TEXT_COLOR)
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//3))
            menu_btn = draw_button("MENUGA QAYTISH", HEIGHT//2)

        if not game_over and game_mode == "PvE" and player == 'O':
            m = bot_move()
            if m:
                board[m[0]][m[1]] = 'O'
                res = check_winner(board)
                if res: game_over = True; winner = res
                player = 'X'

    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if game_state == "MAIN_MENU" and start_btn.collidepoint(pos): game_state = "MODE_MENU"
            elif game_state == "MODE_MENU":
                if pvp_btn.collidepoint(pos): game_mode = "PvP"; game_state = "PLAYING"; restart()
                if pve_btn.collidepoint(pos): game_mode = "PvE"; game_state = "DIFF_MENU"
            elif game_state == "DIFF_MENU":
                if d0.collidepoint(pos): difficulty = 0; game_state = "PLAYING"; restart()
                if d1.collidepoint(pos): difficulty = 1; game_state = "PLAYING"; restart()
                if d2.collidepoint(pos): difficulty = 2; game_state = "PLAYING"; restart()
            elif game_state == "PLAYING":
                if game_over and menu_btn.collidepoint(pos): game_state = "MAIN_MENU"
                elif not game_over and (player == 'X' or game_mode == "PvP"):
                    if OFFSET_X < pos[0] < OFFSET_X + BOARD_SIZE and OFFSET_Y < pos[1] < OFFSET_Y + BOARD_SIZE:
                        c, r = (pos[0]-OFFSET_X)//SQUARE_SIZE, (pos[1]-OFFSET_Y)//SQUARE_SIZE
                        if board[r][c] is None:
                            board[r][c] = player
                            res = check_winner(board)
                            if res: game_over = True; winner = res
                            player = 'O' if player == 'X' else 'X'
    pygame.display.update()
