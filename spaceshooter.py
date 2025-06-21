import pygame
import random
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_DURATION_SECONDS = 120

# Colors
BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)

# Player settings
PLAYER_ACCELERATION = 0.4
PLAYER_FRICTION = -0.04
PLAYER_TURN_SPEED = 4.5

# --- Star Field ---
NUM_STARS = 120
star_field = [
    (
        random.randint(0, SCREEN_WIDTH),
        random.randint(0, SCREEN_HEIGHT),
        random.randint(80, 255)  # brightness
    )
    for _ in range(NUM_STARS)
]

# --- Asset Loader ---
def load_image(filename, scale_x, scale_y):
    """Loads, scales, and handles errors for an image."""
    try:
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.scale(image, (scale_x, scale_y))
        return image
    except pygame.error as e:
        print(f"Unable to load image: {filename}. Make sure it's in the same folder.")
        print(e)
        sys.exit()

# --- Classes ---

class Player(pygame.sprite.Sprite):
    """Represents a player's spaceship."""
    def __init__(self, x, y, image, controls, start_pos):
        super().__init__()
        self.original_image = image
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        
        self.controls = controls
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.angle = 0
        
        self.score = 0
        self.start_pos = start_pos
        
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 250

        self.laser_count = 1
        self.max_lasers = 5  # Optional: limit max lasers

    def update(self, gamepad=None):
        self.acc = pygame.math.Vector2(0, 0)
        keys = pygame.key.get_pressed()
        used_gamepad = False

        # --- Gamepad controls ---
        if gamepad:
            axis_x = gamepad.get_axis(0)
            axis_y = gamepad.get_axis(1)
            # Deadzone
            if abs(axis_x) > 0.15:
                self.angle -= axis_x * PLAYER_TURN_SPEED * 1.5
                used_gamepad = True
            if abs(axis_y) > 0.15:
                self.acc = pygame.math.Vector2(0, -PLAYER_ACCELERATION * -axis_y).rotate(-self.angle)
                used_gamepad = True
            # A button (usually 0)
            if gamepad.get_button(0):
                self.shoot()
                used_gamepad = True

        # --- Keyboard fallback ---
        if not used_gamepad:
            if keys[self.controls['left']]:
                self.angle += PLAYER_TURN_SPEED
            if keys[self.controls['right']]:
                self.angle -= PLAYER_TURN_SPEED
            if keys[self.controls['up']]:
                self.acc = pygame.math.Vector2(0, -PLAYER_ACCELERATION).rotate(-self.angle)
            if keys[self.controls['fire']]:
                self.shoot()

        # Apply friction & update motion
        self.acc += self.vel * PLAYER_FRICTION
        self.vel += self.acc
        self.pos += self.vel

        # Keep player within screen boundaries (wrap around)
        if self.pos.x > SCREEN_WIDTH: self.pos.x = 0
        if self.pos.x < 0: self.pos.x = SCREEN_WIDTH
        if self.pos.y > SCREEN_HEIGHT: self.pos.y = 0
        if self.pos.y < 0: self.pos.y = SCREEN_HEIGHT

        # Update image rotation and rect
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.pos)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            # Fan out lasers, centered on the ship's facing direction
            spread = 25  # total spread angle in degrees
            count = self.laser_count
            if count == 1:
                angles = [self.angle]
            else:
                angles = [self.angle + spread/2 - i*(spread/(count-1)) for i in range(count)]
            for ang in angles:
                projectile = Projectile(self.rect.center, ang, self)
                all_sprites.add(projectile)
                projectiles.add(projectile)
            laser_sound.play()

    def reset(self):
        self.pos = pygame.math.Vector2(self.start_pos)
        self.vel = pygame.math.Vector2(0, 0)
        self.angle = 0

