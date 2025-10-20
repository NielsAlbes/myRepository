import pygame
import math
import sys
import random
from time import strftime


# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen settings
WIDTH, HEIGHT = 1920, 1280
CENTER = (WIDTH // 2, HEIGHT // 2)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Orbit Animation")
font = pygame.font.SysFont("", 60)

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Colors
BLACK = (5, 5, 20)
WHITE = (255, 255, 255)
SUN_COLOR = (255, 210, 90)
PLANET_COLOR = (110, 160, 240)
TRAIL_COLOR = (70, 110, 180)

# Orbit settings
orbit_radius = 400
angle = 4.5
planet_radius = 15
sun_radius = 40
angular_speed = 0.015
# Trail history
trail = []

stars = []
numberOfStars = 75

for _ in range(numberOfStars):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    velocity = random.randint(1, 2)
    size = velocity
    stars.append([x, y, velocity, size])

def draw_stars():
    for star in stars:
        star[1] += star[2]
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)
            star[2] = random.randint(1, 2)
            star[3] = star[2]
        pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[3])

def draw_sun():
    # Glow effect using multiple circles
    for r in range(100, 0, -15):
        alpha = max(20, 255 - r * 4)
        glow = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 220, 100, alpha), (r, r), r)
        screen.blit(glow, (CENTER[0] - r, CENTER[1] - r))
    pygame.draw.circle(screen, SUN_COLOR, CENTER, sun_radius)

def draw_orbit():
    pygame.draw.circle(screen, (100, 100, 120), CENTER, orbit_radius, 1)

def draw_trail(trail):
    for i, pos in enumerate(trail):
        alpha = int(255 * (i + 1) / len(trail))
        trail_surface = pygame.Surface((planet_radius*2, planet_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(trail_surface, (*TRAIL_COLOR, alpha), (planet_radius, planet_radius), planet_radius)
        screen.blit(trail_surface, (pos[0] - planet_radius, pos[1] - planet_radius))

def draw_planet(x, y):
    # Shadow effect
    pygame.draw.circle(screen, (50, 80, 120), (int(x)+2, int(y)+2), planet_radius)
    pygame.draw.circle(screen, PLANET_COLOR, (int(x), int(y)), planet_radius)

def draw_time(time):
    text = font.render(f"{time}", 0, (220, 220, 220))
    screen.blit(text, (250, 300))
    

# Main loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)
    zeit = strftime("%H:%M:%S")

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Background
    draw_stars()
    draw_orbit()
    draw_sun()
    draw_time(zeit)
    
    # Calculate position
    x = CENTER[0] + orbit_radius * math.cos(angle)
    y = CENTER[1] + orbit_radius * math.sin(angle)
    angle += angular_speed

    # Save trail
    trail.append((x, y))
    if len(trail) > 60:
        trail.pop(0)

    draw_trail(trail)
    draw_planet(x, y)

    pygame.display.flip()

pygame.quit()
sys.exit()