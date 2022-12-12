import random
from pygame import Color
from pygame.image import load
from pygame.math import Vector2
from pygame.mixer import Sound


def load_sprite(name, with_alpha=True):
	path = f"assets/sprites/{name}.png"
	loaded_sprite = load(path)

	if with_alpha: return loaded_sprite.convert_alpha()
	else: return loaded_sprite.convert()


def wrap_position(position, surface):
	x, y = position
	w, h = surface.get_size()
	return Vector2(x % w, y % h)


def get_random_pos(surface):
	return Vector2(
		random.randrange(surface.get_width()),
		random.randrange(surface.get_height())
	)


def get_random_velocity(min_speed, max_speed):
	speed = random.randint(min_speed * 10, max_speed * 10) * 0.1
	angle = random.randrange(0, 360)
	return Vector2(speed, 0).rotate(angle)


def load_sound(name):
	path = f"assets/sounds/{name}.wav"
	return Sound(path)


def print_text(surface, text, font, color=Color("tomato"), coords=None):
	text_surface = font.render(text, True, color)
	text_rect = text_surface.get_rect()
	if coords: text_rect.center = Vector2(coords)
	else: text_rect.center = Vector2(surface.get_size()) / 2
	surface.blit(text_surface, text_rect)
	'''
	text_surface = font.render(text, True, color)
	rect = text_surface.get_rect()
	if coords: rect.center = Vector2(coords)
	else: rect.center = Vector2(surface.get_size()) / 2
	surface.blit(text_surface, rect)'''
