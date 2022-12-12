import pygame
import sys
from time import sleep
from models import Spaceship, Asteroid, Heart
from utils import get_random_pos, load_sprite, print_text, load_sound
from math import sin
from random import randint


class SpaceRocks:
    def __init__(self):
        self._init_pygame()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.ticks = 0

        self.font = pygame.font.Font("assets/planetbe.ttf", 84)
        self.color = (177, 197, 207)
        self._main_menu()

        self.score = 0
        self.lives = 3
        self.hearts = []
        for num in range(1, 4):
            self.hearts.append(Heart((num * 50 - 20, 30)))

        self.wave = 1
        self.ticks = 0

        self.message = ""
        self.indestructable = True

        self.background = pygame.transform.scale(load_sprite("space", False), (800, 600))

        self.MIN_ASTEROID_DIST = 200

        self._create_new_wave()
        self.main_loop()

    def main_loop(self):
        while True:
            self._handle_input()
            self._process_game_logic()
            self._draw()

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Asteroids")

    def _main_menu(self):
        no_key_pressed = True
        while no_key_pressed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

                if (event.type == pygame.KEYUP and event.key) or event.type == pygame.MOUSEBUTTONUP:
                    no_key_pressed = False

            self.screen.fill((25, 20, 25))
            print_text(self.screen, "Asteroids!", self.font, self.color, (400, 180 + sin(2.5 * (self.ticks / 60 - 3)) * 30))
            print_text(self.screen, "Press any key or click to start!", (pygame.font.SysFont("Corbel", 24)), self.color, (400, 400))

            pygame.display.update()

            self.clock.tick(60)
            self.ticks += 1

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                sys.exit("Game script terminated.")
            elif self.spaceship and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.spaceship.shoot()

        if self.spaceship:
            key_pressed = pygame.key.get_pressed()
            if key_pressed[pygame.K_RIGHT] or key_pressed[pygame.K_d]:
                self.spaceship.rotate(clockwise=True)
            if key_pressed[pygame.K_LEFT] or key_pressed[pygame.K_a]:
                self.spaceship.rotate(clockwise=False)
            if key_pressed[pygame.K_UP] or key_pressed[pygame.K_w]:
                self.spaceship.accelerate()
            if key_pressed[pygame.K_DOWN] or key_pressed[pygame.K_s]:
                self.spaceship.accelerate(mode=-1)
            if key_pressed[pygame.K_b] or key_pressed[pygame.K_s]:
                self.spaceship.accelerate(mode=0)
            self.spaceship.accelerate(mode=-2)

    def _process_game_logic(self):
        for game_object in self._get_game_objects():
            game_object.move(self.screen, self.ticks)

        if self.spaceship:
            for gem in self.gems:
                if gem.collides_with(self.spaceship):
                    self.score += int(gem.worth)
                    self.gems.remove(gem)
                    load_sound("reward").play()

            for asteroid in self.asteroids:
                if asteroid.collides_with(self.spaceship) and not self.indestructable:
                    self.lives -= 1
                    self.hearts.pop()
                    self.ticks = 0
                    self.indestructable = True
                    if self.lives == 0:
                        self.spaceship = None
                        self.message = f"You died at {self.score} points, at wave {self.wave}. :("
                        break

        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if asteroid.collides_with(bullet):
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    asteroid.split()
                    if asteroid.size == 3: self.score += randint(250, 350) * self.wave
                    elif asteroid.size == 2: self.score += randint(925, 1075) * self.wave
                    elif asteroid.size == 1: self.score += randint(2400, 3600) * self.wave
                    break

        for bullet in self.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.position):
                self.bullets.remove(bullet)

        if not self.asteroids and self.spaceship: self.message = f"You beat wave {self.wave}! :D"
        if 300 < self.ticks and self.indestructable: self.indestructable = False

    def _draw(self):
        self.screen.blit(self.background, (0, 0))

        for game_object in self._get_game_objects(): game_object.draw(self.screen)

        print_text(self.screen, f"Score: {self.score}", pygame.font.SysFont("Corbel", 32), color=pygame.Color("orange"), coords=(720 - len(str(self.score)) * 5, 20))
        if "You died" in self.message:
            print_text(self.screen, self.message, pygame.font.SysFont("Chiller", 60))
            pygame.display.flip()
            if self.score >= 20000:
                with open("highscores.txt", "a") as f:
                    f.write(f"\n{self.score},{self.wave}")

            with open("highscores.txt", "r") as f:
                contents = f.read()

            lines = contents.split("\n")
            scores = sorted([int(line.split(',')[0]) for line in lines])

            top = scores[10:] if len(scores) >= 10 else scores[len(scores):]
            top.reverse()
            self.screen.blit(self.background, (0, 0))
            print_text(self.screen, "Game Over", pygame.font.SysFont("Courier New", 74), pygame.Color("red"), (350, 70))
            for i, score in enumerate(top):
                print_text(self.screen, str(score), pygame.font.SysFont("Corbel", 38), pygame.Color("white"), (375, 50 * i + 140))
            pygame.display.flip()

            load_sound("lose").play()

            self._wait_until_action()

            sys.exit(self.message)
        elif self.message:
            if self.until_next == -100: self.until_next = 600
            if self.until_next <= 0:
                print_text(self.screen, self.message, pygame.font.SysFont("Bradley Hand ITC", 60), color=pygame.Color("green3"))
                pygame.display.flip()
                self._wait_until_action()
                self.wave += 1
                self._create_new_wave()
            else: self.until_next -= 1

        pygame.display.flip()
        self.ticks += 1
        self.clock.tick(60)

    def _get_game_objects(self):
        game_objects = [*self.dust, *self.gems, *self.asteroids, *self.bullets, *self.hearts]
        if self.spaceship: game_objects.append(self.spaceship)
        return game_objects

    def _create_new_wave(self):
        self.message = ""
        self.bullets = []
        self.dust = []
        self.spaceship = Spaceship((400, 300), self.bullets.append, self.dust.append, self.dust.remove)
        self.asteroids = []
        self.ticks = 0
        self.gems = []
        self.until_next = -100
        self.indestructable = True

        asteroids_in_level = round((self.wave + 1) ** 1.4 - self.wave / 1.2)
        for _ in range(asteroids_in_level):
            while True:
                apos = get_random_pos(self.screen)
                if apos.distance_to(self.spaceship.position) > self.MIN_ASTEROID_DIST: break

            self.asteroids.append(Asteroid(apos, self.asteroids.append, self.gems.append, self.dust.append, self.dust.remove))

    def _wait_until_action(self):
        alive = True
        while alive:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

                if event.type == pygame.MOUSEBUTTONUP:
                    alive = False
