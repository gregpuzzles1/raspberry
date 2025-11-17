import random
import pygame
import sys
from collections import deque

# === Game Settings ===
MAP_WIDTH, MAP_HEIGHT = 24, 17  # One less row to make space for the legend area
TILE_SIZE = 48
NUM_FOOD = 40
NUM_OBSTACLES = 24
MAX_ANTS = 30
SPAWN_INTERVAL = 3
WARRIOR_HP = 3
FORAGER_HP = 1
DAMAGE = 1
FPS = 6  # Slowed down by 5 times (original was 30)
MOVE_FRAMES = 6

# === Symbols ===
EMPTY, FOOD, OBSTACLE = '.', 'F', '#'
ALLY_COLONY, ENEMY_COLONY = 'C', 'X'
FORAGER, WARRIOR = 'F', 'W'

# === Colors ===
COLORS = {
    EMPTY: (240, 240, 240),
    FOOD: (0, 255, 0),  # Green for food
    OBSTACLE: (80, 80, 80),
    ALLY_COLONY: (0, 100, 255),
    ENEMY_COLONY: (255, 50, 50),
    FORAGER: (255, 0, 0),
    WARRIOR: (0, 0, 255)
}

# === Initialize pygame ===
pygame.init()
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, (MAP_HEIGHT + 1) * TILE_SIZE + 60))
pygame.display.set_caption("Ant Bot Simulation")
font = pygame.font.SysFont(None, 28)
clock = pygame.time.Clock()

