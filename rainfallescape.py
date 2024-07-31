import pygame
import random
import time
import sys

# Configuration
WIDTH, HEIGHT = 360, 640
FPS = 60
ACC = 1.2
FRIC = -0.10
GAME_DURATION = 30  # Game duration in seconds

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("It's Raining")
clock = pygame.time.Clock()

# Load assets
bg_image = pygame.image.load("bg.png").convert()
font = pygame.font.Font(None, 40)
menu_bg_image = pygame.image.load("bg.jpg").convert()  # Replace with your main menu background image path
top_image = pygame.image.load("top.png").convert_alpha()
top_image = pygame.transform.scale(top_image, (WIDTH, 100))

# Button class with border
class Button:
    def __init__(self, x, y, width, height, text, font, bg_color, text_color, border_color=None, border_width=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width
        self.draw_button()

    def draw_button(self):
        # Draw the button background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        # Draw the button text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        # Draw the button border if specified
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)

    def is_clicked(self, event):
        return self.rect.collidepoint(event.pos)


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, player_img):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.pos = pygame.math.Vector2(self.rect.center)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)

    def update(self):
        self.acc = pygame.math.Vector2(0, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acc.x = -ACC
        if keys[pygame.K_RIGHT]:
            self.acc.x = ACC
        if keys[pygame.K_UP]:
            self.acc.y = -ACC
        if keys[pygame.K_DOWN]:
            self.acc.y = ACC

        self.acc += self.vel * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH:
            self.pos.x = WIDTH
        if self.pos.x < 0:
            self.pos.x = 0
        if self.pos.y > HEIGHT:
            self.pos.y = HEIGHT
        if self.pos.y < 0:
            self.pos.y = 0

        self.rect.center = self.pos

# Raindrop class
class Raindrop(pygame.sprite.Sprite):
    def __init__(self, raindrop_img):
        super().__init__()
        self.image = raindrop_img
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.uniform(2.5, 6)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.reset()

def game_loop(player_img_path, raindrop_img_path, is_score_time_based):
    player_img = pygame.image.load(player_img_path).convert_alpha()
    player_img = pygame.transform.scale(player_img, (50, 50))
    raindrop_img = pygame.image.load(raindrop_img_path).convert_alpha()
    raindrop_img = pygame.transform.scale(raindrop_img, (20, 20))

    player = Player(player_img)
    raindrops = pygame.sprite.Group()
    for _ in range(10):
        raindrops.add(Raindrop(raindrop_img))
    all_sprites = pygame.sprite.Group(player, *raindrops)

    running = True
    score = 0
    best_score = 0
    game_over = False
    start_time = None
    frame_count = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Press Enter to restart
                        game_over = False
                        score = 0
                        frame_count = 0
                        player.rect.center = (WIDTH // 2, HEIGHT - 50)
                        for raindrop in raindrops:
                            raindrop.reset()
                        start_time = time.time()
                    if event.key == pygame.K_q:  # Press Q to go back to the main menu
                        return

        if not game_over:
            if start_time is None:
                start_time = time.time()

            current_time = time.time()
            elapsed_time = current_time - start_time
            remaining_time = max(0, GAME_DURATION - elapsed_time)

            if is_score_time_based:
                if remaining_time == 0:
                    game_over = True
                    best_score = max(best_score, score)
            else:
                frame_count += 1
                if frame_count % 10 == 0:
                    score += 1

            hit = pygame.sprite.spritecollideany(player, raindrops)
            if hit:
                if is_score_time_based:
                    score += 1
                    hit.reset()
                else:
                    best_score = max(best_score, score)
                    game_over = True
                    time.sleep(0.5)

            all_sprites.update()

        screen.blit(bg_image, (0, 0))
        all_sprites.draw(screen)

        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        best_score_text = font.render(f"Best: {best_score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(best_score_text, (10, 50))
        if is_score_time_based:
            time_text = font.render(f"Time: {int(remaining_time)}", True, (0, 0, 0))
            screen.blit(time_text, (WIDTH - 115, 10))

        if game_over:
            game_over_text1 = font.render("Game Over!" if not is_score_time_based else "Time's Up!", True, (255, 0, 0))
            game_over_text2 = font.render("Press Enter to restart", True, (255, 0, 0))
            game_over_text3 = font.render("or Q to go back", True, (255, 0, 0))
            screen.blit(game_over_text1, (WIDTH // 2 - game_over_text1.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(game_over_text2, (WIDTH // 2 - game_over_text2.get_width() // 2, HEIGHT // 2))
            screen.blit(game_over_text3, (WIDTH // 2 - game_over_text3.get_width() // 2, HEIGHT // 2 + 40))


        pygame.display.flip()
        clock.tick(FPS)


# Initialize buttons with border
button_font = pygame.font.Font(pygame.font.match_font('arialbd'), 40)  # Use Arial Bold or similar
umbrella_button = Button(
    WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 70,
    "Use Umbrella", button_font, 
    (229, 228, 226), (0, 0, 0), (0, 0, 0), 3  # Border color: black, width: 3
)
running_button = Button(
    WIDTH // 2 - 150, HEIGHT // 2 + 90, 300, 70,
    "Run !!!", button_font, 
    (229, 228, 226), (0, 0, 0), (0, 0, 0), 3  # Border color: black, width: 3
)



# Main menu loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if umbrella_button.is_clicked(event):
                game_loop("umbrella.png", "rain.png", is_score_time_based=True)
            if running_button.is_clicked(event):
                game_loop("player1.jpg", "rain.png", is_score_time_based=False)

    screen.blit(menu_bg_image, (0, 0))
    screen.blit(top_image, (0, 70))
    umbrella_button.draw_button()
    running_button.draw_button()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
