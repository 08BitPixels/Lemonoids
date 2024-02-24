import pygame
from sys import exit
from time import time
from math import atan2, cos, sin, degrees, radians, pi
from random import randint, uniform
from constants import *

# PYGAME SETUP
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

pygame.mouse.set_visible(False)
pygame.display.set_icon(pygame.image.load('Images/Icon.ico'))
pygame.display.set_caption('Lemonoids | INITIALISING...')
screen.blit(pygame.transform.scale(pygame.image.load('Images/Cover.png'), (WIDTH, HEIGHT)), (0, 0))
pygame.display.update()

class Game:

	def __init__(self) -> None:
		
		start_time = time()

		self.S_PLAY = 'play'

		self.state = self.S_PLAY
		self.shake_offset = (0, 0)
		self.shake_offsets = []

		self.explosion_frames = [pygame.transform.scale_by(pygame.transform.rotate(pygame.image.load(f'Images/Explosion/God-Rays.png'), step), 0.75).convert_alpha() for step in range(0, int(360 / 12), 2)]

		self.player = pygame.sprite.GroupSingle(Player(self))
		self.crosshair = pygame.sprite.GroupSingle(Crosshair(self.player.sprite.ship_index, self))
		self.health_bars = pygame.sprite.Group()
		self.lemonoids = pygame.sprite.Group(Lemonoid(angle = randint(0, 360), max_health = 20, move_speed = 75, size = 1, game = self))
		self.explosions = pygame.sprite.Group()

		self.LEMONOID_FREQUENCY = 5000
		self.LEMONOID_TIMER = pygame.USEREVENT + 0
		#pygame.time.set_timer(self.LEMONOID_TIMER, self.LEMONOID_FREQUENCY)

		end_time = time()
		print(f'Game Initialised in {round(end_time - start_time, 3)}s')

	def get_state(self) -> str:
		return self.state

	def set_state(self, state: str) -> None:
		self.state = state

	def shake(self, offset: tuple) -> None:
		self.shake_offset = (self.shake_offset[0] * offset[0], self.shake_offset[1] * offset[1])

