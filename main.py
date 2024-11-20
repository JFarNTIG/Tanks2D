import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("2D Tanks Game")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 177, 76)
RED = (255, 0, 0)

# Terrain generation function
def generate_terrain():
    terrain = []
    num_points = 100
    dx = screen_width // (num_points - 1)
    previous_height = random.randint(screen_height // 2, screen_height - 50)
    for i in range(num_points):
        x = i * dx
        delta_height = random.randint(-30, 30)
        y = previous_height + delta_height
        y = min(max(y, screen_height // 2), screen_height - 50)
        terrain.append((x, y))
        previous_height = y
    return terrain

# Draw terrain
def draw_terrain(terrain):
    pygame.draw.polygon(screen, GREEN, terrain + [(screen_width, screen_height), (0, screen_height)])

class Tank:
    def __init__(self, x, y, color=BLACK, enemy=False):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 20
        self.color = color
        self.health = 100
        self.angle = 45
        self.power = 50
        self.enemy = enemy

    def draw(self, screen):
        # Draw tank body
        pygame.draw.rect(screen, self.color, (self.x - self.width // 2, self.y - self.height, self.width, self.height))
        # Draw tank barrel
        barrel_length = 30
        if self.enemy:
            barrel_angle = 180 - self.angle
        else:
            barrel_angle = self.angle
        end_x = self.x + barrel_length * math.cos(math.radians(barrel_angle))
        end_y = self.y - self.height - barrel_length * math.sin(math.radians(barrel_angle))
        pygame.draw.line(screen, self.color, (self.x, self.y - self.height), (end_x, end_y), 5)

# Projectile class
class Projectile:
    def __init__(self, x, y, angle, power):
        self.initial_x = x
        self.initial_y = y
        self.x = x
        self.y = y
        self.angle = angle
        self.power = power
        self.time = 0
        self.gravity = 9.8 * 2  # Increased gravity for game effect

    def update(self, dt):
        self.time += dt * 2  # Speed up time for game effect
        angle_rad = math.radians(self.angle)
        self.x = self.initial_x + self.power * math.cos(angle_rad) * self.time
        self.y = self.initial_y - (self.power * math.sin(angle_rad) * self.time - 0.5 * self.gravity * self.time ** 2)

    def draw(self, screen):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), 5)

# Helper functions
def get_tank_positions(terrain):
    player_x, player_y = terrain[5]
    enemy_x, enemy_y = terrain[-6]
    return (player_x, player_y), (enemy_x, enemy_y)

def get_terrain_height_at_x(terrain, x):
    for i in range(len(terrain) - 1):
        x1, y1 = terrain[i]
        x2, y2 = terrain[i + 1]
        if x1 <= x <= x2:
            y = y1 + (y2 - y1) * (x - x1) / (x2 - x1)
            return y
    return screen_height

def calculate_damage(proj_x, proj_y, tank):
    dist = math.hypot(proj_x - tank.x, proj_y - tank.y)
    if dist < 20:
        return 50
    elif dist < 40:
        return 30
    elif dist < 60:
        return 10
    else:
        return 0

def check_collision(projectile, terrain, player_tank, enemy_tank, current_player):
    if projectile.x < 0 or projectile.x > screen_width or projectile.y > screen_height:
        return True

    terrain_y = get_terrain_height_at_x(terrain, projectile.x)
    if projectile.y >= terrain_y:
        return True

    if current_player == 'player':
        if (enemy_tank.x - enemy_tank.width // 2 <= projectile.x <= enemy_tank.x + enemy_tank.width // 2 and
            enemy_tank.y - enemy_tank.height <= projectile.y <= enemy_tank.y):
            damage = calculate_damage(projectile.x, projectile.y, enemy_tank)
            enemy_tank.health -= damage
            return True
    else:
        if (player_tank.x - player_tank.width // 2 <= projectile.x <= player_tank.x + player_tank.width // 2 and
            player_tank.y - player_tank.height <= projectile.y <= player_tank.y):
            damage = calculate_damage(projectile.x, projectile.y, player_tank)
            player_tank.health -= damage
            return True
    return False

def draw_health_bars(player_tank, enemy_tank):
    pygame.draw.rect(screen, RED, (20, 20, 100, 10))
    pygame.draw.rect(screen, GREEN, (20, 20, player_tank.health, 10))
    pygame.draw.rect(screen, RED, (screen_width - 120, 20, 100, 10))
    pygame.draw.rect(screen, GREEN, (screen_width - 120, 20, enemy_tank.health, 10))

# Game initialization
terrain = generate_terrain()
(player_x, player_y), (enemy_x, enemy_y) = get_tank_positions(terrain)
player_tank = Tank(player_x, player_y, color=BLACK)
enemy_tank = Tank(enemy_x, enemy_y, color=RED, enemy=True)
projectile = None
running = True
clock = pygame.time.Clock()
current_player = 'player'
font = pygame.font.SysFont(None, 24)

# Game loop
while running:
    dt = clock.tick(30) / 500.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input handling
    if projectile is None:
        if current_player == 'player':
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player_tank.angle = min(player_tank.angle + 1, 90)
            if keys[pygame.K_RIGHT]:
                player_tank.angle = max(player_tank.angle - 1, 0)
            if keys[pygame.K_UP]:
                player_tank.power = min(player_tank.power + 1, 250)
            if keys[pygame.K_DOWN]:
                player_tank.power = max(player_tank.power - 1, 10)
            if keys[pygame.K_SPACE]:
                projectile = Projectile(player_tank.x, player_tank.y - player_tank.height, player_tank.angle, player_tank.power)
        elif current_player == 'enemy':
            enemy_tank.angle = random.randint(20, 90)
            enemy_tank.power = random.randint(40, 220)
            projectile = Projectile(enemy_tank.x, enemy_tank.y - enemy_tank.height, 180 - enemy_tank.angle, enemy_tank.power)
    else:
        projectile.update(dt)
        if check_collision(projectile, terrain, player_tank, enemy_tank, current_player):
            projectile = None
            if current_player == 'player':
                current_player = 'enemy'
            else:
                current_player = 'player'

    if player_tank.health <= 0 or enemy_tank.health <= 0:
        running = False

    # Drawing code
    screen.fill(WHITE)
    draw_terrain(terrain)
    player_tank.draw(screen)
    enemy_tank.draw(screen)
    draw_health_bars(player_tank, enemy_tank)

    angle_text = font.render(f"Angle: {player_tank.angle}", True, BLACK)
    power_text = font.render(f"Power: {player_tank.power}", True, BLACK)
    screen.blit(angle_text, (20, 40))
    screen.blit(power_text, (20, 60))

    if projectile:
        projectile.draw(screen)

    pygame.display.flip()

# Game Over screen
game_over_text = font.render("Game Over", True, RED)
winner = "Player" if enemy_tank.health <= 0 else "Enemy"
winner_text = font.render(f"{winner} Wins!", True, RED)
screen.blit(game_over_text, (screen_width / 2 - 50, screen_height / 2 - 20))
screen.blit(winner_text, (screen_width / 2 - 50, screen_height / 2 + 20))
pygame.display.flip()
pygame.time.wait(3000)
pygame.quit()
