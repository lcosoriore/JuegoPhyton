import pygame
import os
import time
import random
from pygame.locals import *

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Guerra Mortal")

# Colors
WHITE = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Assets
ASSETS_PATH = os.path.join("assets")

# Load images
enemigo1 = pygame.image.load(os.path.join(ASSETS_PATH, "Cuervo.png"))
enemigo2 = pygame.image.load(os.path.join(ASSETS_PATH, "gavilan.png"))
enemigo3 = pygame.image.load(os.path.join(ASSETS_PATH, "gaviota.png"))

# Player players
MARIO = pygame.image.load(os.path.join(ASSETS_PATH, "personaje.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join(ASSETS_PATH, "bala5.png"))
GREEN_LASER = pygame.image.load(os.path.join(ASSETS_PATH, "bala2.png"))
BLUE_LASER = pygame.image.load(os.path.join(ASSETS_PATH, "bala3.png"))
YELLOW_LASER = pygame.image.load(os.path.join(ASSETS_PATH, "bala5.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_PATH, "fondo.jpg")), (WIDTH, HEIGHT))

# Sounds (You need to have sound files in assets folder)
SHOOT_SOUND = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "background.wav"))
HIT_SOUND = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "background.wav"))

# Game variables
FPS = 60
enemy_vel = 1
player_vel = 5
laser_vel = 5
wave_length = 5
player_lives = 5
game_font = pygame.font.Font(None, 30)
score =0

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            SHOOT_SOUND.play()
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = MARIO
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        global score
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        HIT_SOUND.play()
                        objs.remove(obj)                        
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            score+=1

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        # Barra exterior
        pygame.draw.rect(window, BLUE, (self.x - 5, self.y + self.ship_img.get_height() + 5, self.ship_img.get_width() + 10, 20), border_radius=10)

        # Barra interior que representa la salud actual
        health_width = self.ship_img.get_width() * (self.health / self.max_health)
        pygame.draw.rect(window, CYAN, (self.x, self.y + self.ship_img.get_height() + 10, health_width, 10), border_radius=5)

class Enemy(Ship):
    COLOR_MAP = {
        "red": (enemigo1, RED_LASER),
        "green": (enemigo2, GREEN_LASER),
        "blue": (enemigo3, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            SHOOT_SOUND.play()
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None

def game_loop(player_name):
    global player_lives, score
    run = True
    clock = pygame.time.Clock()
    
    # Player
    player = Player(300, 630)

    # Enemies
    enemies = []
    wave_length = 5
    enemy_vel = 1

    # Game variables
    level = 0
    lost = False
    lost_count = 0
    score=0
    # Main loop
    while run:
        clock.tick(FPS)
        WIN.blit(BG, (0, 0))

        if player.health <= 0:
            player_lives -= 1
            player.health = 100

        if player_lives <= 0:
            lost = True
            lost_count += 1

        if lost:
            lost_label = game_font.render("Perdiste", 1, WHITE)
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))
            pygame.display.update()
            pygame.time.delay(3000)

             # Restablecer las variables del juego
            player_lives = 5
            level = 0
            lost = False
            lost_count = 0
            score = 0
            player = Player(300, 630)
            enemies = []
            wave_length = 5
            enemy_vel = 1

            # Volver a la pantalla de inicio
            player_name = main_menu() 
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                score += 1
            elif enemy.y + enemy.get_height() > HEIGHT:
                player_lives -= 1
                enemies.remove(enemy)
                score += 1

        player.move_lasers(-laser_vel, enemies)
        player.draw(WIN)

        # Draw enemies
        for enemy in enemies:
            enemy.draw(WIN)

        # Display game information
        lives_label = game_font.render(f"Vidas: {player_lives}", 1, WHITE)
        name_label = game_font.render(f"Jugador: {player_name}", 1, WHITE)
        level_label = game_font.render(f"Nivel: {level}", 1, WHITE)
        score_label = game_font.render(f"Puntaje: {score}", 1, WHITE)
        WIN.blit(lives_label, (10, 10))
        WIN.blit(name_label, (WIDTH / 2 - name_label.get_width() / 2, 10)) # Muestra el nombre en el centro del tablero
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (WIDTH - score_label.get_width() - 10, 40))

        # Game Over screen
        if lost:
            lost_label = game_font.render("Perdiste", 1, WHITE)
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()
       
    pygame.quit()

def main_menu():
    title_font = pygame.font.Font(None, 70)
    input_font = pygame.font.Font(None, 70)
    run = True
    player_name = ""

    while run:
        WIN.blit(BG, (0, 0))

        title_label = title_font.render("Toca la pantalla", 1, WHITE)
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 250))

        # Show player name input field
        input_label = input_font.render("Ingresa tu nombre:", 1, WHITE)
        WIN.blit(input_label, (WIDTH / 2 - input_label.get_width() / 2, 350))

        # Show entered player name
        player_name_label = input_font.render(player_name, 1, WHITE)
        WIN.blit(player_name_label, (WIDTH / 2 - player_name_label.get_width() / 2, 400))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    run = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode

    #pygame.quit()
    game_loop(player_name)

# Start the game
main_menu()
