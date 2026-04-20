#------------------------------------------------------------------#
# Space Invaders Knockoff - Animated Ship + Clean Variable Names
# Created by Ben Ellis
# Last modified 4/20/2026
#------------------------------------------------------------------#

import pygame
import sys
import random

pygame.init()

# Screen + Colors
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

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

selected_ship_color = GREEN

# ---------------------------------------------------------
# FULLSCREEN FIX  Borderless fullscreen + dynamic resolution
# ---------------------------------------------------------
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

# Update screen size to match monitor resolution
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

pygame.display.set_caption("Space Invaders")
font = pygame.font.SysFont(None, 50)
small_font = pygame.font.SysFont(None, 30)
clock = pygame.time.Clock()

player_lives = 3
pygame.mixer.music.set_volume(0.5)

# Load Background Image (GAME ONLY, NOT MENU)
background_image = pygame.image.load("assets/background/SpaceBg.png").convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))


# Neon Title Text
def draw_neon_text(surface, text, font_obj, x, y, base_color):
    glow_colors = [
        (base_color[0]//4, base_color[1]//4, base_color[2]//4),
        (base_color[0]//2, base_color[1]//2, base_color[2]//2),
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


# Button Class
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
        if event.type == pygame.MOUSEBUTTONDOWN:
         if hasattr(event, "pos"):
            return self.rect.collidepoint(event.pos)
        return False


# Volume Button
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
        self.muted = not self.muted
        pygame.mixer.music.set_volume(0 if self.muted else 0.5)


# Main Menu
def main_menu():
    play_button = Button("play", SCREEN_WIDTH//2 - 100, 200, 200, 50, GRAY, DARK_GRAY)
    exit_button = Button("Exit", SCREEN_WIDTH//2 - 100, 360, 200, 50, GRAY, DARK_GRAY)
    volume_button = VolumeButton(SCREEN_WIDTH - 60, 50, 40)

    while True:
        screen.fill(BLACK)

        title_text = "Space Invaders Knockoff"
        title_x = SCREEN_WIDTH//2 - font.size(title_text)[0]//2
        title_y = 80
        draw_neon_text(screen, title_text, font, title_x, title_y, (0, 180, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if play_button.is_clicked(event):
                game()

            if exit_button.is_clicked(event):
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if abs(event.pos[0] - volume_button.x) < 20 and abs(event.pos[1] - volume_button.y) < 20:
                    volume_button.toggle()

        play_button.draw(screen)
        exit_button.draw(screen)
        volume_button.draw(screen)

        pygame.display.flip()
        clock.tick(120)


# Scales an image while keeping its aspect ratio
def scale_image_keep_aspect(img, target_width):
    scale_factor = target_width / img.get_width()
    new_height = int(img.get_height() * scale_factor)
    return pygame.transform.scale(img, (target_width, new_height))


# Load Player Animation Frames
def load_player_animation_frames(target_width):
    frames = []
    for i in range(1, 10):
        filename = f"assets/player/redfighter{i:04}.png"
        img = pygame.image.load(filename).convert_alpha()
        img = scale_image_keep_aspect(img, target_width)
        frames.append(img)
    return frames


# Load Alien Sprites
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
# Game Loop
def game():
    global player_lives

    player_lives = 3
    current_level = 1
    enemy_horizontal_speed = 1

    TARGET_ALIEN_WIDTH = 50
    alien_sprites = load_alien_sprites(TARGET_ALIEN_WIDTH)

    # One version per level
    current_level_alien_version = random.choice(ALIEN_VERSIONS)

    enemy_list = []

    # Spawn Enemies (nested correctly)
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

                # One version per level, random color per alien
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

    spawn_enemies()

    # Player Setup
    TARGET_PLAYER_WIDTH = 70
    player_frames = load_player_animation_frames(TARGET_PLAYER_WIDTH)

    player_ship_width = player_frames[0].get_width()
    player_ship_height = player_frames[0].get_height()

    player_position_x = SCREEN_WIDTH // 2 - player_ship_width // 2
    player_position_y = SCREEN_HEIGHT - player_ship_height - 10
    player_movement_speed = 4

    # Animation state
    current_player_frame_index = 0
    player_animation_timer = 0
    player_animation_speed = 0.12
    player_animation_direction = 1

    # Bullets
    player_bullet_list = []
    bullet_vertical_speed = 4

    enemy_vertical_drop_amount = 10
    enemy_horizontal_direction = 1

    last_player_shot_timestamp = 0
    player_shot_cooldown_ms = 300

    alien_bullet_list = []
    alien_min_shot_interval_ms = 500
    alien_max_shot_interval_ms = 1500
    next_alien_shot_timestamp = pygame.time.get_ticks() + random.randint(
        alien_min_shot_interval_ms, alien_max_shot_interval_ms
    )

    explosion_list = []
    pre_fire_duration_ms = 400

    # Enemy Movement (nested correctly)
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

    # Level Up
    def level_up():
        nonlocal current_level, enemy_horizontal_speed, current_level_alien_version
        current_level += 1
        enemy_horizontal_speed += 0.2

        # New version each level
        current_level_alien_version = random.choice(ALIEN_VERSIONS)

        spawn_enemies()

    # Alien Shooting (schedule pre-fire)
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

    # Draw Explosions
    def draw_explosions():
        for explosion in explosion_list[:]:
            pygame.draw.circle(screen, YELLOW, explosion['pos'], explosion['radius'])
            explosion['radius'] -= 0.5
            if explosion['radius'] <= 0:
                explosion_list.remove(explosion)

    # Main Game Loop
    running = True
    while running:
        current_time = pygame.time.get_ticks()

        screen.blit(background_image, (0, 0))

        # Alien shooting timer
        if current_time >= next_alien_shot_timestamp:
            schedule_alien_shot(current_time)
            next_alien_shot_timestamp = current_time + random.randint(
                alien_min_shot_interval_ms, alien_max_shot_interval_ms
            )

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                if event.key == pygame.K_SPACE:
                    if current_time - last_player_shot_timestamp > player_shot_cooldown_ms:
                        player_bullet_list.append(
                            [player_position_x + player_ship_width // 2, player_position_y]
                        )
                        last_player_shot_timestamp = current_time

        # Player Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_position_x > 0:
            player_position_x -= player_movement_speed
        if keys[pygame.K_RIGHT] and player_position_x < SCREEN_WIDTH - player_ship_width:
            player_position_x += player_movement_speed

        # Player Animation
        if player_frames:
            player_animation_timer += player_animation_speed
            if player_animation_timer >= 1:
                player_animation_timer = 0
                current_player_frame_index += player_animation_direction

                if current_player_frame_index == len(player_frames) - 1:
                    player_animation_direction = -1
                elif current_player_frame_index == 0:
                    player_animation_direction = 1

            current_frame_image = player_frames[current_player_frame_index]
            screen.blit(current_frame_image, (player_position_x, player_position_y))

        # Tighter hitbox
        player_rect = pygame.Rect(
            player_position_x + 10,
            player_position_y + 10,
            player_ship_width - 20,
            player_ship_height - 20
        )

        # Player Bullets
        for bullet in player_bullet_list[:]:
            bullet[1] -= bullet_vertical_speed
            if bullet[1] < 0:
                player_bullet_list.remove(bullet)
            else:
                pygame.draw.rect(screen, WHITE, (bullet[0], bullet[1], 5, 10))

        # Alien Pre-Fire Animation + Shooting
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
                        alien_bullet_list.append({'pos': [shot_x, shot_y], 'color': GREEN, 'radius': 8})
                    else:
                        alien_bullet_list.append({'pos': [shot_x, shot_y], 'color': RED, 'radius': 4})

                    enemy["pending_shot_type"] = None

        # Alien Bullets
        for bullet in alien_bullet_list[:]:
            bullet['pos'][1] += bullet_vertical_speed

            # Green bombs track the player
            if bullet['color'] == GREEN:
                if bullet['pos'][0] < player_position_x:
                    bullet['pos'][0] += 1
                elif bullet['pos'][0] > player_position_x:
                    bullet['pos'][0] -= 1

            if bullet['pos'][1] > SCREEN_HEIGHT:
                alien_bullet_list.remove(bullet)
                continue

            pygame.draw.circle(screen, bullet['color'], bullet['pos'], bullet['radius'])

            # Green bomb explosion
            if bullet['color'] == GREEN and bullet['pos'][1] >= player_position_y:
                explosion_center = [bullet['pos'][0], player_position_y + player_ship_height // 2]
                explosion_list.append({'pos': explosion_center, 'radius': 40})
                alien_bullet_list.remove(bullet)

                dx = abs(explosion_center[0] - player_rect.centerx)
                dy = abs(explosion_center[1] - player_rect.centery)

                if dx <= player_rect.width // 2 + 40 and dy <= player_rect.height // 2 + 40:
                    player_lives -= 1
                    player_position_x = SCREEN_WIDTH // 2 - player_ship_width // 2
                    if player_lives <= 0:
                        game_over_screen()
                        return
                continue

        # Move Enemies
       
        move_enemies()

        # Draw Enemies + Track Rects
        enemy_rect_list = []
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

        # Bullet Collision with Enemies
        for bullet in player_bullet_list[:]:
            bullet_rect = pygame.Rect(bullet[0], bullet[1], 5, 10)
            for enemy, enemy_rect in zip(enemy_list[:], enemy_rect_list[:]):
                if enemy_rect.colliderect(bullet_rect):
                    enemy_list.remove(enemy)
                    player_bullet_list.remove(bullet)
                    enemy_rect_list.remove(enemy_rect)
                    break

        # Enemy Collision with Player
        for enemy_rect in enemy_rect_list:
            if enemy_rect.colliderect(player_rect):
                game_over_screen()
                return

        # Enemies Reach Bottom
        for enemy in enemy_list:
            color = enemy["color"]
            version = enemy["version"]
            frame = alien_sprites[color][version][0]
            alien_height = frame.get_height()
            if enemy["y"] + alien_height >= player_position_y:
                game_over_screen()
                return

        # Level Complete
        if not enemy_list:
            level_up()
            waiting = True
            while waiting:
                screen.blit(background_image, (0, 0))
                msg = font.render("Level Complete!", True, WHITE)
                msg2 = small_font.render("Press ENTER for next level or ESC to quit", True, WHITE)
                screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 250))
                screen.blit(msg2, (SCREEN_WIDTH//2 - msg2.get_width()//2, 320))
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            waiting = False
                        if event.key == pygame.K_ESCAPE:
                            return

        # Red Bullet Direct Hit
        for bullet in alien_bullet_list[:]:
            if bullet['color'] == RED:
                if player_rect.collidepoint(bullet['pos'][0], bullet['pos'][1]):
                    alien_bullet_list.remove(bullet)
                    player_lives -= 1
                    player_position_x = SCREEN_WIDTH // 2 - player_ship_width // 2
                    if player_lives <= 0:
                        game_over_screen()
                        return

        # HUD
        lives_text = small_font.render(f"Lives: {player_lives}", True, WHITE)
        screen.blit(lives_text, (10, 10))

        level_text = small_font.render(f"Level: {current_level}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH - 120, 10))

        draw_explosions()

        pygame.display.flip()
        clock.tick(120)

# Game Over Screen
def game_over_screen():
    while True:
        screen.blit(background_image, (0, 0))
        over_text = font.render("Game Over!", True, WHITE)
        prompt_text = small_font.render("Press ENTER to Restart or ESC to Quit", True, WHITE)

        screen.blit(over_text, (SCREEN_WIDTH//2 - over_text.get_width()//2, SCREEN_HEIGHT//2 - 40))
        screen.blit(prompt_text, (SCREEN_WIDTH//2 - prompt_text.get_width()//2, SCREEN_HEIGHT//2 + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game()
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


# Start Game
if __name__ == "__main__":
    main_menu()