class Player(pygame.sprite.Sprite):

	def __init__(self, game: Game) -> None:

		super().__init__()

		self.game = game
		self.ship_index = 0

		self.og_image = pygame.image.load(f'Images/Player/Ship{self.ship_index}/Normal.png')
		self.shoot_image = pygame.image.load(f'Images/Player/Ship{self.ship_index}/Shoot.png')

		self.image = self.og_image
		self.rect = self.image.get_rect(center = (CENTER_X, CENTER_Y))
		self.pos = pygame.math.Vector2(self.rect.center)

		self.shoot_sfx = pygame.mixer.Sound('Audio/SFX/Player/Shoot.wav')

		self.lasers_fired = pygame.sprite.Group()
		self.ACCELERATION_VEL = 0.975
		self.SPEED = 20
		self.FIRE_RATE = 0
		self.FIRE_RATES = {0: 5} #ship index: fire rate
		self.x_vel = 0
		self.y_vel = 0
		self.angle = 0
		self.fire_buffer = 0
		self.set_fire_rate()

	def update(self, dt: float | int) -> None: 
		
		self.rect.center = self.pos
		self.input(dt)

	def input(self, dt: float | int) -> None:

		keys_pressed = pygame.key.get_pressed()
		mouse_pressed = pygame.mouse.get_pressed()[0]
		mouse_pos = pygame.mouse.get_pos()

		self.move_x(keys_pressed[pygame.K_d] - keys_pressed[pygame.K_a], dt)
		self.move_y(keys_pressed[pygame.K_s] - keys_pressed[pygame.K_w], dt)

		self.bound_movement()

		if self.fire_buffer != 0: self.rotate_to(mouse_pos, self.og_image)
		if self.fire_buffer == 0: self.rotate_to(mouse_pos, self.shoot_image)

		if mouse_pressed or keys_pressed[pygame.K_SPACE]: self.shoot(dt)
		elif not mouse_pressed and not keys_pressed[pygame.K_SPACE]: self.set_fire_rate()

	def bound_movement(self) -> None:

		if self.pos.x > WIDTH - self.image.get_width() / 2: self.pos.x = WIDTH - self.image.get_width() / 2
		elif self.pos.x < 0 + self.image.get_width() / 2: self.pos.x = 0 + self.image.get_width() / 2
		if self.pos.y > HEIGHT - self.image.get_height() / 2: self.pos.y = HEIGHT - self.image.get_height() / 2
		elif self.pos.y < 0 + self.image.get_height() / 2: self.pos.y =  0 + self.image.get_height() / 2

	def move_x(self, dir: int, dt: float | int) -> None:
		
		self.x_vel += self.ACCELERATION_VEL * dir * self.SPEED * dt
		self.x_vel = self.ACCELERATION_VEL * self.x_vel
		self.pos.x += self.x_vel + self.game.shake_offset[0]

	def move_y(self, dir: int, dt: float | int) -> None:
		
		self.y_vel += self.ACCELERATION_VEL * dir * self.SPEED * dt
		self.y_vel = self.ACCELERATION_VEL * self.y_vel
		self.pos.y += self.y_vel + self.game.shake_offset[1]

	def rotate_to(self, pos: tuple, og_image: pygame.Surface) -> None:
		
		x_distance = pos[0] - self.pos.x
		y_distance = pos[1] - self.pos.y
		radians = atan2(-y_distance, x_distance)
		radians %= 2 * pi
		self.angle = round(degrees(radians), 2)
		self.image = pygame.transform.rotate(og_image, self.angle).convert_alpha()
		self.rect = self.image.get_rect(center = self.pos)

	def shoot(self, dt: int | float) -> None:

		if self.fire_buffer < 0: self.set_fire_rate()
		elif self.fire_buffer == 0: 
			
			if SFX: self.shoot_sfx.play()
			self.lasers_fired.add(Laser(start_pos = self.pos, angle = self.angle, laser_index = self.ship_index, game = self.game))

		self.fire_buffer -= round(100 * dt)

	def set_fire_rate(self) -> None:

		self.FIRE_RATE = self.FIRE_RATES[self.ship_index]
		self.fire_buffer = self.FIRE_RATE

class Crosshair(pygame.sprite.Sprite):

	def __init__(self, type: int, game: Game) -> None:

		super().__init__()
		
		self.unfocus_image = pygame.transform.scale_by(pygame.image.load(f'Images/Crosshair/Ship{type}-Unfocus.png'), 3).convert_alpha()
		self.focus_image = pygame.transform.scale_by(pygame.image.load(f'Images/Crosshair/Ship{type}-Focus.png'), 3).convert_alpha()
		self.focussed = False
		self.images = [self.unfocus_image, self.focus_image]
		self.image = self.images[self.focussed]

		self.rect = self.image.get_rect(center = (0, 0))
		self.pos = pygame.math.Vector2()

		self.game = game
		self.ROTATE_SPEED = 500
		self.angle = 0

	def update(self, dt: float | int) -> None:

		self.rect.center = self.pos
		self.image = self.images[self.focussed]
		self.input()

		if self.focussed: 
			
			self.rotate(dt)
			self.image = pygame.transform.rotate(self.images[self.focussed], self.angle).convert_alpha()

		self.rect = self.image.get_rect(center = self.pos)

	def input(self) -> None:

		self.pos = pygame.mouse.get_pos()
		self.focussed = pygame.mouse.get_pressed()[0]

	def rotate(self, dt: float | int) -> None:
		self.angle = (self.angle % 360) + self.ROTATE_SPEED * dt

