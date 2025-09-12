import pygame
import sys
import time
from collections import deque

# Initialize pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Load beep sound
BEEP = pygame.mixer.Sound("beep.wav")

# Screen setup
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
ROWS = HEIGHT // TILE_SIZE
COLS = WIDTH // TILE_SIZE

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wheelchair Navigation - Alert Mode")

# Load wheelchair image AFTER TILE_SIZE exists
wheelchair_img = pygame.image.load("wheelchair.png")
wheelchair_img = pygame.transform.scale(wheelchair_img, (TILE_SIZE, TILE_SIZE))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHTBLUE = (173, 216, 230)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Fonts
FONT = pygame.font.SysFont(None, 20)
BIG_FONT = pygame.font.SysFont(None, 32)

# Hospital map (0=free, 1=wall)
hospital_map = [
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,1,1,1,1,0,0,1,1,1,0,0,1,1,1,1,1,1,1,1],
    [0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,1,1,1,1],
    [0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
    [0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
    [0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1],
    [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1],
    [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1],
    [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1],
    [0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1],
    [0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
    [0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
    [0,1,1,1,1,0,1,1,1,1,1,1,1,1,0,0,1,1,1,1],
    [0,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

grid = [row[:] for row in hospital_map]

# Room coordinates
room_coords = {
    "ICU": (5, 1),
    "Doctor's Room": (11, 1),
    "Restroom": (18, 6),
    "Pharmacy": (14, 12),
    "Patient's Room": (4, 13),
    "Nurses Room": (6, 13)
}
room_labels = {
    "ICU": (5, 1),
    "Doctor's Room": (11, 1),
    "Restroom": (18, 6),
    "Pharmacy": (14, 12),
    "Patient's Room": (1, 13),
    "Nurses Room": (6, 13)
}

wheel_x, wheel_y = 0, 0

# Define corridor path
trashbin_path = set()
for y in range(ROWS):
    for x in range(COLS):
        if hospital_map[y][x] == 0:
            trashbin_path.add((x, y))

def bfs(start, goal):
    queue = deque([start])
    visited = {start: None}
    while queue:
        cur = queue.popleft()
        if cur == goal:
            break
        x, y = cur
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                if (nx, ny) in trashbin_path and grid[ny][nx] != 2 and (nx, ny) not in visited:
                    visited[(nx, ny)] = cur
                    queue.append((nx, ny))
    if goal not in visited:
        return []
    path = []
    cur = goal
    while cur:
        path.append(cur)
        cur = visited[cur]
    return path[::-1]

def draw_window(path, alert=False, blink=False):
    WIN.fill(WHITE)

    # Draw walls
    for row in range(ROWS):
        for col in range(COLS):
            if hospital_map[row][col] == 1:
                pygame.draw.rect(WIN, BLACK, (col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Draw corridor
    for (gx, gy) in trashbin_path:
        pygame.draw.rect(WIN, GRAY, (gx*TILE_SIZE, gy*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Draw path
    for (px, py) in path:
        pygame.draw.rect(WIN, LIGHTBLUE, (px*TILE_SIZE, py*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Draw obstacles
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] == 2:
                pygame.draw.rect(WIN, YELLOW, (col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Draw wheelchair
    WIN.blit(wheelchair_img, (wheel_x*TILE_SIZE, wheel_y*TILE_SIZE))

    # Draw alert blink
    if alert and blink:
        cx, cy = wheel_x*TILE_SIZE + TILE_SIZE//2, wheel_y*TILE_SIZE
        pygame.draw.circle(WIN, RED, (cx, cy-10), 10)

    # Draw room labels (centered above tiles)
    for room, (rx, ry) in room_labels.items():
        label = FONT.render(room, True, LIGHTBLUE)
        label_rect = label.get_rect()
        label_rect.centerx = rx*TILE_SIZE + TILE_SIZE//2
        label_rect.bottom = ry*TILE_SIZE - 2
        WIN.blit(label, label_rect)

    pygame.display.update()

def get_room_name_input():
    input_box = pygame.Rect(50, HEIGHT-80, 300, 32)
    color = GRAY
    text = ''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: return text.strip()
                elif event.key == pygame.K_BACKSPACE: text = text[:-1]
                else: text += event.unicode

        WIN.fill(WHITE)
        prompt = BIG_FONT.render("Enter destination room name:", True, BLACK)
        WIN.blit(prompt, (50, HEIGHT-120))
        txt_surface = BIG_FONT.render(text, True, BLACK)
        input_box.w = max(300, txt_surface.get_width()+10)
        WIN.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(WIN, color, input_box, 2)
        rooms_surface = FONT.render("Rooms: " + " | ".join(room_coords.keys()), True, BLACK)
        WIN.blit(rooms_surface, (50, HEIGHT-40))
        pygame.display.flip()

def popup_message(text, color=BLACK):
    overlay = BIG_FONT.render(text, True, color)
    WIN.blit(overlay, (WIDTH//2 - overlay.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    pygame.time.wait(2500)

def main():
    global wheel_x, wheel_y
    room_name = None
    while room_name not in room_coords:
        room_name = get_room_name_input()

    dest_x, dest_y = room_coords[room_name]
    path = bfs((wheel_x, wheel_y), (dest_x, dest_y))

    clock = pygame.time.Clock()
    running = True
    step_index = 0
    alert_mode = False
    alert_start = None

    while running:
        clock.tick(5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx//TILE_SIZE, my//TILE_SIZE
                if (gx, gy) in trashbin_path:
                    grid[gy][gx] = 0 if grid[gy][gx] == 2 else 2

        if step_index < len(path):
            # Look 2 steps ahead
            if step_index+2 < len(path):
                ahead_x, ahead_y = path[step_index+2]
                if grid[ahead_y][ahead_x] == 2:
                    if not alert_mode:
                        alert_mode = True
                        alert_start = time.time()
                        BEEP.play(-1)  # loop beep

                    if alert_mode:
                        blink = int((time.time()*2) % 2) == 0
                        draw_window(path, alert=True, blink=blink)

                        if time.time() - alert_start > 5:
                            path = bfs((wheel_x, wheel_y), (dest_x, dest_y))
                            step_index = 0
                            alert_mode = False
                            BEEP.stop()
                            if not path:  # 🚫 trapped
                                popup_message("The Wheelchair is Trapped", RED)
                                running = False
                    continue

            alert_mode = False
            BEEP.stop()
            next_x, next_y = path[step_index]
            if grid[next_y][next_x] != 2:
                wheel_x, wheel_y = next_x, next_y
                step_index += 1

        draw_window(path)

        if step_index >= len(path) and path:
            popup_message(f"Wheelchair reached {room_name}", GREEN)
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