class Asteroid(pygame.sprite.Sprite):
    """Represents a floating asteroid."""
    def __init__(self):
        super().__init__()
        self.original_image = asteroid_img
        self.image = self.original_image.copy()
        
        # Spawn on edges
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x, y = random.randrange(SCREEN_WIDTH), 0
        elif side == 'bottom':
            x, y = random.randrange(SCREEN_WIDTH), SCREEN_HEIGHT
        elif side == 'left':
            x, y = 0, random.randrange(SCREEN_HEIGHT)
        else: # right
            x, y = SCREEN_WIDTH, random.randrange(SCREEN_HEIGHT)

        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        self.rot = 0
        self.rot_speed = random.randrange(-3, 3)

    def update(self):
        self.pos += self.vel
        self.rot = (self.rot + self.rot_speed) % 360
        
        # Wrap around screen
        if self.pos.x > SCREEN_WIDTH + 20: self.pos.x = -20
        if self.pos.x < -20: self.pos.x = SCREEN_WIDTH + 20
        if self.pos.y > SCREEN_HEIGHT + 20: self.pos.y = -20
        if self.pos.y < -20: self.pos.y = SCREEN_HEIGHT + 20

        self.image = pygame.transform.rotate(self.original_image, self.rot)
        self.rect = self.image.get_rect(center=self.pos)

class Projectile(pygame.sprite.Sprite):
    """Represents a laser beam."""
    def __init__(self, pos, angle, owner):
        super().__init__()
        # Create a base image for the laser that can be rotated
        self.original_image = pygame.Surface((5, 20), pygame.SRCALPHA)
        self.original_image.fill(RED)
        
        # Rotate the image to match the ship's angle
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=pos)
        
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(0, -10).rotate(-angle)
        self.owner = owner

    def update(self):
        self.pos += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        # Kill if it moves off-screen
        if not screen.get_rect().contains(self.rect):
            self.kill()