class Laser(pygame.sprite.Sprite):

	def __init__(self, start_pos: tuple, angle: int | float, laser_index: int, game: Game) -> None:

		super().__init__()
		
		self.laser_index = laser_index

		self.image = pygame.transform.rotate(pygame.image.load(f'Images/Laser/Laser{self.laser_index}.png'), angle).convert_alpha()
		self.hit_image = pygame.transform.rotate(pygame.image.load(f'Images/Laser/Hit.png'), angle).convert_alpha()

		self.rect = self.image.get_rect(center = start_pos)
		self.pos = pygame.math.Vector2(self.rect.center)

		self.game = game
		self.ANGLE = angle
		self.SPEED = 1000
		self.collided = False

	def update(self, dt: int | float) -> None:

		if self.collided: self.kill()
		self.rect.center = self.pos
		self.move(dt)
		self.input()

	def input(self) -> None:

		if self.pos.y <= 0 - (self.image.get_height() / 2) or self.pos.y >= HEIGHT + (self.image.get_height() / 2): self.kill()
		if self.pos.x <= 0 - (self.image.get_width() / 2) or self.pos.x >= WIDTH + (self.image.get_width() / 2): self.kill()

		if pygame.sprite.spritecollide(self, self.game.lemonoids, False): self.hit()

	def move(self, dt: int | float) -> None:

		x = cos(radians(self.ANGLE)) * self.SPEED * dt
		y = sin(radians(self.ANGLE)) * self.SPEED * dt
		self.pos += pygame.math.Vector2((x, -y)) + pygame.math.Vector2(self.game.shake_offset)

	def hit(self) -> None:

		self.image = self.hit_image
		self.rect = self.image.get_rect(center = self.pos)
		self.collided = True
		
