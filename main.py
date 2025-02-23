import pygame
import csv
import constants
from character import Character
from weapon import Weapon
from items import Item
from world import World
from button import Button
from pygame import mixer

mixer.init()
pygame.init()

# Create Window (constants)
screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Game")

# Game variables
level = 1
screen_scroll = [0, 0]
start_fade = False
start_game = False
pause_game = False

# Control game speed
clock = pygame.time.Clock()

# Define player movement
moving_left = False
moving_right = False
moving_down = False
moving_up = False

# Default font
font = pygame.font.Font("assets/fonts/AtariClassic.ttf", 20)

# Scaling Function
def scale_image(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (w * scale, h * scale))

# Load audio
pygame.mixer.music.load("assets/audio/music.wav")
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play(-1, 0.0, 3000)
shot_sound = pygame.mixer.Sound("assets/audio/arrow_shot.mp3")
shot_sound.set_volume(0.4)
hit_sound = pygame.mixer.Sound("assets/audio/arrow_hit.wav")
hit_sound.set_volume(0.4)
coin_sound = pygame.mixer.Sound("assets/audio/coin.wav")
coin_sound.set_volume(0.4)
heal_sound = pygame.mixer.Sound("assets/audio/heal.wav")
heal_sound.set_volume(0.4)

# Button images
restart_image = scale_image(pygame.image.load("assets/images/buttons/button_restart.png").convert_alpha(), constants.BUTTON_SCALE)
start_image = scale_image(pygame.image.load("assets/images/buttons/button_start.png").convert_alpha(), constants.BUTTON_SCALE)
exit_image = scale_image(pygame.image.load("assets/images/buttons/button_exit.png").convert_alpha(), constants.BUTTON_SCALE)
resume_image = scale_image(pygame.image.load("assets/images/buttons/button_resume.png").convert_alpha(), constants.BUTTON_SCALE)

# Life images
heart_full = scale_image(pygame.image.load("assets/images/items/heart_full.png").convert_alpha(), constants.ITEM_SCALE)
heart_half = scale_image(pygame.image.load("assets/images/items/heart_half.png").convert_alpha(), constants.ITEM_SCALE)
heart_empty = scale_image(pygame.image.load("assets/images/items/heart_empty.png").convert_alpha(), constants.ITEM_SCALE)

# Coin images
coin_images = []
for i in range(4):
    img = scale_image(pygame.image.load(f"assets/images/items/coin_f{i}.png").convert_alpha(), constants.ITEM_SCALE)
    coin_images.append(img)

# Potion image
potion_image = scale_image(pygame.image.load("assets/images/items/potion_red.png").convert_alpha(), constants.POTION_SCALE)

item_images = []
item_images.append(coin_images)
item_images.append(potion_image)

# Load weapon images
bow_image = scale_image(pygame.image.load(f"assets/images/weapons/bow.png").convert_alpha(), constants.BOW_SCALE)
arrow_image = scale_image(pygame.image.load(f"assets/images/weapons/arrow.png").convert_alpha(), constants.BOW_SCALE)
fireball_image = scale_image(pygame.image.load(f"assets/images/weapons/fireball.png").convert_alpha(), constants.FB_SCALE)

# Load tile_map images
tile_list = []
for x in range(constants.TILE_TYPES):
    img = pygame.image.load(f"assets/images/tiles/{x}.png").convert_alpha()
    img = pygame.transform.scale(img, (constants.TILE_SIZE, constants.TILE_SIZE))
    tile_list.append(img)

# Load character images
mob_animations = []
mob_types = ["elf", "imp", "skeleton", "goblin", "muddy", "tiny_zombie", "big_demon"]

