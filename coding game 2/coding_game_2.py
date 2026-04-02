import pygame
import sys
import random

pygame.init()

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

SHIP_COLORS = {
    "Green": GREEN,
    "Blue": BLUE,
    "Yellow": YELLOW,
    "Red": RED
}

selected_ship_color = GREEN

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")
font = pygame.font.SysFont(None, 50)
small_font = pygame.font.SysFont(None, 30)
clock = pygame.time.Clock()

player_lives = 3
pygame.mixer.music.set_volume(0.5)

def draw_neon_text(surface, text, font, x, y, base_color):
    glow_colors = [
        (base_color[0]//4, base_color[1]//4, base_color[2]//4),
        (base_color[0]//2, base_color[1]//2, base_color[2]//2),
        base_color
    ]
    for i, color in enumerate(glow_colors):
        glow = font.render(text, True, color)
        offset = 4 - i
        surface.blit(glow, (x - offset, y - offset))
        surface.blit(glow, (x + offset, y - offset))
        surface.blit(glow, (x - offset, y + offset))
        surface.blit(glow, (x + offset, y + offset))
    final = font.render(text, True, WHITE)
    surface.blit(final, (x, y))

class Button:
    def __init__(self, text, x, y, width, height, color, hover_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.rect(surface,
                         self.hover_color if self.rect.collidepoint(mouse_pos) else self.color,
                         self.rect)
        text_surf = font.render(self.text, True, WHITE)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

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

def color_menu():
    global selected_ship_color
    buttons = []
    y = 200
    for name, color in SHIP_COLORS.items():
        buttons.append((name, Button(name, SCREEN_WIDTH//2 - 100, y, 200, 50, color, DARK_GRAY)))
        y += 80
    back_button = Button("Back", SCREEN_WIDTH//2 - 100, 500, 200, 50, GRAY, DARK_GRAY)
    while True:
        screen.fill(BLACK)
        title = font.render("Choose Ship Color", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        for name, btn in buttons:
            btn.draw(screen)
        back_button.draw(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for name, btn in buttons:
                if btn.is_clicked(event):
                    selected_ship_color = SHIP_COLORS[name]
                    return
            if back_button.is_clicked(event):
                return

#main menu
def main_menu():
    play_button = Button("Play", SCREEN_WIDTH//2 - 100, 200, 200, 50, GRAY, DARK_GRAY)
    color_button = Button("Ship Color", SCREEN_WIDTH//2 - 100, 280, 200, 50, GRAY, DARK_GRAY)
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
            if color_button.is_clicked(event):
                color_menu()
            if exit_button.is_clicked(event):
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if abs(event.pos[0] - volume_button.x) < 20 and abs(event.pos[1] - volume_button.y) < 20:
                    volume_button.toggle()
        play_button.draw(screen)
        color_button.draw(screen)
        exit_button.draw(screen)
        volume_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def game():
    global player_lives
    player_lives = 3
    level = 1
    enemy_speed = 2
    enemies = []

    def spawn_enemies():
        enemies.clear()
        rows = min(2 + (level // 5), 6)
        aliens_per_row = 7
        spacing_x = 80
        spacing_y = 60
        start_x = (SCREEN_WIDTH - (aliens_per_row - 1) * spacing_x) // 2
        start_y = 50
        for row in range(rows):
            y = start_y + row * spacing_y
            for col in range(aliens_per_row):
                x = start_x + col * spacing_x
                enemies.append([x, y])

    spawn_enemies()

    player_width = 50
    player_height = 30
    player_x = SCREEN_WIDTH // 2 - player_width // 2
    player_y = SCREEN_HEIGHT - player_height - 10
    player_speed = 5

    bullets = []
    bullet_speed = 7
    enemy_drop = 10
    enemy_direction = 1
    last_shot_time = 0
    shot_cooldown = 300

    alien_bullets = []
    min_shoot_interval = 500
    max_shoot_interval = 1500
    next_shoot_time = pygame.time.get_ticks() + random.randint(min_shoot_interval, max_shoot_interval)

    explosions = []

    def move_enemies():
        nonlocal enemy_direction, enemy_speed
        for e in enemies:
            e[0] += enemy_speed * enemy_direction
        xs = [e[0] for e in enemies]
        if enemies:
            if max(xs) + 40 > SCREEN_WIDTH or min(xs) < 0:
                enemy_direction *= -1
                for e in enemies:
                    e[1] += enemy_drop

    def level_up():
        nonlocal level, enemy_speed
        level += 1
        enemy_speed += 0.5
        spawn_enemies()

    def aliens_shoot():
        if not enemies:
            return
        shooter = random.choice(enemies)
        if random.random() < 0.1:
            alien_bullets.append({'pos': [shooter[0] + 20, shooter[1] + 30], 'color': GREEN, 'radius': 8})
        else:
            alien_bullets.append({'pos': [shooter[0] + 20, shooter[1] + 30], 'color': RED, 'radius': 4})

    def draw_explosions():
        for exp in explosions[:]:
            pygame.draw.circle(screen, YELLOW, exp['pos'], exp['radius'])
            exp['radius'] -= 1
            if exp['radius'] <= 0:
                explosions.remove(exp)

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        screen.fill(BLACK)
        if current_time >= next_shoot_time:
            aliens_shoot()
            next_shoot_time = current_time + random.randint(min_shoot_interval, max_shoot_interval)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    if current_time - last_shot_time > shot_cooldown:
                        bullets.append([player_x + player_width // 2, player_y])
                        last_shot_time = current_time
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - player_width:
            player_x += player_speed
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        pygame.draw.rect(screen, selected_ship_color, player_rect)
        for b in bullets[:]:
            b[1] -= bullet_speed
            if b[1] < 0:
                bullets.remove(b)
            else:
                pygame.draw.rect(screen, WHITE, (b[0], b[1], 5, 10))
        for b in alien_bullets[:]:
            b['pos'][1] += bullet_speed
            if b['color'] == GREEN:
                if b['pos'][0] < player_x:
                    b['pos'][0] += 2
                elif b['pos'][0] > player_x:
                    b['pos'][0] -= 2
            if b['pos'][1] > SCREEN_HEIGHT:
                alien_bullets.remove(b)
                continue
            pygame.draw.circle(screen, b['color'], b['pos'], b['radius'])
            if b['color'] == GREEN and b['pos'][1] >= player_y:
                explosion_center = [b['pos'][0], player_y + player_height // 2]
                explosions.append({'pos': explosion_center, 'radius': 40})
                alien_bullets.remove(b)
                dx = abs(explosion_center[0] - player_rect.centerx)
                dy = abs(explosion_center[1] - player_rect.centery)
                if dx <= player_rect.width // 2 + 40 and dy <= player_rect.height // 2 + 40:
                    player_lives -= 1
                    player_x = SCREEN_WIDTH // 2 - player_width // 2
                    if player_lives <= 0:
                        game_over_screen()
                        return
                continue
        move_enemies()
        enemies_rects = []
        for e in enemies:
            rect = pygame.Rect(e[0], e[1], 40, 30)
            enemies_rects.append(rect)
            pygame.draw.rect(screen, RED, rect)
        for b in bullets[:]:
            b_rect = pygame.Rect(b[0], b[1], 5, 10)
            for e, e_rect in zip(enemies, enemies_rects):
                if e_rect.colliderect(b_rect):
                    enemies.remove(e)
                    bullets.remove(b)
                    break
        for e_rect in enemies_rects:
            if e_rect.colliderect(player_rect):
                game_over_screen()
                return
        for e in enemies:
            if e[1] + 30 >= player_y:
                game_over_screen()
                return
        if not enemies:
            level_up()
            waiting = True
            while waiting:
                screen.fill(BLACK)
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
        for b in alien_bullets[:]:
            if b['color'] == RED:
                if player_rect.collidepoint(b['pos'][0], b['pos'][1]):
                    alien_bullets.remove(b)
                    player_lives -= 1
                    player_x = SCREEN_WIDTH // 2 - player_width // 2
                    if player_lives <= 0:
                        game_over_screen()
                        return
        lives_text = small_font.render(f"Lives: {player_lives}", True, WHITE)
        screen.blit(lives_text, (10, 10))
        level_text = small_font.render(f"Level: {level}", True, WHITE)
        screen.blit(level_text, (700, 10))
        draw_explosions()
        pygame.display.flip()
        clock.tick(60)

def game_over_screen():
    while True:
        screen.fill(BLACK)
        over_text = font.render("Game Over! Press Enter to Restart or ESC to Quit.", True, WHITE)
        screen.blit(over_text, (SCREEN_WIDTH//2 - over_text.get_width()//2, SCREEN_HEIGHT//2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game()
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    main_menu()