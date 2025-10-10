import pygame as py
import random
import time
import sys
import os

py.init()
py.mixer.init()

width = 1920
height = 1280
screen = py.display.set_mode((width, height))
clock = py.time.Clock()
font = py.font.SysFont("Arial", 80)
font2 = py.font.SysFont("Arial", 30)
last_shot = 0
shot_delay = 250
score = 0
tempo = 0
running = True
current_time = time.time()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

laserSound = py.mixer.Sound(resource_path("assets/laser.mp3"))
ship_img = py.image.load(resource_path("assets/spaceship.png")).convert_alpha()
ship_img = py.transform.scale(ship_img, (100, 75))
asteroid_img = py.image.load(resource_path("assets/asteroid.png")).convert_alpha()
asteroid_img = py.transform.scale(asteroid_img, (60, 50))

stars = []
quantityStars = 150
for _ in range(quantityStars):
    x = random.randint(0, width)
    y = random.randint(0, height)
    velocity = random.randint(1, 3)
    size = velocity 
    stars.append([x, y, velocity, size])

def backgroundWithStars():
    screen.fill((15, 15, 30))
    for star in stars:
        star[1] += star[2]
        if star[1] > height:
            star[0] = random.randint(0, width)
            star[1] = 0
            star[2] = random.randint(1, 3)
            star[3] = star[2]
        py.draw.circle(screen, (240, 250, 240), (star[0], star[1]), star[3])

position = width/2
def starship(x):
    rect = ship_img.get_rect(center=(x, height/2+100))
    screen.blit(ship_img, rect)
    hitbox = rect.inflate(-30, -30)
    return hitbox

quantityAsteroids = 13
asteroids = []
for _ in range(quantityAsteroids):
    x = random.randint(100, width-100)
    y = random.randint(-200, 0)
    velocity = random.randint(2, 6)
    rect = asteroid_img.get_rect(center=(x, y))
    asteroids.append({'x': x, 'y': y, 'velocity': velocity, 'rect': rect})

def showAsteroids():
    asteroid_rects = []
    for asteroid in asteroids:
        asteroid['y'] += asteroid['velocity'] + tempo
        if asteroid['y'] > height:
            asteroid['x'] = random.randint(50, width-50)
            asteroid['y'] = 0
            if asteroid['velocity'] < 18:
                asteroid['velocity'] += random.randint(0,1)
        
        asteroid['rect'].center = (asteroid['x'], asteroid['y'])
        screen.blit(asteroid_img, asteroid['rect'])

        asteroid_rects.append(asteroid['rect'])
    return asteroid_rects

laser_rects = []
def fireLaser():
    for laser in laser_rects[:]:
        laser.y -= 20
        if laser.y < 0:
            laser_rects.remove(laser)
        else:
            py.draw.rect(screen, (255, 120, 50), laser)

while running:
    
    for event in py.event.get():
        if event.type == py.QUIT:
            running = False
    keys = py.key.get_pressed()
    
    if keys[py.K_LEFT] and position > 60:
        position -= 15
    elif keys[py.K_RIGHT] and position < width-60:
        position += 15
    elif keys[py.K_UP]:
        now = py.time.get_ticks()
        if now - last_shot > shot_delay:
            laser_rects.append(py.Rect(position-2, height/2, 4, 40))
            laserSound.play()
            last_shot = now
    elif keys[py.K_DOWN] and tempo < 2:
        tempo += 0.1

    backgroundWithStars()
    asteroidHitbox = showAsteroids()
    starshipHitbox = starship(position)
    fireLaser()
    
    text = font.render("Game Over!", False, (255, 255, 255))
    
    text2 = font2.render(f"Score: {score}", False, (255, 255, 255))
    screen.blit(text2, (200, 200))
    for rect in asteroidHitbox:
        if starshipHitbox.colliderect(rect):
            screen.blit(text, text.get_rect(center=(width/2, height/2)))
            py.display.flip()
            time.sleep(1)
            running = False
    
    for laser in laser_rects[:]:
        for asteroid in asteroids:
            if laser.colliderect(asteroid['rect']):
                asteroid['x'] = random.randint(50, width-50)
                asteroid['y'] = random.randint(-100, 0)
                asteroid['velocity'] = random.randint(2, 6)
                laser_rects.remove(laser)
                score += 1
                break

    start_time = time.time()
    game_time = round(start_time - current_time, 1)
    text3 = font2.render(f"Time: {game_time}", False, (255, 255, 255))
    screen.blit(text3, (200, 400))

    py.display.flip()
    clock.tick(60)

py.quit()