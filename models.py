from pygame.math import Vector2
from utils import get_random_velocity, load_sound, load_sprite, wrap_position
from pygame.transform import rotozoom, scale
from random import randint, uniform
from time import time
from math import ceil

UP = Vector2(0, -1)


class GameObject:
    def __init__(self, position, sprite, velocity):
        self.sprite = sprite
        self.position = Vector2(position)
        self.radius = sprite.get_width() / 2
        self.velocity = Vector2(velocity)

    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

    def move(self, surface, *args):
        self.position = wrap_position(self.position + self.velocity, surface)

    def collides_with(self, other_obj):
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius


class Spaceship(GameObject):
    def __init__(self, position, cbc, cdc, ddc):
        self.create_bullet_callback = cbc
        self.create_dust_callback = cdc
        self.destroy_dust_callback = ddc
        self.direction = Vector2(UP)
        super().__init__(position, load_sprite("spaceship"), Vector2(0))
        self.laser_sound = load_sound("laser")
        self.MANEUVERABILITY = 5
        self.ACCELERATION = 0.06
        self.BRAKEFORCE = 0.7
        self.BULLET_SPEED = 3
        self.MAX_SPEED = 5
        self.SPACE_FRICTION = 0.985

    def rotate(self, clockwise=True):
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)

    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def accelerate(self, mode=1):
        if sum(self.velocity) > self.MAX_SPEED: self.velocity *= self.SPACE_FRICTION
        else:
            if mode == 0: self.velocity *= self.BRAKEFORCE
            elif mode == -1: self.velocity -= self.direction * self.ACCELERATION / 3
            elif mode == -2: self.velocity *= self.SPACE_FRICTION
            else:
                self.velocity += self.direction * self.ACCELERATION
                d = Dust(self.position, -uniform(0.7, 1.8) * Vector2(self.velocity.x + uniform(-1, 1), self.velocity.y + uniform(-1, 1)), 2)
                d.kill_callback = self.destroy_dust_callback
                self.create_dust_callback(d)

    def shoot(self):
        bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
        bullet = Bullet(self.position, bullet_velocity)
        self.create_bullet_callback(bullet)
        self.laser_sound.play()


class Asteroid(GameObject):
    def __init__(self, position, cac, cgc, cdc, ddc, size=3):
        self.create_asteroid_callback = cac
        self.create_gem_callback = cgc
        self.create_dust_callback = cdc
        self.destroy_dust_callback = ddc
        self.size = size
        self.explosion_sound = load_sound("boom")
        self.size_to_data = {
            3: [1.1, 3],
            2: [0.6, 6],
            1: [0.3, 9]
        }
        scale = self.size_to_data[size][0]
        sprite = rotozoom(load_sprite("asteroid"), 0, scale)
        super().__init__(position, sprite, get_random_velocity(1, 2))

    def split(self):
        for _ in range(randint(30, 45) * self.size):
            d = Dust(self.position, get_random_velocity(2, 4) * self.size, 1)
            d.kill_callback = self.destroy_dust_callback
            self.create_dust_callback(d)

        if self.size > 1:
            for _ in range(2):
                asteroid = Asteroid(self.position, self.create_asteroid_callback, self.create_gem_callback, self.create_dust_callback, self.destroy_dust_callback, self.size - 1)
                self.create_asteroid_callback(asteroid)

        self.explosion_sound.play()
        if randint(1, self.size_to_data[self.size][1]) == 1:
            gem = Gem(self.position, self.size)
            self.create_gem_callback(gem)


class Dust(GameObject):
    def __init__(self, position, velocity, lifetime=3, friction=0.97):
        super().__init__(position, scale(load_sprite("dust"), (12, 12)), velocity)
        self.kill_callback = None
        self.friction = friction
        self.born = time()
        self.lifetime = lifetime + uniform(-1, 1)
        self.size = 14
        self.last_size = 14
        self.SIZE_CHANGE = self.lifetime / 6
        self.dead = False

    def move(self, *args):
        if self.dead: return
        self.size -= self.SIZE_CHANGE
        if ceil(self.size) != ceil(self.last_size):
            if self.size > 0: self.sprite = scale(self.sprite, (self.size, self.size))
            else: self.dead = True
        self.position = self.position + self.velocity * self.friction
        self.velocity *= self.friction
        if time() - self.born > self.lifetime: self.kill_callback(self)
        self.last_size = self.size


class Bullet(GameObject):
    def __init__(self, position, velocity, friction=0.998):
        super().__init__(position, load_sprite("bullet"), velocity)
        self.friction = friction

    def move(self, surface, *args):
        self.position += self.velocity
        self.velocity *= self.friction


class Gem(GameObject):
    def __init__(self, position, size):
        super().__init__(position, scale(load_sprite("gem"), (size * 20, size * 18)), Vector2(0))
        self.worth = round(size * uniform(0.8, 1.2) * 4500, -2)


class Heart(GameObject):
    def __init__(self, position):
        super().__init__(position, scale(load_sprite("heart"), (50, 50)), Vector2(0))
        self.mode = 1
        self.forever_pos = position

    def move(self, surface, ticks):
        if ticks % 30 == 0:
            if self.mode == 1:
                self.position += Vector2(0, 5)
                self.mode = -1
            else:
                self.position = self.forever_pos
                self.position -= Vector2(0, 5)
                self.mode = 1