# === Game State ===
def initialize_game():
    global grid, food_positions, obstacles, allies, enemies, ally_colony, enemy_colony
    global ally_score, enemy_score, ally_food_bank, enemy_food_bank
    grid = [[EMPTY for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    food_positions = []
    obstacles = set()
    allies = []
    enemies = []
    ally_colony = enemy_colony = None
    ally_score = {'food': 0, 'kills': 0}
    enemy_score = {'food': 0, 'kills': 0}
    ally_food_bank = enemy_food_bank = 0
    obstacles.update(place_random(OBSTACLE, NUM_OBSTACLES, []))
    food_positions.extend(place_random(FOOD, NUM_FOOD, obstacles))
    ally_colony = place_random(ALLY_COLONY, 1, food_positions + list(obstacles))[0]
    enemy_colony = place_random(ENEMY_COLONY, 1, food_positions + list(obstacles) + [ally_colony])[0]
    spawn_ant(*ally_colony, allies, FORAGER)
    spawn_ant(*enemy_colony, enemies, FORAGER)

# === Functions ===
def place_random(symbol, count, avoid):
    positions = []
    while len(positions) < count:
        x, y = random.randint(0, MAP_WIDTH - 1), random.randint(0, MAP_HEIGHT - 1)
        if grid[y][x] == EMPTY and (x, y) not in avoid:
            grid[y][x] = symbol
            positions.append((x, y))
    return positions

def spawn_ant(x, y, team_list, ant_type):
    hp = WARRIOR_HP if ant_type == WARRIOR else FORAGER_HP
    team_list.append({'x': x, 'y': y, 'type': ant_type, 'hp': hp, 'tx': x, 'ty': y, 'fx': 0, 'fy': 0})
    grid[y][x] = ant_type

def bfs(start, targets):
    if not targets:  # Early exit if no targets
        return None
    if start in targets:  # Already at target
        return start
    
    visited = set()
    queue = deque([(start, [])])
    
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        
        # Check neighbors first before adding to queue
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in targets:  # Found target - return immediately
                return path[0] if path else (nx, ny)
            
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                if grid[ny][nx] in [EMPTY, FOOD] and (nx, ny) not in visited:
                    queue.append(((nx, ny), path + [(nx, ny)]))
    
    return None

def attack(ant, enemy_team, team_score):
    x, y = ant['x'], ant['y']
    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
        nx, ny = x + dx, y + dy
        for enemy in enemy_team:
            if enemy['x'] == nx and enemy['y'] == ny:
                enemy['hp'] -= DAMAGE
                if enemy['hp'] <= 0:
                    enemy_team.remove(enemy)
                    grid[ny][nx] = EMPTY
                    team_score['kills'] += 1
                return

def move_ant(ant, team, enemy_team, team_score, symbol):
    global ally_food_bank, enemy_food_bank
    
    if ant['type'] == WARRIOR:
        attack(ant, enemy_team, team_score)
        enemy_positions = {(e['x'], e['y']) for e in enemy_team}
        if not enemy_positions:  # No enemies to target
            return
        target = bfs((ant['x'], ant['y']), enemy_positions)
    else:
        if not food_positions:  # No food available
            return
        target = bfs((ant['x'], ant['y']), set(food_positions))
    
    if not target:
        return
    
    nx, ny = target
    if grid[ny][nx] not in [EMPTY, FOOD]:
        return
    
    # Update grid
    current_pos = (ant['x'], ant['y'])
    grid[ant['y']][ant['x']] = EMPTY if current_pos not in [ally_colony, enemy_colony] else symbol
    
    if grid[ny][nx] == FOOD and ant['type'] == FORAGER:
        if (nx, ny) in food_positions:
            food_positions.remove((nx, ny))
            team_score['food'] += 1
            if symbol == 'C':
                ally_food_bank += 1
            else:
                enemy_food_bank += 1
    
    ant['tx'], ant['ty'] = nx, ny
    ant['fx'] = (nx - ant['x']) * TILE_SIZE / MOVE_FRAMES
    ant['fy'] = (ny - ant['y']) * TILE_SIZE / MOVE_FRAMES

def try_spawn(colony, team_list, food_bank, symbol):
    if food_bank <= 0 or len(team_list) >= MAX_ANTS:
        return food_bank
    x, y = colony
    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT and grid[ny][nx] == EMPTY:
            ant_type = FORAGER if random.random() < 0.6 else WARRIOR
            spawn_ant(nx, ny, team_list, ant_type)
            return food_bank - 1
    return food_bank

def draw_grid():
    screen.fill((180, 180, 180))
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            rect = pygame.Rect(x * TILE_SIZE, (y + 1) * TILE_SIZE + 12, TILE_SIZE, TILE_SIZE)
            symbol = grid[y][x]
            color = COLORS.get(symbol, (0, 0, 0))
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (100, 100, 100), rect, 1)
            if (x, y) in food_positions:
                center = rect.center
                pygame.draw.circle(screen, COLORS[FOOD], center, 8)

def draw_ants(team, color):
    for ant in team:
        base_x = ant['x'] * TILE_SIZE
        base_y = (ant['y'] + 1) * TILE_SIZE + 12
        if ant['fx'] != 0 or ant['fy'] != 0:
            base_x += ant['fx']
            base_y += ant['fy']
        rect = pygame.Rect(base_x + 12, base_y + 12, 24, 24)
        pygame.draw.ellipse(screen, color, rect)
        if ant['type'] == WARRIOR:
            hp_ratio = ant['hp'] / WARRIOR_HP
            pygame.draw.rect(screen, (255, 0, 0), (base_x + 10, base_y + 6, int(28 * hp_ratio), 4))

def draw_labels(game_over):
    text1 = font.render(f"Allies - Food: {ally_score['food']} | Kills: {ally_score['kills']} | Bank: {ally_food_bank}", True, (0, 0, 0))
    text2 = font.render(f"Enemies - Food: {enemy_score['food']} | Kills: {enemy_score['kills']} | Bank: {enemy_food_bank}", True, (0, 0, 0))
    legend1 = font.render("Legend:", True, (0, 0, 0))
    legend2 = font.render("Green=Food  Red=Forager  Blue=Warrior  Gray=Obstacle", True, (0, 0, 0))
    screen.blit(text1, (10, 5))
    screen.blit(text2, (10, 30))
    screen.blit(legend1, (400, 5))
    screen.blit(legend2, (400, 30))
    if game_over:
        over_text = font.render("Game Over - Close Window to Exit", True, (0, 0, 0))
        screen.blit(over_text, (10, (MAP_HEIGHT + 1) * TILE_SIZE + 10))

def safe_exit():
    pygame.quit()
    sys.exit()

# === Main Simulation ===
initialize_game()
turn = 1
running = True
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        if turn % MOVE_FRAMES == 1:
            for ant in list(allies):
                move_ant(ant, allies, enemies, ally_score, 'C')
            for ant in list(enemies):
                move_ant(ant, enemies, allies, enemy_score, 'X')
            if turn // MOVE_FRAMES % SPAWN_INTERVAL == 0:
                ally_food_bank = try_spawn(ally_colony, allies, ally_food_bank, 'C')
                enemy_food_bank = try_spawn(enemy_colony, enemies, enemy_food_bank, 'X')
            for ant in allies + enemies:
                ant['x'], ant['y'] = ant['tx'], ant['ty']
                ant['fx'] = ant['fy'] = 0
        if not food_positions:
            game_over = True
        turn += 1

    draw_grid()
    draw_ants(allies, COLORS[FORAGER])
    draw_ants(enemies, COLORS[WARRIOR])
    draw_labels(game_over)
    pygame.display.flip()
    clock.tick(FPS)

safe_exit()
