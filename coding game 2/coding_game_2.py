#------------------------------------------------------------------#
# Space Invaders Knockoff - Full Boss System Edition
# Created by Ben Ellis
# Fully merged, corrected, and cleaned
#------------------------------------------------------------------#

import pygame
import sys
import random
import math

pygame.init()

# SCREEN + COLORS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

GLOBAL_SFX_VOLUME = 1.0
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 150, 255)

ALIEN_COLORS = ["yellow", "red", "purple", "green", "orange", "blue"]
ALIEN_VERSIONS = ["a", "b", "c"]

# BOSS CONFIGURATION
BOSS_TYPES = ["juggernaut", "hive_mother", "teleporter", "laser_core", "bomber"]

# Each boss uses a consistent alien color/version
BOSS_SPRITES = {
    "juggernaut": ("red", "a"),
    "hive_mother": ("green", "c"),
    "teleporter": ("purple", "b"),
    "laser_core": ("blue", "c"),
    "bomber": ("orange", "a"),
}

BOSS_SCALE_FACTOR = 3
BOSS_LEVEL_INTERVAL = 5
selected_ship_color = GREEN

# FULLSCREEN + DYNAMIC RESOLUTION
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

# Boss vertical position (top area)
BOSS_Y_POSITION = max(20, int(SCREEN_HEIGHT * 0.08))

pygame.display.set_caption("Space Invaders")
font = pygame.font.SysFont(None, 50)
small_font = pygame.font.SysFont(None, 30)
clock = pygame.time.Clock()

player_lives = 3
pygame.mixer.music.set_volume(0.5)

# AUDIO SETUP 
MAIN_MENU_MUSIC = "assets/audio/main menu music.mp3"
GAME_MUSIC = "assets/audio/game music.ogg"

boss_alarm_sound = pygame.mixer.Sound("assets/audio/boss alarm.mp3")
laser_fire_sound = pygame.mixer.Sound("assets/audio/lazer boss.mp3")
player_shoot_sound = pygame.mixer.Sound("assets/audio/player_ship.mp3")
death_sound = pygame.mixer.Sound("assets/audio/death audio.mp3")
ship_damage_sound = pygame.mixer.Sound("assets/audio/ship dmg.ogg")

def start_main_menu_music():
    pygame.mixer.music.load(MAIN_MENU_MUSIC)
    pygame.mixer.music.play(-1)

#sfx volume
boss_alarm_sound.set_volume(GLOBAL_SFX_VOLUME)
laser_fire_sound.set_volume(GLOBAL_SFX_VOLUME)
player_shoot_sound.set_volume(GLOBAL_SFX_VOLUME)
death_sound.set_volume(GLOBAL_SFX_VOLUME)
ship_damage_sound.set_volume(GLOBAL_SFX_VOLUME)

def draw_centered_text(surface, text, font_obj, y, color):
    text_surf = font_obj.render(text, True, color)
    x = SCREEN_WIDTH // 2 - text_surf.get_width() // 2
    surface.blit(text_surf, (x, y))
