import pygame
import sys
import random
import tkinter
from tkinter import simpledialog
import os
import json

# Константы
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 30
MOVE_SPEED = 5
JUMP_SPEED = -10
GRAVITY = 0.5
FPS = 60
TILE_SIZE = 40
MIN_PLATFORM_SIZE = 40
NUM_COINS = 3
COIN_SIZE = TILE_SIZE
FACE_SIZE = 12
SPIKE_SCALE = 0.5
# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BACKGROUND_COLOR = (100, 149, 237)
GRAY = (128, 128, 128)


BUTTON_COLOR = (50, 50, 100)  
BUTTON_HOVER_COLOR = (70, 70, 130) 
BUTTON_TEXT_COLOR = WHITE
BUTTON_BORDER_COLOR = (100, 100, 180)
BUTTON_BORDER_WIDTH = 2

#Кнопки 
BUTTON_WIDTH=150  
BUTTON_HEIGHT = 40 


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Toggle Game")
clock = pygame.time.Clock()


try:
    player_image = pygame.image.load("player.png")
    platform_image = pygame.image.load("platform.png")
    spike_image = pygame.image.load("spike.png")
    exit_image = pygame.image.load("exit.png")
    player_start_image = pygame.image.load("player_start.png")
    tree_image = pygame.image.load("tree.png")
    spike_image_2 = pygame.image.load("spike2.png")
    coin_image = pygame.image.load("coin.png")
    menu_background = pygame.image.load("menu_background.png")  
    game_background = pygame.image.load("game_background.jpg")
    default_face = pygame.image.load("face.png") 

except FileNotFoundError as e:
    print(f"Error: One or more image files not found: {e}")
    sys.exit()

player_image = pygame.transform.scale(player_image, (PLAYER_SIZE, PLAYER_SIZE))
platform_image = pygame.transform.scale(platform_image, (TILE_SIZE, TILE_SIZE))
spike_image = pygame.transform.scale(spike_image, (TILE_SIZE, TILE_SIZE))
exit_image = pygame.transform.scale(exit_image, (TILE_SIZE, TILE_SIZE))
player_start_image = pygame.transform.scale(player_start_image, (TILE_SIZE, TILE_SIZE))
tree_image = pygame.transform.scale(tree_image, (TILE_SIZE * 2, TILE_SIZE * 2))
spike_image_2 = pygame.transform.scale(spike_image_2, (TILE_SIZE, TILE_SIZE))
coin_image = pygame.transform.scale(coin_image, (COIN_SIZE, COIN_SIZE))
menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))
game_background = pygame.transform.scale(game_background, (WIDTH, HEIGHT))
default_face = pygame.transform.scale(default_face, (FACE_SIZE, FACE_SIZE))


font_path = "397-font_1.otf"
try:
    title_font = pygame.font.Font(font_path, 74)
    button_font = pygame.font.Font(font_path, 20)
    creator_font = pygame.font.Font(font_path, 12)
    editor_font = pygame.font.Font(font_path, 12)
    small_font = pygame.font.Font(font_path, 10)
except FileNotFoundError:
    print("Error: Font file not found. Using default font.")
    title_font = pygame.font.Font(None, 74)
    button_font = pygame.font.Font(None, 36)
    creator_font = pygame.font.Font(None, 24)
    editor_font = pygame.font.Font(None, 20)
    small_font = pygame.font.Font(None, 16)