animation_types = ["idle", "run"]
for mob in mob_types:
    # Load images
    animation_list = []
    for animation in animation_types:
        temp_list = []
        for i in range(4):
            img = pygame.image.load(f"assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
            img = scale_image(img, constants.SCALE)
            temp_list.append(img)
        animation_list.append(temp_list)
    mob_animations.append(animation_list)

# Function to output text
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

# Display game info
def draw_info():
    pygame.draw.rect(screen, constants.PANEL_COLOR, (0, 0, constants.SCREEN_WIDTH, 50))
    pygame.draw.line(screen, constants.WHITE, (0, 50), (constants.SCREEN_WIDTH, 50), 2)
    # Draw lives
    half_heart_drawn = False
    for i in range(5):
        if player.hp >= ((i + 1) * 20):
            screen.blit(heart_full, (15 + (i * 50), 0))
        elif (player.hp % 20 > 0) and half_heart_drawn == False:
            screen.blit(heart_half, (15 + (i * 50), 0))
            half_heart_drawn = True
        else:
            screen.blit(heart_empty, (15 + (i * 50), 0))

    # Show level
    draw_text(f"Level: {level}", font, constants.WHITE, constants.SCREEN_WIDTH / 2, 15)

    # Draw coins
    draw_text(f"X{player.coins}", font, constants.WHITE, constants.SCREEN_WIDTH - 100, 15)

# Reset Level
def reset_level():
    damage_text_group.empty()
    arrow_group.empty()
    fireball_group.empty()
    item_group.empty()

    # Create empty world data
    data = []
    for row in range(constants.ROWS):
        r = [-1] * constants.COLS
        data.append(r)
    
    return data


world_data = []
for row in range(constants.ROWS):
    r = [-1] * constants.COLS
    world_data.append(r)

# Load level data to create world
with open(f"levels/level{level}_data.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
world.process_data(world_data, tile_list, item_images, mob_animations)

# Damage Class
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        super().__init__()
        self.image = font.render(str(damage), True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.delay = 0

    def update(self):
        # Move based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]
        # Move text up
        self.rect.y -= 1
        if self.rect.y < 0:
            self.kill()
        # Delete damage text after fixed delay
        self.delay += 1
        if self.delay > 50:
            self.kill()
        
class ScreenFade():
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1: # whole screen fade
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (constants.SCREEN_WIDTH // 2 + self.fade_counter, 0, constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0 - self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color, (0, constants.SCREEN_HEIGHT // 2 + self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT // 2))
        elif self.direction == 2: # vertical screen fade downwards
            pygame.draw.rect(screen, self.color, (0, 0, constants.SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= constants.SCREEN_WIDTH:
            fade_complete = True

        return fade_complete

# Create player
player = world.player
# Create player weapon
bow = Weapon(bow_image, arrow_image)

# Enemy list from world data
enemy_list = world.character_list


# Sprite groups
damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()

score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
item_group.add(score_coin)

# Add items from level data
for item in world.item_list:
    item_group.add(item)


# Create screen fade
first_fade = ScreenFade(1, constants.BLACK, 4)
death_fade = ScreenFade(2, constants.PINK, 4)

# Create buttons
restart_button = Button(restart_image, constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 50)
start_button = Button(start_image, constants.SCREEN_WIDTH // 2 - 145, constants.SCREEN_HEIGHT // 2 - 150)
exit_button = Button(exit_image, constants.SCREEN_WIDTH // 2 - 110, constants.SCREEN_HEIGHT // 2 + 50)
resume_button = Button(resume_image, constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 150)

# Game Loop
run = True
while run:

    clock.tick(constants.FPS)

    if start_game == False:
        screen.fill(constants.MENU_COLOR)
        if start_button.draw(screen):
            start_game = True
            start_fade = True
        if exit_button.draw(screen):
            run = False
    else:
        if pause_game == True:
            screen.fill(constants.MENU_COLOR)
            if resume_button.draw(screen):
                pause_game = False
            if exit_button.draw(screen):
                run = False
        else:
            screen.fill(constants.BACKGROUND_COLOR)
            if player.alive:
                
                # Player movement
                dx = 0
                dy = 0
                if moving_left == True:
                    dx = -constants.PLAYER_SPEED
                if moving_right == True:
                    dx = constants.PLAYER_SPEED
                if moving_down == True:
                    dy = constants.PLAYER_SPEED
                if moving_up == True:
                    dy = -constants.PLAYER_SPEED

                # Move player
                screen_scroll, level_complete = player.move(dx, dy, world.obstacle_tiles, world.exit_tile)

                # Update objects
                world.update(screen_scroll)
                for enemy in enemy_list:
                    fireball = enemy.ai(player, world.obstacle_tiles, screen_scroll, fireball_image)
                    if fireball:
                        fireball_group.add(fireball)
                    if enemy.alive:
                        enemy.update()
                player.update()
                arrow = bow.update(player)
                if arrow:
                    arrow_group.add(arrow)
                    shot_sound.play()
                for arrow in arrow_group:
                    damage, damage_position = arrow.update(screen_scroll, world.obstacle_tiles, enemy_list)
                    if damage:
                        hit_sound.play()
                        damage_text = DamageText(damage_position.centerx, damage_position.y, str(damage), constants.PLAYER_COLOR) # (red)
                        damage_text_group.add(damage_text) 
                damage_text_group.update()
                fireball_group.update(screen_scroll, player)
                item_group.update(screen_scroll, player, coin_sound, heal_sound)

            # Draw player
            world.draw(screen)
            for enemy in enemy_list:
                enemy.draw(screen)
            player.draw(screen)
            bow.draw(screen)
            for arrow in arrow_group:
                arrow.draw(screen)
            for fireball in fireball_group:
                fireball.draw(screen)
            damage_text_group.draw(screen)
            item_group.draw(screen)
            draw_info()
            score_coin.draw(screen)

            # Check if level is complete
            if level_complete:
                start_fade = True
                level += 1
                world_data = reset_level()
                # Load in level data
                with open(f"levels/level{level}_data.csv", newline="") as csvfile:
                    reader = csv.reader(csvfile, delimiter=",")
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                world.process_data(world_data, tile_list, item_images, mob_animations)
                temp_hp = player.hp
                temp_coins = player.coins
                player = world.player
                player.hp = temp_hp
                player.coins = temp_coins
                enemy_list = world.character_list
                score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
                item_group.add(score_coin)
                for item in world.item_list:
                    item_group.add(item)


            # Show starting fade
            if start_fade:
                if first_fade.fade():
                    start_fade = False
                    first_fade.fade_counter = 0

            # Show death fade
            if player.alive == False:
                if death_fade.fade():
                    if restart_button.draw(screen):
                        death_fade.fade_counter = 0
                        start_fade = True
                        world_data = reset_level()
                        # Load in level data
                        with open(f"levels/level{level}_data.csv", newline="") as csvfile:
                            reader = csv.reader(csvfile, delimiter=",")
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        world.process_data(world_data, tile_list, item_images, mob_animations)
                        temp_coins = player.coins
                        player = world.player
                        player.coins = temp_coins
                        enemy_list = world.character_list
                        score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
                        item_group.add(score_coin)
                        for item in world.item_list:
                            item_group.add(item)

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_s:
                moving_down = True
            if event.key == pygame.K_w:
                moving_up = True
            if event.key == pygame.K_ESCAPE:
                pause_game = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_s:
                moving_down = False
            if event.key == pygame.K_w:
                moving_up = False

    # Update Display
    pygame.display.update()

pygame.quit()