# BACKGROUND
background_image = pygame.image.load("assets/background/SpaceBg.png").convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# NEON TITLE TEXT
def draw_neon_text(surface, text, font_obj, x, y, base_color):
    glow_colors = [
        (base_color[0] // 4, base_color[1] // 4, base_color[2] // 4),
        (base_color[0] // 2, base_color[1] // 2, base_color[2] // 2),
        base_color
    ]
    for i, color in enumerate(glow_colors):
        glow = font_obj.render(text, True, color)
        offset = 4 - i
        surface.blit(glow, (x - offset, y - offset))
        surface.blit(glow, (x + offset, y - offset))
        surface.blit(glow, (x - offset, y + offset))
        surface.blit(glow, (x + offset, y + offset))
    final = font_obj.render(text, True, WHITE)
    surface.blit(final, (x, y))

# BUTTON CLASS
class Button:
    def __init__(self, text, x, y, width, height, color, hover_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.rect(
            surface,
            self.hover_color if self.rect.collidepoint(mouse_pos) else self.color,
            self.rect
        )
        text_surf = font.render(self.text, True, WHITE)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# VOLUME BUTTON
class VolumeButton:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.muted = False

    def draw(self, surface):
        color = GRAY if not self.muted else DARK_GRAY
        pygame.draw.circle(surface, color, (self.x, self.y), self.size // 2)
        volume_text = small_font.render("Vol", True, WHITE)
        surface.blit(volume_text, volume_text.get_rect(center=(self.x, self.y)))

    def toggle(self):
        global GLOBAL_SFX_VOLUME

        self.muted = not self.muted

        if self.muted:
            pygame.mixer.music.set_volume(0)
            GLOBAL_SFX_VOLUME = 0
        else:
            pygame.mixer.music.set_volume(0.5)
            GLOBAL_SFX_VOLUME = 1.0

            # If we're in the main menu and music isn't playing, restart it
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(MAIN_MENU_MUSIC)
                pygame.mixer.music.play(-1)

        # Apply new SFX volume to all loaded sounds
        boss_alarm_sound.set_volume(GLOBAL_SFX_VOLUME)
        laser_fire_sound.set_volume(GLOBAL_SFX_VOLUME)
        player_shoot_sound.set_volume(GLOBAL_SFX_VOLUME)

def boss_intro(boss_type):
    title = boss_type.replace("_", " ").title()

    # Stop any current music (e.g., main menu)
    pygame.mixer.music.stop()

    for _ in range(2):
        # Draw encounter screen
        screen.blit(background_image, (0, 0))
        text1 = font.render("BOSS ENCOUNTER", True, WHITE)
        text2 = font.render(title, True, RED)

        screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

        boss_alarm_sound.play()

        # Wait for the sound to finish, but still process quit events
        end_time = pygame.time.get_ticks() + int(boss_alarm_sound.get_length() * 1000)
        while pygame.time.get_ticks() < end_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

# BOSS SELECT MENU
def boss_select_menu(volume_button):
    buttons = []
    y = 200
    for boss in BOSS_TYPES:
        buttons.append(Button(boss.title(), SCREEN_WIDTH//2 - 150, y, 300, 50, GRAY, DARK_GRAY))
        y += 80

    back_button = Button("Back", SCREEN_WIDTH//2 - 150, y, 300, 50, GRAY, DARK_GRAY)

    while True:
        screen.fill(BLACK)

        # Centered "Select Boss" title
        title_text = "Select Boss"
        title_width = font.render(title_text, True, WHITE).get_width()
        draw_neon_text(
            screen,
            title_text,
            font,
            SCREEN_WIDTH // 2 - title_width // 2,
            80,
            (0, 200, 255)
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for btn, boss in zip(buttons, BOSS_TYPES):
                if btn.is_clicked(event):
                    pygame.mixer.music.stop()
                    boss_intro(boss)
                    game(start_boss=boss, boss_mode=True, volume_button=volume_button)

            if back_button.is_clicked(event):
                # Only start menu music if it's not already playing and not muted
                if pygame.mixer.music.get_volume() > 0 and not pygame.mixer.music.get_busy():
                    start_main_menu_music()
                return

        for btn in buttons:
            btn.draw(screen)
        back_button.draw(screen)

        pygame.display.flip()
        clock.tick(120)

def game_over_screen():
    screen.fill(BLACK)

    msg1 = font.render("YOU DIED", True, RED)
    msg2 = small_font.render("Press ENTER to return to Main Menu", True, WHITE)

    screen.blit(msg1, (SCREEN_WIDTH//2 - msg1.get_width()//2, SCREEN_HEIGHT//2 - 80))
    screen.blit(msg2, (SCREEN_WIDTH//2 - msg2.get_width()//2, SCREEN_HEIGHT//2))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False

# MAIN MENU
def main_menu():
    play_button = Button("Play", SCREEN_WIDTH//2 - 100, 200, 200, 50, GRAY, DARK_GRAY)
    boss_button = Button("Boss Select", SCREEN_WIDTH//2 - 100, 280, 200, 50, GRAY, DARK_GRAY)
    exit_button = Button("Exit", SCREEN_WIDTH//2 - 100, 360, 200, 50, GRAY, DARK_GRAY)
    volume_button = VolumeButton(SCREEN_WIDTH - 60, 50, 40)

    # start menu music once when entering main_menu
    start_main_menu_music()

    while True:
        screen.fill(BLACK)

        # Centered title
        title_text = "Space Invaders Knockoff"
        title_width = font.render(title_text, True, WHITE).get_width()
        draw_neon_text(
            screen,
            title_text,
            font,
            SCREEN_WIDTH // 2 - title_width // 2,
            80,
            (0, 180, 255)
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if abs(event.pos[0] - volume_button.x) < 20 and abs(event.pos[1] - volume_button.y) < 20:
                    volume_button.toggle()

            if play_button.is_clicked(event):
                pygame.mixer.music.stop()
                game(volume_button=volume_button)
                # when game() returns (ESC or otherwise), resume menu music if not muted
                if not volume_button.muted and not pygame.mixer.music.get_busy():
                    start_main_menu_music()

            if boss_button.is_clicked(event):
                boss_select_menu(volume_button)

            if exit_button.is_clicked(event):
                pygame.quit()
                sys.exit()

        play_button.draw(screen)
        boss_button.draw(screen)
        exit_button.draw(screen)
        volume_button.draw(screen)

        pygame.display.flip()
        clock.tick(120)

# IMAGE SCALING
def scale_image_keep_aspect(img, target_width):
    scale_factor = target_width / img.get_width()
    new_height = int(img.get_height() * scale_factor)
    return pygame.transform.scale(img, (target_width, new_height))

# LOAD PLAYER ANIMATION
def load_player_animation_frames(target_width):
    frames = []
    for i in range(1, 10):
        filename = f"assets/player/redfighter{i:04}.png"
        img = pygame.image.load(filename).convert_alpha()
        img = scale_image_keep_aspect(img, target_width)
        frames.append(img)
    return frames

# LOAD BOMB FRAMES
def load_bomb_frames(target_width):
    travel = pygame.image.load("assets/explosions/bomb-a.png").convert_alpha()
    travel = scale_image_keep_aspect(travel, target_width)

    explosion_frames = []
    for name in ["b", "c", "d", "e"]:
        img = pygame.image.load(f"assets/explosions/bomb-{name}.png").convert_alpha()
        img = scale_image_keep_aspect(img, target_width)
        explosion_frames.append(img)

    return travel, explosion_frames

# LOAD ALIEN SPRITES
def load_alien_sprites(target_width):
    alien_sprites = {}
    for color in ALIEN_COLORS:
        alien_sprites[color] = {}
        for version in ALIEN_VERSIONS:
            frames = []
            for frame_index in range(1, 4):
                filename = f"assets/aliens/xenis-{color}-{version}-{frame_index}.png"
                img = pygame.image.load(filename).convert_alpha()
                img = scale_image_keep_aspect(img, target_width)
                frames.append(img)
            alien_sprites[color][version] = frames
    return alien_sprites

# GAME LOOP
def game(start_boss=None, boss_mode=False, volume_button=None):
    global player_lives

    player_lives = 3
    current_level = 1
    enemy_horizontal_speed = 1

    TARGET_ALIEN_WIDTH = 50
    alien_sprites = load_alien_sprites(TARGET_ALIEN_WIDTH)
    bomb_travel_frame, explosion_frames = load_bomb_frames(60)

    current_level_alien_version = random.choice(ALIEN_VERSIONS)
    enemy_list = []

    # BOSS STATE
    boss_active = False
    boss_type = None
    boss_hp = 0
    boss_max_hp = 0
    boss_rect = None
    boss_horizontal_speed = 2
    boss_horizontal_direction = 1
    boss_attack_timer = 0
    boss_attack_interval_ms = 1200

    # Boss sprite selection (color/version) and animation index
    boss_color = None
    boss_version = None

    # Separate timer for teleporter movement so it doesn't conflict with attacks
    boss_teleport_timer = 0
    boss_teleport_interval_ms = 1500

    hive_minion_list = []

    # LASER CORE
    # laser_follow_mode = False  -> lock-on shot (fixed at player's x when attack starts)
    # laser_follow_mode = True   -> special shot (beam moves with boss horizontally)
    laser_warning_active = False
    laser_active = False
    laser_follow_mode = False

    laser_warning_start_time = 0
    laser_fire_start_time = 0
    laser_warning_duration_ms = 800
    laser_fire_duration_ms = 1600

    laser_x = SCREEN_WIDTH // 2
    laser_target_x = SCREEN_WIDTH // 2

    # PLAYER INVULNERABILITY
    player_invulnerable = False
    player_invulnerable_until = 0
    player_blink_timer = 0
    player_blink_interval_ms = 120
    player_visible = True
    player_dead = False
    death_trigger_time = 0

    def handle_player_death():
        nonlocal player_dead, death_trigger_time

        if player_dead:
            return  # already handled

        # Stop all looping/background audio
        pygame.mixer.music.stop()
        boss_alarm_sound.stop()
        laser_fire_sound.stop()
        player_shoot_sound.stop()
        ship_damage_sound.stop()

        # Play only the death sound
        death_sound.play()

        player_dead = True
        death_trigger_time = pygame.time.get_ticks()

    # BOSS SELECT MODE
    if start_boss is not None:
        boss_active = True
        boss_type = start_boss
        if boss_type == "juggernaut":
            boss_hp = 120
        else:
            boss_hp = 60

        boss_max_hp = boss_hp
        boss_rect = None
        enemy_list.clear()
        current_level = 0

        if boss_type == "juggernaut":
            boss_horizontal_speed = 1
        else:
            boss_horizontal_speed = 2
        pygame.mixer.music.load(GAME_MUSIC)
        pygame.mixer.music.play(-1)

        # Set boss sprite based on type
        boss_color, boss_version = BOSS_SPRITES[boss_type]
    else:
        pass

    # SPAWN NORMAL ENEMIES
    def spawn_enemies():
        nonlocal current_level, current_level_alien_version
        enemy_list.clear()

        rows = min(2 + (current_level // 5), 6)
        aliens_per_row = 9
        spacing_x = 80
        spacing_y = 60
        start_x = (SCREEN_WIDTH - (aliens_per_row - 1) * spacing_x) // 2
        start_y = 50

        for row in range(rows):
            y = start_y + row * spacing_y
            for col in range(aliens_per_row):
                x = start_x + col * spacing_x

                alien_color = random.choice(ALIEN_COLORS)
                alien_version = current_level_alien_version

                enemy_list.append({
                    "x": x,
                    "y": y,
                    "color": alien_color,
                    "version": alien_version,
                    "current_frame_index": 0,
                    "is_pre_firing": False,
                    "pre_fire_start_time": 0,
                    "scheduled_shot_time": 0,
                    "pending_shot_type": None
                })

    if not boss_active:
        spawn_enemies()

    # PLAYER SETUP
    TARGET_PLAYER_WIDTH = 70
    player_frames = load_player_animation_frames(TARGET_PLAYER_WIDTH)

    player_ship_width = player_frames[0].get_width()
    player_ship_height = player_frames[0].get_height()

    player_position_x = SCREEN_WIDTH // 2 - player_ship_width // 2
    player_position_y = SCREEN_HEIGHT - player_ship_height - 10
    player_movement_speed = 4

    current_player_frame_index = 0
    player_animation_timer = 0
    player_animation_speed = 0.12
    player_animation_direction = 1

    # BULLETS
    player_bullet_list = []
    bullet_vertical_speed = 4

    enemy_vertical_drop_amount = 10
    enemy_horizontal_direction = 1

    last_player_shot_timestamp = 0
    player_shot_cooldown_ms = 600

    alien_bullet_list = []
    alien_min_shot_interval_ms = 500
    alien_max_shot_interval_ms = 1500
    next_alien_shot_timestamp = pygame.time.get_ticks() + random.randint(
        alien_min_shot_interval_ms, alien_max_shot_interval_ms
    )

    explosion_list = []
    pre_fire_duration_ms = 430

    # Start in-game music (loop)
    pygame.mixer.music.load(GAME_MUSIC)
    pygame.mixer.music.play(-1)

    # NORMAL ALIEN MOVEMENT
    def move_enemies():
        nonlocal enemy_horizontal_direction

        for enemy in enemy_list:
            enemy["x"] += enemy_horizontal_speed * enemy_horizontal_direction

        xs = [enemy["x"] for enemy in enemy_list]

        if enemy_list:
            sample_enemy = enemy_list[0]
            sample_frame = alien_sprites[sample_enemy["color"]][sample_enemy["version"]][0]
            alien_width = sample_frame.get_width()

            if max(xs) + alien_width > SCREEN_WIDTH or min(xs) < 0:
                enemy_horizontal_direction *= -1
                for enemy in enemy_list:
                    enemy["y"] += enemy_vertical_drop_amount

    # LEVEL UP
    def level_up():
        nonlocal current_level, enemy_horizontal_speed, current_level_alien_version
        nonlocal boss_active, boss_type, boss_hp, boss_max_hp, boss_rect, hive_minion_list
        nonlocal laser_warning_active, laser_active

        current_level += 1

        if current_level % BOSS_LEVEL_INTERVAL == 0:
            boss_active = True
            boss_type = random.choice(BOSS_TYPES)
            if boss_type == "juggernaut":
                boss_hp = 120
            else:
                boss_hp = 60

            boss_max_hp = boss_hp
            boss_rect = None
            hive_minion_list.clear()
            enemy_list.clear()
            laser_warning_active = False
            laser_active = False

            boss_color, boss_version = BOSS_SPRITES[boss_type]

            boss_intro(boss_type) 
            pygame.mixer.music.stop()
            boss_intro(boss_type)

            return
        if boss_type == "juggernaut":
            boss_horizontal_speed = 1
        else:
            boss_horizontal_speed = 2
        enemy_horizontal_speed += 0.2
        current_level_alien_version = random.choice(ALIEN_VERSIONS)
        spawn_enemies()

    # PREFIRE SYSTEM
    def schedule_alien_shot(current_time):
        if not enemy_list:
            return
        shooter = random.choice(enemy_list)

        if shooter["is_pre_firing"]:
            return

        pending_type = "green" if random.random() < 0.1 else "red"

        shooter["is_pre_firing"] = True
        shooter["pre_fire_start_time"] = current_time
        shooter["scheduled_shot_time"] = current_time + pre_fire_duration_ms
        shooter["pending_shot_type"] = pending_type
        shooter["current_frame_index"] = 0

    # EXPLOSIONS
    def draw_explosions():
        for explosion in explosion_list[:]:
            explosion['timer'] += 1

            if explosion['timer'] >= 8:
                explosion['timer'] = 0
                explosion['frame'] += 1

            if explosion['frame'] >= len(explosion_frames):
                explosion_list.remove(explosion)
                continue

            frame_img = explosion_frames[explosion['frame']]
            if explosion.get('type') == 'bomber_green':
                scale = 2.8
            else:
                scale = 1.5
            w = int(frame_img.get_width() * scale)
            h = int(frame_img.get_height() * scale)
            frame_img = pygame.transform.scale(frame_img, (w, h))

            x = explosion['pos'][0] - frame_img.get_width() // 2
            y = explosion['pos'][1] - frame_img.get_height() // 2

            screen.blit(frame_img, (x, y))

    # MAIN GAME LOOP STARTS HERE
    running = True
    while running:
        current_time = pygame.time.get_ticks()

        screen.blit(background_image, (0, 0))

        if player_dead:
            # Freeze gameplay completely
            if current_time - death_trigger_time >= int(death_sound.get_length() * 1000):
                game_over_screen()
                return

            pygame.display.flip()
            clock.tick(120)
            continue


        # PLAYER INVULNERABILITY
        if player_invulnerable:
            if current_time >= player_invulnerable_until:
                player_invulnerable = False
                player_visible = True
            else:
                if current_time - player_blink_timer >= player_blink_interval_ms:
                    player_blink_timer = current_time
                    player_visible = not player_visible
        else:
            player_visible = True


        # ALIEN SHOOT TIMER
        if not boss_active:
            if current_time >= next_alien_shot_timestamp:
                schedule_alien_shot(current_time)
                next_alien_shot_timestamp = current_time + random.randint(
                    alien_min_shot_interval_ms, alien_max_shot_interval_ms
                )

        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


            # ESC returns to main menu
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop()
                if volume_button and not volume_button.muted and not pygame.mixer.music.get_busy():
                    start_main_menu_music()
                return

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if player_invulnerable:
                    player_invulnerable = False
                    player_visible = True

                if current_time - last_player_shot_timestamp > player_shot_cooldown_ms:
                    player_bullet_list.append(
                        [player_position_x + player_ship_width // 2, player_position_y]
                    )
                    last_player_shot_timestamp = current_time
                    player_shoot_sound.play()

        # PLAYER MOVEMENT
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_position_x > 0:
            player_position_x -= player_movement_speed
        if keys[pygame.K_RIGHT] and player_position_x < SCREEN_WIDTH - player_ship_width:
            player_position_x += player_movement_speed

        # PLAYER ANIMATION
        if player_frames:
            player_animation_timer += player_animation_speed
            if player_animation_timer >= 1:
                player_animation_timer = 0
                current_player_frame_index += player_animation_direction

                if current_player_frame_index == len(player_frames) - 1:
                    player_animation_direction = -1
                elif current_player_frame_index == 0:
                    player_animation_direction = 1

            if player_visible:
                current_frame_image = player_frames[current_player_frame_index]
                screen.blit(current_frame_image, (player_position_x, player_position_y))

        # PLAYER HITBOX
        player_rect = pygame.Rect(
            player_position_x + 10,
            player_position_y + 10,
            player_ship_width - 20,
            player_ship_height - 20
        )

        # PLAYER BULLETS
        for bullet in player_bullet_list[:]:
            bullet[1] -= bullet_vertical_speed
            if bullet[1] < 0:
                player_bullet_list.remove(bullet)
            else:
                pygame.draw.rect(screen, WHITE, (bullet[0], bullet[1], 5, 10))

        # NORMAL ALIEN PREFIRE + SHOOTING
        if not boss_active:
            for enemy in enemy_list:
                color = enemy["color"]
                version = enemy["version"]
                frames = alien_sprites[color][version]
                frame_count = len(frames)

                if enemy["is_pre_firing"]:
                    elapsed = current_time - enemy["pre_fire_start_time"]
                    if elapsed < pre_fire_duration_ms:
                        progress = elapsed / pre_fire_duration_ms
                        enemy["current_frame_index"] = min(int(progress * frame_count), frame_count - 1)
                    else:
                        enemy["is_pre_firing"] = False
                        enemy["current_frame_index"] = 0

                        sprite = frames[0]
                        alien_width = sprite.get_width()
                        alien_height = sprite.get_height()
                        shot_x = enemy["x"] + alien_width // 2
                        shot_y = enemy["y"] + alien_height

                        if enemy["pending_shot_type"] == "green":
                            alien_bullet_list.append({'pos': [shot_x, shot_y], 'type': 'green'})
                        else:
                            alien_bullet_list.append({'pos': [shot_x, shot_y], 'type': 'red'})

                        enemy["pending_shot_type"] = None

        # ALIEN BULLETS (NORMAL + GREEN BOMBS)
        for bullet in alien_bullet_list[:]:

            # Move bullet downward
            bullet['pos'][1] += bullet_vertical_speed

            # Green bombs track the player
            if bullet['type'] == 'green':
                if bullet['pos'][0] < player_position_x:
                    bullet['pos'][0] += 1
                elif bullet['pos'][0] > player_position_x:
                    bullet['pos'][0] -= 1

            # Remove bullets off screen
            if bullet['type'] == 'bomber_green':
                bomb_height = bullet.get('scaled_height', bomb_travel_frame.get_height())
                bomb_bottom_y = bullet['pos'][1] + bomb_height // 2
                if bomb_bottom_y > SCREEN_HEIGHT:
                    alien_bullet_list.remove(bullet)
                    continue
            else:
                if bullet['pos'][1] > SCREEN_HEIGHT:
                    alien_bullet_list.remove(bullet)
                    continue

            # Draw bomber bomb
            if bullet['type'] == 'bomber_green':
                scale = 3.0
                w = int(bomb_travel_frame.get_width() * scale)
                h = int(bomb_travel_frame.get_height() * scale)
                missile_img = pygame.transform.scale(bomb_travel_frame, (w, h))
                bullet['scaled_height'] = h
                screen.blit(missile_img, (bullet['pos'][0] - w//2, bullet['pos'][1] - h//2))

            # Draw green bomb
            elif bullet['type'] == 'green':
                scale = 1.4
                w = int(bomb_travel_frame.get_width() * scale)
                h = int(bomb_travel_frame.get_height() * scale)
                missile_img = pygame.transform.scale(bomb_travel_frame, (w, h))
                screen.blit(missile_img, (bullet['pos'][0] - w//2, bullet['pos'][1] - h//2))

            # Draw red bullet
            elif bullet['type'] == 'red':
                pygame.draw.circle(screen, RED, bullet['pos'], 4)

            # GREEN / BOMBER EXPLOSIONS
            if bullet['type'] in ('green', 'bomber_green'):
                bomb_height = bullet['scaled_height'] if bullet['type'] == 'bomber_green' else int(bomb_travel_frame.get_height() * 1.4)
                bomb_bottom_y = bullet['pos'][1] + bomb_height // 2

                if bomb_bottom_y >= player_position_y:
                    explosion_center = [bullet['pos'][0], player_position_y + player_ship_height // 2]

                    explosion_list.append({
                        'pos': explosion_center,
                        'frame': 0,
                        'timer': 0,
                        'type': bullet['type']
                    })
                    alien_bullet_list.remove(bullet)

                    dx = abs(explosion_center[0] - player_rect.centerx)
                    dy = abs(explosion_center[1] - player_rect.centery)

                    explosion_radius = 90 if bullet['type'] == 'bomber_green' else 40

                    if not player_invulnerable:
                        if dx <= player_rect.width//2 + explosion_radius and dy <= player_rect.height//2 + explosion_radius:
                            ship_damage_sound.play()
                            player_lives -= 1
                            player_position_x = SCREEN_WIDTH//2 - player_ship_width//2

                            player_invulnerable = True
                            player_invulnerable_until = current_time + 3000
                            player_blink_timer = current_time

                            if player_lives <= 0:
                                pygame.mixer.music.stop()
                                death_sound.play()
                                game_over_screen()
                                return

                continue  # prevents red bullet logic from running on green bombs

            # RED BULLET DIRECT HIT
            if bullet['type'] == 'red':
                if player_rect.collidepoint(bullet['pos'][0], bullet['pos'][1]):
                    alien_bullet_list.remove(bullet)

                    if not player_invulnerable:
                        ship_damage_sound.play()
                        player_lives -= 1
                        player_position_x = SCREEN_WIDTH//2 - player_ship_width//2

                        player_invulnerable = True
                        player_invulnerable_until = current_time + 3000
                        player_blink_timer = current_time

                        if player_lives <= 0:
                            pygame.mixer.music.stop()
                            death_sound.play()
                            game_over_screen()
                            return
                         

                continue

        # NORMAL ALIEN MOVEMENT
        if not boss_active:
            move_enemies()
 
        # DRAW NORMAL ALIENS
        enemy_rect_list = []
        if not boss_active:
            for enemy in enemy_list:
                color = enemy["color"]
                version = enemy["version"]
                frames = alien_sprites[color][version]
                current_frame = frames[enemy["current_frame_index"]]
                alien_width = current_frame.get_width()
                alien_height = current_frame.get_height()

                rect = pygame.Rect(enemy["x"], enemy["y"], alien_width, alien_height)
                enemy_rect_list.append(rect)
                screen.blit(current_frame, (enemy["x"], enemy["y"]))

        # PLAYER BULLET COLLISION WITH NORMAL ALIENS
        if not boss_active:
            for bullet in player_bullet_list[:]:
                bullet_rect = pygame.Rect(bullet[0], bullet[1], 5, 10)
                for enemy, enemy_rect in zip(enemy_list[:], enemy_rect_list[:]):
                    if enemy_rect.colliderect(bullet_rect):
                        enemy_list.remove(enemy)
                        player_bullet_list.remove(bullet)
                        enemy_rect_list.remove(enemy_rect)
                        break

        # NORMAL ALIEN COLLISION WITH PLAYER
        if not boss_active:
            for enemy_rect in enemy_rect_list:
                if enemy_rect.colliderect(player_rect):
                    game_over_screen()
                    return

        # NORMAL ALIENS REACH BOTTOM
        if not boss_active:
            for enemy in enemy_list:
                color = enemy["color"]
                version = enemy["version"]
                frame = alien_sprites[color][version][0]
                alien_height = frame.get_height()
                if enemy["y"] + alien_height >= player_position_y:
                    game_over_screen()
                    return

        # LEVEL COMPLETE
        if not boss_active and not enemy_list:
            level_up()
            waiting = True
            while waiting and not boss_active:
                screen.blit(background_image, (0, 0))
                msg = font.render("Level Complete!", True, WHITE)
                msg2 = small_font.render("Press ENTER for next level or ESC to quit", True, WHITE)
                screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 250))
                screen.blit(msg2, (SCREEN_WIDTH // 2 - msg2.get_width() // 2, 320))
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            waiting = False
                        if event.key == pygame.K_ESCAPE:
                            return

        # HUD
        lives_text = small_font.render(f"Lives: {player_lives}", True, WHITE)
        screen.blit(lives_text, (10, 10))

        level_text = small_font.render(f"Level: {current_level}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH - 120, 10))

        # Boss HP bar (shows whenever a boss is active, regardless of how you got there)
        if boss_active and boss_max_hp > 0:
            bar_width = int(SCREEN_WIDTH * 0.5)
            bar_height = 20
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            bar_y = 10

            # Background bar
            pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))

            # Current HP
            hp_ratio = max(0, boss_hp / boss_max_hp)
            current_width = int(bar_width * hp_ratio)
            pygame.draw.rect(screen, RED, (bar_x, bar_y, current_width, bar_height))

            # Boss name text
            boss_name_text = small_font.render(boss_type.replace("_", " ").title(), True, WHITE)
            screen.blit(
                boss_name_text,
                (SCREEN_WIDTH // 2 - boss_name_text.get_width() // 2, bar_y + bar_height + 5)
            )

        draw_explosions()
         
        if boss_active:
    
            # INITIALIZE BOSS RECT IF NOT CREATED YET
             
            # BOSS LOGIC STARTS HERE
            if boss_active:

                # INITIALIZE BOSS RECT IF NOT CREATED YET
                if boss_rect is None:
                    # Use the boss's configured color/version
                    if boss_color is None or boss_version is None:
                        boss_color, boss_version = BOSS_SPRITES[boss_type]

                    base_img = alien_sprites[boss_color][boss_version][0]
                    w = int(base_img.get_width() * BOSS_SCALE_FACTOR)
                    h = int(base_img.get_height() * BOSS_SCALE_FACTOR)
                    boss_rect = pygame.Rect(
                        SCREEN_WIDTH // 2 - w // 2,
                        BOSS_Y_POSITION,
                        w,
                        h
                    )
                    boss_teleport_timer = current_time

                # BOSS MOVEMENT (SIDE-TO-SIDE EXCEPT TELEPORTER)
                if boss_type != "teleporter":
                    boss_rect.x += boss_horizontal_speed * boss_horizontal_direction

                    if boss_rect.right >= SCREEN_WIDTH or boss_rect.left <= 0:
                        boss_horizontal_direction *= -1
                else:
                    # TELEPORTER: random teleport every 1.5 seconds (separate timer)
                    if current_time - boss_teleport_timer > boss_teleport_interval_ms:
                        boss_teleport_timer = current_time
                        # Teleport to a random X but keep boss fully on screen
                        boss_rect.x = random.randint(50, SCREEN_WIDTH - 50 - boss_rect.width)

             
            # BOSS ATTACKS
            if current_time - boss_attack_timer > boss_attack_interval_ms:
                boss_attack_timer = current_time

                if boss_type == "juggernaut":
                    # Triple red shot
                    for offset in [-40, 0, 40]:
                        alien_bullet_list.append({
                            'pos': [boss_rect.centerx + offset, boss_rect.bottom],
                            'type': 'red'
                        })

                elif boss_type == "bomber":
                    # Bomber shoots slower
                    boss_attack_interval_ms = 1200

                    alien_bullet_list.append({
                        'pos': [boss_rect.centerx, boss_rect.bottom],
                        'type': 'bomber_green'
                    })

                elif boss_type == "teleporter":
                    # Fast red shot
                    alien_bullet_list.append({
                        'pos': [boss_rect.centerx, boss_rect.bottom],
                        'type': 'red'
                    })

                elif boss_type == "laser_core":
                    # Start a laser attack:
                    #  - 60% chance: lock-on shot (fixed at player's current x)
                    #  - 40% chance: special shot (beam moves with boss horizontally)
                    laser_warning_active = True
                    laser_active = False
                    laser_warning_start_time = current_time

                    if random.random() < 0.6:
                        # Lock-on mode: remember where the player is RIGHT NOW
                        laser_follow_mode = False
                        laser_target_x = player_rect.centerx
                        laser_x = laser_target_x
                    else:
                        # Special mode: beam will move with the boss
                        laser_follow_mode = True
                        laser_x = boss_rect.centerx

                elif boss_type == "hive_mother":
                    # Summon minions
                    if len(hive_minion_list) < 6:
                        angle = random.uniform(0, 360)
                        hive_minion_list.append({
                            "angle": angle,
                            "distance": 140,
                            "color": random.choice(ALIEN_COLORS),
                            "version": random.choice(ALIEN_VERSIONS),
                            "frame": 0,
                            "shot_timer": current_time
                        })

            # LASER CORE — GHOST LASER + REAL LASER
            if boss_type == "laser_core":

                # Ghost laser (warning phase)

                if laser_warning_active:
                    # In special mode, ghost beam moves with boss.
                    # In lock-on mode, it stays where it first targeted the player.
                    if laser_follow_mode:
                        laser_x = boss_rect.centerx

                    pygame.draw.line(
                        screen,
                        (0, 255, 255),
                        (laser_x, boss_rect.bottom),
                        (laser_x, SCREEN_HEIGHT),
                        4
                    )

                    if current_time - laser_warning_start_time >= laser_warning_duration_ms:
                        laser_warning_active = False
                        laser_active = True
                        laser_fire_start_time = current_time

                        # Play real laser sound
                        laser_fire_sound.play()

                # Real laser (damage phase)
                if laser_active:
                    # In special mode, real beam also moves with boss.
                    if laser_follow_mode:
                        laser_x = boss_rect.centerx

                    pygame.draw.line(
                        screen,
                        (255, 0, 0),
                        (laser_x, boss_rect.bottom),
                        (laser_x, SCREEN_HEIGHT),
                        8
                    )

                    # Damage player if they are in the beam column
                    if not player_invulnerable:
                        if player_rect.left <= laser_x <= player_rect.right:
                            player_lives -= 1
                            player_position_x = SCREEN_WIDTH // 2 - player_ship_width // 2

                            player_invulnerable = True
                            player_invulnerable_until = current_time + 3000
                            player_blink_timer = current_time

                            if player_lives <= 0:
                                pygame.mixer.music.stop()      
                                boss_alarm_sound.stop()        
                                laser_fire_sound.stop()        
                                player_shoot_sound.stop()      

                                death_sound.play()            
                                pygame.time.delay(int(death_sound.get_length() * 1000))

                                game_over_screen()
                                return

                    # End of laser duration
                    if current_time - laser_fire_start_time >= laser_fire_duration_ms:
                        laser_active = False

             
            # HIVE MOTHER — ORBITING MINIONS
            if boss_type == "hive_mother":
                for minion in hive_minion_list[:]:
                    minion["angle"] += 0.8
                    rad = math.radians(minion["angle"])

                    mx = boss_rect.centerx + math.cos(rad) * minion["distance"]
                    my = boss_rect.centery + math.sin(rad) * minion["distance"]

                    # Keep minions in upper half
                    if my > SCREEN_HEIGHT * 0.45:
                        my = SCREEN_HEIGHT * 0.45

                    frame = alien_sprites[minion["color"]][minion["version"]][minion["frame"]]
                    minion_rect = pygame.Rect(mx, my, frame.get_width(), frame.get_height())

                    screen.blit(frame, (mx, my))

                    # Minion shooting
                    if current_time - minion["shot_timer"] > 1200:
                        minion["shot_timer"] = current_time
                        alien_bullet_list.append({
                            'pos': [mx + frame.get_width()//2, my + frame.get_height()//2],
                            'type': random.choice(['red', 'green'])
                        })

                    # Player bullet hits minion
                    for bullet in player_bullet_list[:]:
                        bullet_rect = pygame.Rect(bullet[0], bullet[1], 5, 10)
                        if minion_rect.colliderect(bullet_rect):
                            player_bullet_list.remove(bullet)
                            hive_minion_list.remove(minion)
                            break

             # Draw boss using its configured alien sprite with attack animation
            if boss_color is None or boss_version is None:
                boss_color, boss_version = BOSS_SPRITES[boss_type]

            boss_frames = alien_sprites[boss_color][boss_version]

            elapsed_since_attack = current_time - boss_attack_timer

            if elapsed_since_attack < 200:
                frame_idx = 0
            elif elapsed_since_attack < 400:
                frame_idx = 1
            else:
                frame_idx = 2

            boss_frame = boss_frames[frame_idx]
            boss_img = pygame.transform.scale(boss_frame, (boss_rect.width, boss_rect.height))
            screen.blit(boss_img, boss_rect)

             
            # PLAYER BULLETS DAMAGE BOSS
            for bullet in player_bullet_list[:]:
                bullet_rect = pygame.Rect(bullet[0], bullet[1], 5, 10)
                if boss_rect.colliderect(bullet_rect):
                    player_bullet_list.remove(bullet)
                    boss_hp -= 1

                    if boss_hp <= 0:
                        boss_active = False
                        hive_minion_list.clear()
                        laser_active = False
                        laser_warning_active = False

                        # Boss defeated screen
                        waiting = True
                        while waiting:
                            screen.blit(background_image, (0, 0))
                            msg = font.render("Boss Defeated!", True, WHITE)
                            msg2 = small_font.render("Press ENTER to continue or ESC to quit", True, WHITE)
                            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 250))
                            screen.blit(msg2, (SCREEN_WIDTH // 2 - msg2.get_width() // 2, 320))
                            pygame.display.flip()

                            for event in pygame.event.get():
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_RETURN:
                                        level_up()
                                        waiting = False
                                    if event.key == pygame.K_ESCAPE:
                                        return

        pygame.display.flip()
        clock.tick(120)

# GAME OVER SCREEN
def game_over_screen():
    while True:
        screen.blit(background_image, (0, 0))
        over_text = font.render("Game Over!", True, WHITE)
        prompt_text = small_font.render("Press ENTER to Restart or ESC to Quit", True, WHITE)

        screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    death_sound.stop()
                    game(volume_button=volume_button)
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

# START GAME
if __name__ == "__main__":
    main_menu()