def load_game_state():
    try:
        with open("game_state.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_game_state(game_state):
    with open("game_state.json", "w") as f:
        json.dump(game_state, f)


game_state_data = load_game_state()
current_points = game_state_data.get("current_points", 0)

class Player: 
    def __init__(self, x=WIDTH // 2, y=HEIGHT // 2): 
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.velocity_y = 0
        self.gravity_direction = 1
        self.is_jumping = False
        self.on_ground = False
        self.face = default_face

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= MOVE_SPEED
        if keys[pygame.K_d]:
            self.rect.x += MOVE_SPEED

    def jump(self):
        self.velocity_y = JUMP_SPEED * self.gravity_direction
        self.is_jumping = True
        self.on_ground = False

    def toggle_gravity(self):
        self.gravity_direction *= -1
        self.velocity_y = 0
        self.on_ground = False

    def update(self, platforms):
        self.velocity_y += GRAVITY * self.gravity_direction
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0 and self.gravity_direction == 1: 
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0 
                    self.on_ground = True 
                    self.is_jumping = False 
                elif self.velocity_y < 0 and self.gravity_direction == -1:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
                    self.on_ground = True
                    self.is_jumping = False

        self.rect.y += self.velocity_y

        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity_y = 0
            self.on_ground = True
            self.is_jumping = False
        elif self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0
            self.on_ground = True
            self.is_jumping = False

    def draw(self, screen):
        screen.blit(player_image, self.rect)

        face_x = self.rect.x + (PLAYER_SIZE - FACE_SIZE) // 2
        face_y = self.rect.y + (PLAYER_SIZE - FACE_SIZE) // 2
        screen.blit(self.face, (face_x, face_y))

    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def to_dict(self):
        return {'x': self.rect.x, 'y': self.rect.y}

    @staticmethod
    def from_dict(data):
        player = Player(data['x'], data['y'])
        return player



class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.transform.scale(platform_image, (width, height)) 

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def resize(self, new_width, new_height):
        self.rect.width = new_width
        self.rect.height = new_height
        self.image = pygame.transform.scale(platform_image, (new_width, new_height)) 

    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def to_dict(self):
        return {'x': self.rect.x, 'y': self.rect.y, 'width': self.rect.width, 'height': self.rect.height}

    @staticmethod
    def from_dict(data):
        return Platform(data['x'], data['y'], data['width'], data['height'])

class PlayerStart: 
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

    def draw(self, screen):
        screen.blit(player_start_image, self.rect)

    def to_dict(self):
        return {'x': self.rect.x, 'y': self.rect.y}

    @staticmethod
    def from_dict(data):
        return PlayerStart(data['x'], data['y'])

class Spike: 
    def __init__(self, x, y, type=1):
        self.width = int(TILE_SIZE * SPIKE_SCALE)
        self.height = int(TILE_SIZE * SPIKE_SCALE)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.type = type
        self.image = pygame.transform.scale(spike_image, (self.width, self.height))  
        self.image_2 = pygame.transform.scale(spike_image_2, (self.width, self.height))  

    def draw(self, screen):
        if self.type == 1:
            screen.blit(self.image, self.rect) 
        elif self.type == 2:
            screen.blit(self.image_2, self.rect)

    def to_dict(self):
        return {'x': self.rect.x, 'y': self.rect.y, 'type': self.type}

    @staticmethod
    def from_dict(data):
        return Spike(data['x'], data['y'], data['type'])

class Exit: 
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

    def draw(self, screen):
        screen.blit(exit_image, self.rect)

    def to_dict(self):
        return {'x': self.rect.x, 'y': self.rect.y}

    @staticmethod
    def from_dict(data):
        return Exit(data['x'], data['y'])

class Tree: 
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE * 2, TILE_SIZE * 2)

    def draw(self, screen):
        screen.blit(tree_image, self.rect)

    def to_dict(self):
        return {'x': self.rect.x, 'y': self.rect.y}

    @staticmethod
    def from_dict(data):
        return Tree(data['x'], data['y'])

class Coin: 
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, COIN_SIZE, COIN_SIZE)
        self.collected = False

    def draw(self, screen):
        if not self.collected:
            screen.blit(coin_image, self.rect)
 

    def to_dict(self):
        return {'x': self.rect.x, 'y': self.rect.y, 'collected': self.collected}

    @staticmethod
    def from_dict(data):
        coin = Coin(data['x'], data['y'])
        coin.collected = data['collected']
        return coin

    def draw_complete_screen(self, screen, x, y):
        if self.collected:
            screen.blit(coin_image, (x,y))  
        else:
            gray_surface = pygame.Surface((COIN_SIZE, COIN_SIZE), pygame.SRCALPHA)
            gray_surface.fill((0, 0, 0, 0)) 
            pygame.draw.circle(gray_surface, GRAY, (COIN_SIZE // 2, COIN_SIZE // 2),
                               COIN_SIZE // 2) 
            screen.blit(gray_surface, (x, y))  

class Level:
    def __init__(self, level_data=None, filename=None):  
        self.platforms = []
        self.spikes = []
        self.exit = None
        self.player_start = None
        self.trees = []
        self.coins = [] 
        self.filename = filename 
        if level_data:
            self.load_level(level_data)
        else:
            self.generate_level()

    def generate_level(self):
        num_platforms = random.randint(3, 6)
        for _ in range(num_platforms):
            width = random.randint(TILE_SIZE * 2, TILE_SIZE * 4)
            height = random.randint(TILE_SIZE // 2, TILE_SIZE)
            x = random.randint(0, WIDTH - width)
            y = random.randint(100, HEIGHT - height - PLAYER_SIZE)
            platform = Platform(x, y, width, height)
            if not any(platform.rect.colliderect(p.rect) for p in self.platforms):
                self.platforms.append(platform)


        platform_index = random.choice(range(len(self.platforms)))
        platform_rect = self.platforms[platform_index].rect

        spike_x = platform_rect.x + random.randint(0, platform_rect.width - TILE_SIZE)
        spike_y = platform_rect.top - TILE_SIZE
        self.spikes.append(Spike(spike_x, spike_y))

        exit_x = platform_rect.x + random.randint(0, platform_rect.width - TILE_SIZE)
        exit_y = platform_rect.top - TILE_SIZE
        self.exit = Exit(exit_x, exit_y)

        self.coins = []
        for _ in range(NUM_COINS):
            coin_x = random.randint(0, WIDTH - COIN_SIZE)
            coin_y = random.randint(100, HEIGHT - COIN_SIZE)
            self.coins.append(Coin(coin_x, coin_y))

    def load_level(self, level_data):
        self.platforms = []
        self.spikes = []
        self.exit = None
        self.player_start = None
        self.trees = []
        self.coins = []
        for row_index, row in enumerate(level_data):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if tile == "P":
                    self.platforms.append(Platform(x, y, TILE_SIZE, TILE_SIZE))
                elif tile == "S":
                    self.spikes.append(Spike(x, y))
                elif tile == "E":
                    self.exit = Exit(x, y)
                elif tile == "M":
                    self.player_start = PlayerStart(x, y)
                elif tile == "T":
                    self.trees.append(Tree(x, y))
                elif tile == "C":  
                    self.coins.append(Coin(x, y))
        while len(self.coins) < NUM_COINS:
            coin_x = random.randint(0, WIDTH - COIN_SIZE)
            coin_y = random.randint(100, HEIGHT - COIN_SIZE)
            self.coins.append(Coin(coin_x, coin_y))

    def draw(self, screen):
        for platform in self.platforms:
            platform.draw(screen)
        for spike in self.spikes:
            spike.draw(screen)
        if self.exit:
            self.exit.draw(screen)
        if self.player_start:
            self.player_start.draw(screen)
        for tree in self.trees:
            tree.draw(screen)
        for coin in self.coins:
            coin.draw(screen)

    def get_level_data(self):
        level_data = [["." for _ in range(WIDTH // TILE_SIZE)] for _ in range(HEIGHT // TILE_SIZE)]
        for platform in self.platforms:
            x = platform.rect.x // TILE_SIZE
            y = platform.rect.y // TILE_SIZE
            width = platform.rect.width // TILE_SIZE
            height = platform.rect.height // TILE_SIZE
            for i in range(height):
                for j in range(width):
                    if y + i < HEIGHT // TILE_SIZE and x + j < WIDTH // TILE_SIZE:
                        level_data[y + i][x + j] = "P"

        for spike in self.spikes:
            x = spike.rect.x // TILE_SIZE
            y = spike.rect.y // TILE_SIZE
            level_data[y][x] = "S"
        if self.exit:
            x = self.exit.rect.x // TILE_SIZE
            y = self.exit.rect.y // TILE_SIZE
            level_data[y][x] = "E"
        if self.player_start:
            x = self.player_start.rect.x // TILE_SIZE
            y = self.player_start.rect.y // TILE_SIZE
            level_data[y][x] = "M"
        for tree in self.trees:
            x = tree.rect.x // TILE_SIZE
            y = tree.rect.y // TILE_SIZE
            level_data[y][x] = "T"
        for coin in self.coins:
            x = coin.rect.x // TILE_SIZE
            y = coin.rect.y // TILE_SIZE
            level_data[y][x] = "C"
        return level_data

    def to_json(self):
        data = {
            'platforms': [platform.to_dict() for platform in self.platforms],
            'spikes': [spike.to_dict() for spike in self.spikes],
            'exit': self.exit.to_dict() if self.exit else None,
            'player_start': [self.player_start.to_dict()] if self.player_start else [],
            'trees': [tree.to_dict() for tree in self.trees],
            'coins': [coin.to_dict() for coin in self.coins]  
        }
        return json.dumps(data)

    @staticmethod
    def from_json(level_json):
        data = json.loads(level_json)
        level = Level()
        level.platforms = [Platform.from_dict(item) for item in data['platforms']]
        level.spikes = [Spike.from_dict(item) for item in data['spikes']]
        level.trees = [Tree.from_dict(item) for item in data['trees']]
        level.coins = [Coin.from_dict(item) for item in data['coins']]  
        if data['exit']:
            level.exit = Exit.from_dict(data['exit'])
        if data['player_start']:
            level.player_start = PlayerStart.from_dict(data['player_start'][0])

        return level

class Button: 
    def __init__(self, x, y, width, height, text, color, hover_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = button_font  
        self.text_surf = self.font.render(text, True, BUTTON_TEXT_COLOR)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surf, self.text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.action()

game_state = "MENU"

current_level_filename = None 

def start_game(): 
    global game_state
    game_state = "GAME"

def open_level_editor():
    global game_state
    game_state = "EDITOR"

def quit_game(): 
    pygame.quit()
    sys.exit()

def open_level_select(): 
    global game_state
    game_state = "LEVEL_SELECT"

def main_menu(): 
    global game_state


    num_buttons = 4  
    total_height = num_buttons * BUTTON_HEIGHT + (num_buttons - 1) * 20 
    start_y = (HEIGHT - total_height) // 2 

    x_offset = WIDTH // 4  
    vert_space = BUTTON_HEIGHT + 20  

    start_button = Button(x_offset - BUTTON_WIDTH // 2, start_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Start Game", BUTTON_COLOR, BUTTON_HOVER_COLOR, start_game)
    editor_button = Button(x_offset - BUTTON_WIDTH // 2, start_y + vert_space, BUTTON_WIDTH, BUTTON_HEIGHT, "Level Editor", BUTTON_COLOR, BUTTON_HOVER_COLOR, open_level_editor)
    level_select_button = Button(x_offset - BUTTON_WIDTH // 2, start_y + 2 * vert_space, BUTTON_WIDTH, BUTTON_HEIGHT, "Level Select", BUTTON_COLOR, BUTTON_HOVER_COLOR, open_level_select)
    quit_button = Button(x_offset - BUTTON_WIDTH // 2, start_y + 3 * vert_space, BUTTON_WIDTH, BUTTON_HEIGHT, "Quit", BUTTON_COLOR, BUTTON_HOVER_COLOR, quit_game)

    buttons = [start_button, editor_button, level_select_button, quit_button]

    while game_state == "MENU":
        screen.blit(menu_background, (0, 0)) 

        title_text = title_font.render("Gravity Game", True, BUTTON_TEXT_COLOR)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        for button in buttons:
            button.draw(screen)

        creator_text = creator_font.render("Created by Kovalev Inc.", True, BLACK)
        screen.blit(creator_text, (10, HEIGHT - 30))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for button in buttons:
                button.handle_event(event)

        clock.tick(FPS)
def game_over_screen(score): 
    while True:
        screen.blit(game_background, (0, 0))  

        game_over_text = title_font.render("Game Over", True, RED)
        score_text = button_font.render(f"Final Score: {score}", True, WHITE)  
        restart_text = button_font.render("Press R to Restart or Q to Quit", True, WHITE)

        center_x = WIDTH // 2
        base_y = HEIGHT // 2 - 70  

        screen.blit(game_over_text,
                    (center_x - game_over_text.get_width() // 2,
                     base_y - game_over_text.get_height() // 2))  

        screen.blit(score_text,  
                    (center_x - score_text.get_width() // 2,
                     base_y + game_over_text.get_height() // 2 + 30))  

        screen.blit(restart_text,
                    (center_x - restart_text.get_width() // 2,
                     base_y + game_over_text.get_height() + game_over_text.get_height() + 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_q:
                    return False

def level_complete_screen(level, time_taken): 
    global game_state_data
    collected_coins = sum(1 for coin in level.coins if coin.collected)

    level_data = {
        "coins_collected": collected_coins,
        "best_time": time_taken / 1000,
        "coins": collected_coins
    }

    if level.filename not in game_state_data or level_data["best_time"] < \
            game_state_data[level.filename]["best_time"]:  
        game_state_data[level.filename] = level_data
        save_game_state(game_state_data)

    while True:
        screen.blit(game_background, (0, 0))  

        complete_text = title_font.render("Level Complete!", True, WHITE)
        time_text = button_font.render(f"Time: {time_taken / 1000:.2f} seconds", True, WHITE)
        coins_text = button_font.render(f"Coins Collected: {collected_coins}", True, WHITE)  

        center_x = WIDTH // 2
        base_y = HEIGHT // 2 - 70 

        screen.blit(complete_text,
                    (center_x - complete_text.get_width() // 2,
                     base_y - complete_text.get_height() // 2))

        screen.blit(time_text,
                    (center_x - time_text.get_width() // 2,
                     base_y + complete_text.get_height() // 2 + 30))

        screen.blit(coins_text,
                    (center_x - coins_text.get_width() // 2,
                     base_y + complete_text.get_height() // 2 + time_text.get_height()+ 30))  


        coin_x_offset = WIDTH // 2 - (NUM_COINS * (COIN_SIZE + 5)) // 2
        coin_draw_y = base_y + complete_text.get_height() + time_text.get_height()+ coins_text.get_height() + 40 
        for i, coin in enumerate(level.coins):
            coin_draw_x = coin_x_offset + i * (COIN_SIZE + 5)
            coin.draw_complete_screen(screen, coin_draw_x, coin_draw_y)  

        restart_text = button_font.render("Press ENTER to Next Level or Q to Quit", True, WHITE)

        screen.blit(restart_text,
                    (center_x - restart_text.get_width() // 2,
                     coin_draw_y + COIN_SIZE + 50)) 

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_q:
                    return False

def load_level_from_file(filename): 
    try:
        with open(filename, "r") as f:
            level_data = [list(line.strip()) for line in f]
        return level_data
    except FileNotFoundError:
        print(f"Error: Level file '{filename}' not found.")
        return None

def level_select(): 
    global game_state, level_data, current_level_filename
    level_files = [f for f in os.listdir() if f.endswith(".txt")]
    buttons = []
    y_offset = 100
    for i, filename in enumerate(level_files):
        button = Button(WIDTH // 2 - 150, y_offset + i * 100, 300, 50, filename, BUTTON_COLOR, BUTTON_HOVER_COLOR,
                        lambda f=filename: load_selected_level(f)) 
        buttons.append(button)

    def load_selected_level(filename):
        global game_state, level_data, current_level_filename

        level_data = load_level_from_file(filename)
        if level_data:
            game_state = "GAME"
            current_level_filename = filename
        else:
            game_state = "MENU"  

    while game_state == "LEVEL_SELECT":
        screen.blit(menu_background, (0, 0))

        font_large = pygame.font.Font(None, 54)
        title_text = font_large.render("Select Level", True, BUTTON_TEXT_COLOR)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))

        for i, button in enumerate(buttons):
            level_name = level_files[i]
            button.draw(screen)

            level_data = game_state_data.get(level_name,
                                              {"coins_collected": 0, "best_time": float('inf')})

            coins_text = small_font.render(f"Coins: {level_data['coins_collected']}", True, BUTTON_TEXT_COLOR)
            screen.blit(coins_text, (button.rect.x + 10, button.rect.bottom + 5))  
            time_text = small_font.render(f"Time: {level_data['best_time']:.2f}", True, BUTTON_TEXT_COLOR)
            screen.blit(time_text, (button.rect.x + 10, button.rect.bottom + 20))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for button in buttons:
                button.handle_event(event)

        clock.tick(FPS)
    return  

def game(level_data=None):
    global game_state, game_state_data, current_level_filename, default_face
    filename = current_level_filename 

    if not filename:  
        print("Error: No level filename specified.")
        return "MENU"

    try:
        level_data = load_level_from_file(filename)
        if not level_data:
            print(f"Error: Could not load level data from {filename}")
            return "MENU"  
    except FileNotFoundError:
        print(f"Error: Level file '{filename}' not found.")
        return "MENU"

    level = Level(level_data=level_data, filename=filename)
    if level.player_start:
        player = Player(level.player_start.rect.x, level.player_start.rect.y)
    else:
        print("Error: Load default player")
        player = Player() 

    player.face = default_face

    start_time = pygame.time.get_ticks()
    running = True

    if filename in game_state_data:
        if isinstance(game_state_data[filename].get('coins', []), int): 
            print("Migrating old save data format to new type...") 

            saved_coins_state = [False] * len(level.coins) 

        else:
            saved_coins_state = game_state_data[filename].get('coins', []) 

        if len(saved_coins_state) < len(level.coins): 
            saved_coins_state.extend([False] * (len(level.coins) - len(saved_coins_state))) 
        elif len(saved_coins_state) > len(level.coins):
            saved_coins_state = saved_coins_state[:len(level.coins)]

        for i, coin in enumerate(level.coins):
            if i < len(saved_coins_state):
                coin.collected = saved_coins_state[i]
    else:
        for coin in level.coins:
            coin.collected = False 
    score=game_state_data["current_points"] 

    while running:
        screen.blit(game_background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and player.on_ground:
                    player.jump()
                if event.key == pygame.K_SPACE:
                    player.toggle_gravity()

        player.handle_input()
        player.update(level.platforms)

        for coin in level.coins:
            if (player.rect.colliderect(coin.rect) and not coin.collected):
                coin.collected = True
                game_state_data["current_points"] = game_state_data.get("current_points", 0) + 1
                score=game_state_data["current_points"]  
                save_game_state(game_state_data)

                print("Coin Collected!")


        for spike in level.spikes:
            if player.rect.colliderect(spike.rect):
                if game_over_screen(score):
                    return "GAME"
                else:
                    return "MENU"

        if level.exit and player.rect.colliderect(level.exit.rect):
            time_taken = pygame.time.get_ticks() - start_time
            coins_collected = sum(1 for coin in level.coins if coin.collected)
            coins_states = [coin.collected for coin in level.coins]

            UpdateCoins(coins_collected, time_taken, game_state_data, coins_states, filename)
            level_data = game_state_data.get(filename)
            save_game_state(game_state_data)

            if level_complete_screen(level, time_taken):
                return "GAME"
            else:
                return "MENU"

        level.draw(screen)
        player.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    return "MENU"  

def UpdateCoins(coins_collected, time_taken, game_state_data, coins_states, filename):
    """Обновляет данные об уровне (монеты и время) в game_state_data."""
    level_data = game_state_data.get(filename)

    if level_data is None or not isinstance(level_data, dict) or 'best_time' not in level_data:
        level_data = {
            "coins_collected": coins_collected,
            "best_time": float('inf'),  
            "coins": coins_states  
        }
        game_state_data[filename] = level_data
    elif level_data["best_time"] > time_taken / 1000:
        level_data["coins_collected"] = coins_collected
        level_data["best_time"] = time_taken / 1000
        level_data["coins"] = coins_states

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = button_font  
        self.text_surf = self.font.render(text, True, BUTTON_TEXT_COLOR) 
        self.text_rect = self.text_surf.get_rect(center=self.rect.center) 

    def draw(self, screen): 

        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos): 
            pygame.draw.rect(screen, self.hover_color, self.rect, border_radius = 5) 
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius = 5) 

        screen.blit(self.text_surf, self.text_rect) 

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.action()

class Editor:
    def __init__(self):
        self.current_tool = 'platform'
        self.level = Level()
        self.is_dragging = False
        self.selected_object = None
        self.start_pos = None
        self.platform_start_pos = None  
        self.editor_controls = {  
            "P": "Platform",
            "S": "Spike",
            "A": "Spike2",
            "E": "Exit",
            "C": "Player",
            "T": "Tree",
            "V": "Coin",
            "Z": "Save Level",
            "X": "Load Level",
            "ESC": "Main Menu"
        }

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.current_tool = 'platform'
            elif event.key == pygame.K_s:
                self.current_tool = 'spike'
            elif event.key == pygame.K_a:
                self.current_tool = 'spike_2'
            elif event.key == pygame.K_e:
                self.current_tool = 'exit'
            elif event.key == pygame.K_c:
                self.current_tool = 'player'
            elif event.key == pygame.K_t:
                self.current_tool = 'tree'
            elif event.key == pygame.K_v:
                self.current_tool = 'coin'
            elif event.key == pygame.K_z:
                self.save_level()
            elif event.key == pygame.K_x:
                self.load_level()
            elif event.key == pygame.K_ESCAPE:
                return "MENU"  

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.handle_mouse_down(event.pos)
            elif event.button == 3:
                self.handle_right_click(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.handle_mouse_up()

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging and self.selected_object and self.current_tool == 'platform':
                self.handle_mouse_drag(event.pos)  

        return None

    def handle_right_click(self, pos):
        for i, platform in enumerate(self.level.platforms):
            if platform.rect.collidepoint(pos):
                del self.level.platforms[i]
                self.draw()
                pygame.display.flip()
                return
        for i, spike in enumerate(self.level.spikes):
            if spike.rect.collidepoint(pos):
                del self.level.spikes[i]
                self.draw()
                pygame.display.flip()
                return
        if self.level.exit and self.level.exit.rect.collidepoint(pos):
            self.level.exit = None
            self.draw()
            pygame.display.flip()
            return
        if self.level.player_start and self.level.player_start.rect.collidepoint(pos):
            self.level.player_start = None
            self.draw()
            pygame.display.flip()
            return
        for i, tree in enumerate(self.level.trees):
            if tree.rect.collidepoint(pos):
                del self.level.trees[i]
                self.draw()
                pygame.display.flip()
                return
        for i, coin in enumerate(self.level.coins):
            if coin.rect.collidepoint(pos):
                del self.level.coins[i]
                self.draw()
                pygame.display.flip()
                return

    def handle_mouse_down(self, pos):
        if self.current_tool == 'platform':
            self.selected_object = Platform(pos[0], pos[1], 0, TILE_SIZE)
            self.is_dragging = True
            self.platform_start_pos = pos  
        elif self.current_tool == 'spike':
            self.level.spikes.append(Spike(pos[0], pos[1]))
        elif self.current_tool == 'spike_2':
            self.level.spikes.append(Spike(pos[0], pos[1], type=2))
        elif self.current_tool == 'exit':
            self.level.exit = Exit(pos[0], pos[1])
        elif self.current_tool == 'player':
            self.level.player_start = PlayerStart(pos[0], pos[1])
        elif self.current_tool == 'tree':
            self.level.trees.append(Tree(pos[0], pos[1]))
        elif self.current_tool == 'coin':
            self.level.coins.append(Coin(pos[0], pos[1]))

    def handle_mouse_up(self):
        if self.selected_object and self.current_tool == 'platform':
            if self.selected_object.rect.width > 0:
                self.level.platforms.append(self.selected_object)
            self.is_dragging = False
            self.selected_object = None
            self.platform_start_pos = None  

    def handle_mouse_drag(self, pos):
        if self.selected_object and self.current_tool == 'platform' and self.is_dragging:
            width = pos[0] - self.platform_start_pos[0]  
            height = TILE_SIZE  
            width = max(width, MIN_PLATFORM_SIZE)

            self.selected_object.resize(width, height) 

    def draw(self):
        screen.fill(BACKGROUND_COLOR)
        self.level.draw(screen)
        if self.selected_object and self.current_tool == 'platform' and self.is_dragging:
            self.selected_object.draw(screen)
        self.draw_editor_controls(screen)

    def draw_editor_controls(self, screen):
        x_offset = 10
        y_offset = 10
        line_height = 25
        for key, action in self.editor_controls.items():
            text = f"{key}: {action}"
            text_surface = editor_font.render(text, True, BLACK)
            screen.blit(text_surface, (x_offset, y_offset))
            y_offset += line_height

    def save_level(self):
        try:
            filename = simpledialog.askstring("Save Level", "Enter filename:")
            if filename:
                self.level.filename = filename + ".txt"
                level_data = self.level.get_level_data()
                with open(filename + '.txt', 'w') as f:
                    for row in level_data:
                        f.write("".join(row) + "\n")
                print("Level saved")
        except Exception as e:
            print(f"Error saving level: {e}")

    def load_level(self):
        try:
            filename = simpledialog.askstring("Load Level", "Enter filename:")
            if filename:
                level_data = load_level_from_file(filename + ".txt")
                if level_data:
                    self.level = Level(level_data, filename= filename + ".txt") 
                else:
                    print("Load error: level data not found in file")

                print("Level loaded")

        except FileNotFoundError:
            print("Error: level.json file not found")
        except Exception as e:
            print(f"Error loading level: {e}")

def level_editor():
    global game_state
    editor = Editor()
    editor.level.filename = "new_level.txt" 
    running = True

    while running and game_state == "EDITOR":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game_state = "MENU"
                break

            next_state = editor.handle_input(event)
            if next_state:
                game_state = next_state
                running = False

        editor.draw()
        pygame.display.flip()
        clock.tick(FPS)

    return "MENU"

if __name__ == "__main__":
    tkinter.Tk().withdraw()
    level_data = None

    level_files = [f for f in os.listdir() if f.endswith(".txt")]
    if level_files:  
        current_level_filename = level_files[0]

    if not game_state_data:

        game_state_data["current_points"] = 0
        save_game_state(game_state_data) 

    while True:
        if game_state == "MENU":
            main_menu()
        elif game_state == "GAME":
            game_state = game(level_data) 
            level_data = None 
        elif game_state == "EDITOR":
            game_state = level_editor()
        elif game_state == "LEVEL_SELECT":
            level_select()

    pygame.quit()
    sys.exit()