class Lemonoid(pygame.sprite.Sprite):

	def __init__(self, angle: int, max_health: int, move_speed: int, size: int, game: Game, pos: tuple = None) -> None:

		super().__init__()

		self.og_image = pygame.transform.scale_by(pygame.transform.rotate(pygame.image.load('Images/Lemonoid/Lemonoid.png'), angle), size).convert_alpha()
		self.hit_image = pygame.transform.scale_by(pygame.transform.rotate(pygame.image.load('Images/Lemonoid/Lemonoid-Hit.png'), angle), size).convert_alpha()
		self.image = self.og_image
		if size == 1: self.rect = self.image.get_rect(center = (CENTER_X + cos(radians(angle)) * WIDTH, CENTER_Y - sin(radians(angle)) * WIDTH))
		elif size != 1: self.rect = self.image.get_rect(center = pos)
		self.pos = pygame.math.Vector2(self.rect.center)

		self.hit_sfx = pygame.mixer.Sound('Audio/SFX/Lemonoid/Hit.wav')
		self.explosion_sfx = pygame.mixer.Sound('Audio/SFX/Lemonoid/Explosion.wav')
		self.explosion_sfx_2 = pygame.mixer.Sound('Audio/SFX/Lemonoid/Explosion2.wav')

		self.game = game
		self.MOVE_SPEED = move_speed
		self.ROTATE_SPEED = 100 / size
		self.DIRECTION = angle
		self.DAMAGE = 1
		self.MAX_HEALTH = max_health
		self.EXPLOSION_VEL = 8
		self.angle = angle
		self.health = self.MAX_HEALTH
		self.colliding = False
		self.size = size

	def update(self, dt: float | int) -> None:

		self.rect.center = self.pos
		self.image = self.og_image
		self.move(dt)
		self.rotate(dt)
		self.wrap_around()
		self.input()

	def input(self) -> None:

		if pygame.sprite.spritecollide(self, self.game.player.sprite.lasers_fired, False) and not self.colliding: 
			
			self.hit()
			self.colliding = True

		elif not pygame.sprite.spritecollide(self, self.game.player.sprite.lasers_fired, False): self.colliding = False
			
	def move(self, dt: float | int) -> None:

		x = cos(radians(self.DIRECTION)) * self.MOVE_SPEED * dt
		y = sin(radians(self.DIRECTION)) * self.MOVE_SPEED * dt
		self.pos -= (x + self.game.shake_offset[0], -y + self.game.shake_offset[1])

	def rotate(self, dt: float | int) -> None:

		self.angle = (self.angle % 360) + self.ROTATE_SPEED * dt
		self.image = pygame.transform.rotate(self.og_image, self.angle).convert_alpha()
		self.rect = self.image.get_rect(center = self.pos)

	def wrap_around(self) -> None:

		if self.pos.x > WIDTH + self.image.get_width() / 2: self.pos.x = 0 - self.image.get_width() / 2
		elif self.pos.x < 0 - self.image.get_width() / 2: self.pos.x = WIDTH + self.image.get_width() / 2
		if self.pos.y > HEIGHT + self.image.get_height() / 2: self.pos.y = 0 - self.image.get_height() / 2
		elif self.pos.y < 0 - self.image.get_height() / 2: self.pos.y = HEIGHT + self.image.get_height() / 2

	def shrink(self, percentage: int | float) -> None:

		self.og_image = pygame.transform.scale_by(self.og_image, percentage).convert_alpha()
		self.hit_image = pygame.transform.scale_by(self.hit_image, percentage).convert_alpha()

	def add_shake_offsets(self) -> None:

		#radians = (atan2(-(self.game.player.sprite.pos.x - self.pos.x), self.game.player.sprite.pos.y - self.pos.y)) % 2 * pi

		#self.game.shake_offset = (cos(degrees(radians)) * 16, sin(degrees(radians)) * 16)
		self.game.shake_offset = (cos(self.game.player.sprite.angle) * 16, sin(self.game.player.sprite.angle) * 16)

		for i in range(self.EXPLOSION_VEL): self.game.shake_offsets.append((1, 1))

		self.game.shake_offsets.append((-1.8, -1.8))
		for i in range(self.EXPLOSION_VEL): self.game.shake_offsets.append((1, 1))

		for i in range(16):
			
			self.game.shake_offsets.append((uniform(-0.5, -0.8), uniform(-0.5, -0.8)))
			for i in range(self.EXPLOSION_VEL): self.game.shake_offsets.append((1, 1))

		self.game.shake_offsets.append((0, 0))

	def hit(self) -> None:

		if self.health > 0:

			self.health -= self.DAMAGE
			if SFX: self.hit_sfx.play()
			# score + 2
			self.image = pygame.transform.rotate(self.hit_image, self.angle).convert_alpha()
			self.rect = self.image.get_rect(center = self.pos)
		
		elif self.health <= 0: self.death()

	def death(self) -> None:

		if self.size == 1:

			if SFX: self.explosion_sfx.play()
			self.game.explosions.add(Explosion(type = 'God-Rays', pos = self.pos, frames = self.game.explosion_frames, game = self.game))
			self.add_shake_offsets()
			# score + 100

		elif self.size < 1:

			if SFX: self.explosion_sfx_2.play()
			self.game.explosions.add(Explosion(type = 'Flash', pos = self.pos, game = self.game))
			# score + 25

		self.size /= 2.5
		self.shrink(self.size)

		if self.size < (1 / 2.5 / 2.5):

			# score + 5
			self.kill()

		else:

			new_direction = self.DIRECTION + randint(0, 180)
			self.game.lemonoids.add(
				Lemonoid(pos = self.pos, angle = new_direction, max_health = 8 if self.size == (1 / 2.5) else 1, move_speed = self.MOVE_SPEED * 1.5, size = self.size, game = self.game),
				Lemonoid(pos = self.pos, angle = new_direction + 120, max_health = 8 if self.size == (1 / 2.5) else 1, move_speed = self.MOVE_SPEED * 1.5, size = self.size, game = self.game),
				Lemonoid(pos = self.pos, angle = new_direction + 240, max_health = 8 if self.size == (1 / 2.5) else 1, move_speed = self.MOVE_SPEED * 1.5, size = self.size, game = self.game)
			)
			
			self.kill()