class Explosion(pygame.sprite.Sprite):
    """Represents an explosion animation."""
    def __init__(self, center, size=60):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 250  # milliseconds

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.spawn_time
        if elapsed > self.duration:
            self.kill()
            return

        progress = elapsed / self.duration
        radius = int((self.size // 12) + progress * (self.size // 2))  # Scales with size
        alpha = 255 - int(progress * 255)

        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (*ORANGE, alpha), (self.size // 2, self.size // 2), radius)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 200, 255), (12, 12), 12)
        pygame.draw.circle(self.image, (255, 255, 0), (12, 12), 8)
        self.rect = self.image.get_rect(center=(random.randint(40, SCREEN_WIDTH-40), random.randint(40, SCREEN_HEIGHT-40)))
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 8000  # milliseconds

    def update(self):
        # Power-up disappears after some time
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()

def draw_text(surf, text, size, x, y, color):
    font = pygame.font.Font(pygame.font.match_font('arial'), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surf.blit(text_surface, text_rect)

def spawn_asteroid():
    a = Asteroid()
    all_sprites.add(a)
    asteroids.add(a)

def spawn_powerup():
    pu = PowerUp()
    all_sprites.add(pu)
    powerups.add(pu)

def show_start_screen():
    """Displays the initial screen with instructions."""
    screen.fill(BLACK)
    draw_text(screen, "ASTEROID SHOOTER", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, WHITE)
    draw_text(screen, "Player 1: W (Up), A (Left), D (Right), F (Shoot)", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 60, WHITE)
    draw_text(screen, "Player 2: Arrow Keys (Up, Left, Right), Right Shift (Shoot)", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 20, WHITE)
    draw_text(screen, "Collect Power-Ups to shoot more lasers!", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20, WHITE)
    draw_text(screen, "Avoid Asteroids or you'll lose your lasers!", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60, WHITE)
    draw_text(screen, "The player with the most asteroids destroyed wins!", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, WHITE)
    draw_text(screen, "Press SPACE to start", 32, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4, GREEN)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

def show_difficulty_screen():
    """Displays the difficulty selection screen."""
    screen.fill(BLACK)
    draw_text(screen, "SELECT DIFFICULTY", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, WHITE)
    draw_text(screen, "Press 1 for EASY", 32, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40, GREEN)
    draw_text(screen, "Press 2 for MEDIUM", 32, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, ORANGE)
    draw_text(screen, "Press 3 for HARD", 32, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40, RED)
    pygame.display.flip()

    waiting = True
    difficulty = None
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    difficulty = "easy"
                    waiting = False
                elif event.key == pygame.K_2:
                    difficulty = "medium"
                    waiting = False
                elif event.key == pygame.K_3:
                    difficulty = "hard"
                    waiting = False
    return difficulty

def show_replay_screen(winner):
    """Displays the replay screen."""
    screen.fill(BLACK)
    if winner:
        draw_text(screen, f"{winner} WINS!", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, WHITE)
    else:
        draw_text(screen, "GAME OVER!", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, WHITE)
    draw_text(screen, "Press SPACE to replay", 32, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, GREEN)
    draw_text(screen, "Press ESC to quit", 32, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40, RED)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                    return True  # Replay
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    return False

def reset_game():
    """Resets the game state for replay."""
    global all_sprites, players, asteroids, projectiles, powerups
    all_sprites.empty()
    players.empty()
    asteroids.empty()
    projectiles.empty()
    powerups.empty()

    # Recreate players
    player1.reset()
    player2.reset()
    all_sprites.add(player1, player2)
    players.add(player1, player2)

    # Spawn asteroids based on difficulty
    for _ in range(num_asteroids):
        spawn_asteroid()

# --- Initialization ---
pygame.init()
pygame.mixer.init()

pygame.joystick.init()
gamepads = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for pad in gamepads:
    pad.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Asteroid Shooter")
clock = pygame.time.Clock()

pygame.mixer.music.load("space_shooter_loop.wav")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

# Load assets
player1_img = load_image("player1.png", 50, 40)
player2_img = load_image("player2.png", 50, 40)
asteroid_img = load_image("asteroid.png", 40, 40)

# Load sounds
laser_sound = pygame.mixer.Sound("laser.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")
powerup_sound = pygame.mixer.Sound("powerup.wav")

# Create sprite groups
all_sprites = pygame.sprite.Group()
players = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# Create players
player1_controls = {'up': pygame.K_w, 'left': pygame.K_a, 'right': pygame.K_d, 'fire': pygame.K_f}
player2_controls = {'up': pygame.K_UP, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'fire': pygame.K_RSHIFT}

player1_start_pos = (SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2)
player2_start_pos = (SCREEN_WIDTH * 3 / 4, SCREEN_HEIGHT / 2)

player1 = Player(player1_start_pos[0], player1_start_pos[1], player1_img, player1_controls, player1_start_pos)
player2 = Player(player2_start_pos[0], player2_start_pos[1], player2_img, player2_controls, player2_start_pos)

all_sprites.add(player1, player2)
players.add(player1, player2)

# Show the start screen
show_start_screen()

# Show difficulty selection screen
# --- Difficulty Settings ---
difficulty_settings = {
    "easy": 5,    # Number of asteroids
    "medium": 10,
    "hard": 15
}
difficulty = show_difficulty_screen()
if difficulty is None:
    print("No difficulty selected. Default to easy.")
    difficulty = "easy"
num_asteroids = difficulty_settings[difficulty]
for _ in range(num_asteroids):
    spawn_asteroid()

# --- Game Loop ---
running = True
game_over = False
winner = None
start_ticks = pygame.time.get_ticks()
last_powerup = pygame.time.get_ticks()
POWERUP_INTERVAL = 10000  # ms
seconds_left = GAME_DURATION_SECONDS  # Initialize to avoid unbound error

while running:
    clock.tick(FPS)

    # Check if the game is over
    if game_over:
        replay = show_replay_screen(winner)
        if replay:
            difficulty = show_difficulty_screen()
            if difficulty is None:
                print("No difficulty selected. Default to easy.")
                difficulty = "easy"
            num_asteroids = difficulty_settings[difficulty]
            reset_game()
            game_over = False
            winner = None
            start_ticks = pygame.time.get_ticks()
            last_powerup = pygame.time.get_ticks()
            seconds_left = GAME_DURATION_SECONDS
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    # --- Update ---
    if not game_over:
        # Pass gamepad to each player if available
        if len(gamepads) >= 2:
            player1.update(gamepad=gamepads[0])
            player2.update(gamepad=gamepads[1])
        elif len(gamepads) == 1:
            player1.update(gamepad=gamepads[0])
            player2.update()
        else:
            player1.update()
            player2.update()
        # Update other sprites
        for sprite in all_sprites:
            if not isinstance(sprite, Player):
                sprite.update()

        all_sprites.update()

        now = pygame.time.get_ticks()
        if now - last_powerup > POWERUP_INTERVAL:
            spawn_powerup()
            last_powerup = now

        # Power-up collection
        for player in players:
            hits = pygame.sprite.spritecollide(player, powerups, True)
            for _ in hits:
                if player.laser_count < player.max_lasers:
                    powerup_sound.play()
                    player.laser_count += 1

        # Check timer
        seconds_left = GAME_DURATION_SECONDS - (pygame.time.get_ticks() - start_ticks) / 1000
        if seconds_left <= 0:
            game_over = True
            if player1.score > player2.score:
                winner = "Player 1 WINS!"
            elif player2.score > player1.score:
                winner = "Player 2 WINS!"
            else:
                winner = "It's a TIE!"

        # --- Collisions ---
        # Asteroid-asteroid collision and bounce
        asteroid_list = list(asteroids)
        for i in range(len(asteroid_list)):
            for j in range(i + 1, len(asteroid_list)):
                a1 = asteroid_list[i]
                a2 = asteroid_list[j]
                if a1.rect.colliderect(a2.rect):
                    # Calculate the direction vector between asteroids
                    delta = a1.pos - a2.pos
                    distance = delta.length() or 1  # Avoid division by zero
                    min_dist = (a1.rect.width + a2.rect.width) / 2
                    if distance < min_dist:
                        # Normalize direction
                        direction = delta.normalize()
                        # Simple elastic collision: swap velocities along the direction vector
                        v1 = a1.vel.project(direction)
                        v2 = a2.vel.project(direction)
                        a1.vel += (v2 - v1)
                        a2.vel += (v1 - v2)
                        # Push them apart so they don't stick
                        overlap = min_dist - distance
                        a1.pos += direction * (overlap / 2)
                        a2.pos -= direction * (overlap / 2)
                        a1.rect.center = a1.pos
                        a2.rect.center = a2.pos

        # Player vs Asteroids
        for player in players:
            collided_asteroids = pygame.sprite.spritecollide(player, asteroids, True, pygame.sprite.collide_circle)
            if collided_asteroids:
                # Big explosion at player
                big_expl = Explosion(player.rect.center, size=120)
                all_sprites.add(big_expl)
                explosion_sound.play()
                if difficulty != "easy":
                    player.laser_count = 1  # Reset laser count
                player.reset()
                # --- Gamepad rumble ---
                # Find which gamepad is assigned to this player
                player_idx = 0 if player == player1 else 1
                if len(gamepads) > player_idx:
                    try:
                        gamepads[player_idx].rumble(0.8, 0.8, 400)  # strong, weak, duration(ms)
                    except Exception as e:
                        print("Rumble not supported:", e)
                # Explode and respawn each asteroid that hit the player
                for asteroid in collided_asteroids:
                    expl = Explosion(asteroid.rect.center)
                    all_sprites.add(expl)
                    explosion_sound.play()
                    spawn_asteroid()

        # Projectiles vs Asteroids
        hits = pygame.sprite.groupcollide(projectiles, asteroids, True, True)
        for projectile, hit_asteroids in hits.items():
            projectile.owner.score += len(hit_asteroids)
            for asteroid in hit_asteroids:
                expl = Explosion(asteroid.rect.center)
                all_sprites.add(expl)
                explosion_sound.play()
                spawn_asteroid()

    # --- Drawing ---
    screen.fill(BLACK)
    # Draw star field
    for x, y, brightness in star_field:
        screen.set_at((x, y), (brightness, brightness, brightness))

    all_sprites.draw(screen)

    # Draw UI (fixed position)
    draw_text(screen, f"P1 Score: {player1.score}", 22, 100, 20, WHITE)
    draw_text(screen, f"P2 Score: {player2.score}", 22, SCREEN_WIDTH - 100, 20, WHITE)
    
    if not game_over:
        draw_text(screen, f"Time: {int(seconds_left)}", 22, SCREEN_WIDTH / 2, 20, WHITE)
    else:
        draw_text(screen, f"{winner}", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50, GREEN)
        draw_text(screen, "Press ESC to quit", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, WHITE)

    pygame.display.flip()