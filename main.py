# PickleHack 2020
# Author: Akshith Gara
# Pickle-Axe (Pickle Shooting Game)

import pygame
import os
import time
import random
from Laser import Laser, collide

pygame.font.init()
WIDTH, HEIGHT = 700, 700 # Window dimensions
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pickle-Axe')

# Getting the images
PICKLE = pygame.image.load(os.path.join("assets", "pickle.png"))
PICKLE = pygame.transform.scale(PICKLE, (80, 150))

# Player
KNIFE = pygame.image.load(os.path.join("assets", "gun.png"))
KNIFE = pygame.transform.scale(KNIFE, (100, 100))

# Enemy fire
RED_LASER = pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
RED_LASER= pygame.transform.scale(RED_LASER, (40, 40))
GREEN_LASER = pygame.image.load(os.path.join("assets","axe.png"))
GREEN_LASER = pygame.transform.scale(GREEN_LASER, (50,75))

# Lives
HEART = pygame.image.load(os.path.join("assets","heart.png"))
HEART = pygame.transform.scale(HEART, (20,20))

BACKGROUND = pygame.image.load(os.path.join("assets", "background.png"))


class Item:
    COOLDOWN = 30
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.item_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.item_img, (self.x, self.y))
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
            laser = Laser(self.x+25, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.item_img.get_width()

    def get_height(self):
        return self.item_img.get_height()

class Player(Item):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.item_img = KNIFE
        self.laser_img = GREEN_LASER
        self.mask = pygame.mask.from_surface(self.item_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.item_img.get_height() + 10, self.item_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.item_img.get_height() + 10, self.item_img.get_width() * (self.health/self.max_health), 10))

class enemyPickle(Item):
    def __init__(self,x, y, health = 100):
        super().__init__(x, y, health)
        self.item_img = PICKLE
        self.laser_img = RED_LASER
        self.mask = pygame.mask.from_surface(self.item_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def main():
    run = True
    fps = 60
    clock = pygame.time.Clock()
    level = 0
    lives = 5
    mainFont = pygame.font.SysFont("open sans", 30)
    lostFont = pygame.font.SysFont("open sans", 60)
    player = Player(350, 575)
    player_velocity = 5
    laser_vel = 5
    enemies = []
    wave_length = 0
    enemy_velocity = 1
    lost = False
    lost_count = 0

    def redraw_window():
        WINDOW.blit(BACKGROUND,(0,0))
        livesLabel = mainFont.render(f'Lives: ', 1, (0,0,0))
        levelLabel = mainFont.render(f'Level: {level}', 1, (0,0,0))

        WINDOW.blit(livesLabel, (10,10))
        WINDOW.blit(levelLabel, (WIDTH - levelLabel.get_width() - 10, 10))


        for enemy in enemies:
            enemy.draw(WINDOW)

        player.draw(WINDOW)

        if lost:
            lost_label = lostFont.render('GAME OVER', 1, (0,0,0))
            WINDOW.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        x = 50
        y = 10
        for i in range(lives):
            x += 20
            WINDOW.blit(HEART, (x,y))
        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw_window()
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > fps * 5:
                run = False
            else:
                continue
        if len(enemies) == 0:
            level += 1
            wave_length += 3
            for i in range(wave_length):
                enemy = enemyPickle(random.randrange(20,WIDTH-75), random.randrange(-150,-50))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_velocity > 0: #left
            player.x -= player_velocity
        if keys[pygame.K_d] and player.x + player_velocity + player.get_width() < WIDTH: #right
            player.x += player_velocity
        if keys[pygame.K_w] and player.y - player_velocity > 0: #up
            player.y -= player_velocity
        if keys[pygame.K_s] and player.y + player_velocity + player.get_height() < HEIGHT: #down
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)


        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WINDOW.blit(BACKGROUND, (0,0))
        title_label = title_font.render("Pickle-Axe", 1, (0,0,0))
        WINDOW.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