class Explosion(pygame.sprite.Sprite):

	def __init__(self, type: str, pos: tuple | pygame.math.Vector2, game: Game, frames: list = None) -> None:

		super().__init__()
		
		if type == 'God-Rays': 
			
			self.frames = frames
			self.frame_index = 0

		if type == 'Flash':

			self.og_image = pygame.transform.scale_by(pygame.image.load(f'Images/Explosion/Flash.png'), 0.5).convert_alpha()

		self.image = self.og_image if type == 'Flash' else self.frames[self.frame_index] 
		self.rect = self.image.get_rect(center = pos)
		self.pos = pygame.math.Vector2(self.rect.center)

		self.TYPE = type
		self.game = game
		self.ROTATE_SPEED = 20
		self.FADE_SPEED = 550
		self.finished = False
		self.alpha = 256

	def update(self, dt: float | int) -> None:
		
		if self.TYPE == 'God-Rays': self.rotate(dt)
		self.fade(dt)

	def rotate(self, dt: float | int) -> None:

		self.frame_index = (self.frame_index + self.ROTATE_SPEED * dt) % len(self.frames)
		self.image = self.frames[int(self.frame_index)]
		self.rect = self.image.get_rect(center = self.pos + pygame.math.Vector2(self.game.shake_offset))

	def fade(self, dt: float | int) -> None:

		self.alpha -= self.FADE_SPEED * dt
		self.image.set_alpha(self.alpha)
		if self.alpha <= 0: self.kill()

class Health_Bar(pygame.sprite.Sprite):

	def __init__(self, parent: Lemonoid) -> None:

		super().__init__()
		self.image = None
		self.rect = None

		self.parent = parent
		self.MAX_HEALTH = self.parent.MAX_HEALTH
		self.health = self.parent.health

	def update(self, dt: float | int) -> None:

		self.health = self.parent.health

def main():

	game = Game()
	player = game.player
	lasers_fired = player.sprite.lasers_fired
	lemonoids = game.lemonoids
	explosions = game.explosions
	crosshair = game.crosshair
	health_bars = game.health_bars

	previous_time = time()
	while True:

		dt = time() - previous_time
		previous_time = time()

		for event in pygame.event.get():

			if event.type == pygame.QUIT:

				pygame.quit()
				exit()

			if game.get_state() == game.S_PLAY:

				if event.type == game.LEMONOID_TIMER:

					angle = randint(0, 360)
					new_lemonoid = Lemonoid(angle = angle, max_health = 20, move_speed = 75, size = 1, game = game)
					lemonoids.add(new_lemonoid)
					health_bars.add(Health_Bar(parent = new_lemonoid))

				if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:

					game.shake_offset = (-cos(game.player.sprite.angle) * 16, sin(game.player.sprite.angle) * 16)

					for i in range(16): game.shake_offsets.append((1, 1))
					for i in range(16): game.shake_offsets.append((-1, -1))
					game.shake_offsets.append((0, 0))

					'''game.shake_offsets.append((-1.8, -1.8))
					for i in range(8): game.shake_offsets.append((1, 1))

					for i in range(16):
						
						game.shake_offsets.append((uniform(-0.5, -0.8), uniform(-0.5, -0.8)))
						for i in range(8): game.shake_offsets.append((1, 1))

					game.shake_offsets.append((0, 0))'''

		screen.fill(BG_COLOUR)

		if game.get_state() == game.S_PLAY:

			# Game
			if len(game.shake_offsets) > 0:

				game.shake(game.shake_offsets[0])
				game.shake_offsets.pop(0)

			# Health Bars
			health_bars.update(dt)
			health_bars.draw(screen)

			# Explosions
			explosions.update(dt)
			explosions.draw(screen)

			# Player
			player.update(dt)
			player.draw(screen)
			
			# Lemonoids
			lemonoids.update(dt)
			lemonoids.draw(screen)

			# Lasers
			lasers_fired.draw(screen)
			lasers_fired.update(dt)

			# Crosshair
			crosshair.draw(screen)
			crosshair.update(dt)

		pygame.display.set_caption(f'Lemonoids | FPS: {round(clock.get_fps(), 1)}')
		pygame.display.update()
		clock.tick(FPS)

main()