import pygame

from time import time
from math import atan2, cos, sin, degrees, radians, pi
from random import randint, uniform, choice

from constants import *

# PYGAME SETUP
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Fonts
h1_font = pygame.font.Font('Fonts/pixel_font.ttf', 75)
h2_font = pygame.font.Font('Fonts/pixel_font.ttf', 50)
h3_font = pygame.font.Font('Fonts/pixel_font.ttf', 25)

# Window Setup
pygame.mouse.set_visible(False)
pygame.display.set_icon(pygame.image.load('Images/Icon.ico'))
pygame.display.set_caption('Lemonoids | INITIALISING...')
screen.blit(pygame.transform.scale(pygame.image.load('Images/Cover.png'), (WIDTH, HEIGHT)), (0, 0))
pygame.display.update()

class Game:

	def __init__(self) -> None:
		
		start_time = time()

		self.S_PLAY = 'play'
		self.S_GAME_OVER = 'game_over'

		self.state = self.S_PLAY
		self.score = 0
		with open('Saves/save.txt', 'r') as save: self.highscore = int(save.readlines()[0].strip('HIGHSCORE = '))
		self.shake_offset = (0, 0)
		self.shake_offsets = []

		self.explosion_frames = [pygame.transform.scale_by(pygame.transform.rotate(pygame.image.load(f'Images/Explosion/God-Rays1.png'), step), 0.5).convert_alpha() for step in range(0, int(360 / 20), 2)]

		self.player = pygame.sprite.GroupSingle(Player(game = self))
		self.cursor = pygame.sprite.GroupSingle(Cursor(game = self))
		self.lemonoids = pygame.sprite.Group()
		for i in range(3): self.lemonoids.add(Lemonoid(angle = randint(0, 360), move_speed = 75, size = 1, game = self))
		self.explosions = pygame.sprite.Group()
		self.text = Text(game = self)
		self.particles = pygame.sprite.Group()

		self.lemonoid_frequency = 15000
		self.LEMONOID_TIMER = pygame.USEREVENT + 0
		pygame.time.set_timer(self.LEMONOID_TIMER, self.lemonoid_frequency)

		print(f'Game Initialised in {round(time() - start_time, 3)}s')

	def update(self) -> None:

		if self.score > self.highscore: self.highscore = self.score

		if self.score > 10000 and self.lemonoid_frequency == 15000:

			self.lemonoid_frequency = 10000
			pygame.time.set_timer(self.LEMONOID_TIMER, self.lemonoid_frequency)

		if self.score > 50000 and self.lemonoid_frequency == 10000:

			self.lemonoid_frequency = 7500
			pygame.time.set_timer(self.LEMONOID_TIMER, self.lemonoid_frequency)

		if self.score > 100000 and self.lemonoid_frequency == 7500:

			self.lemonoid_frequency = 1000
			pygame.time.set_timer(self.LEMONOID_TIMER, self.lemonoid_frequency)

	def add_score(self, score: int) -> None:
		self.score += score

	def get_state(self) -> str:
		return self.state

	def set_state(self, state: str) -> None:
		self.state = state

	def shake(self, offset: tuple) -> None:
		self.shake_offset = (self.shake_offset[0] * offset[0], self.shake_offset[1] * offset[1])

	def game_over(self) -> None:

		self.score = 0
		self.state = self.S_GAME_OVER
		self.reset()

	def respawn(self) -> None:

		self.shake_offset = (0, 0)
		self.shake_offsets.clear()
		self.lemonoids.empty()
		for i in range(3): self.lemonoids.add(Lemonoid(angle = randint(0, 360), move_speed = 75, size = 1, game = self))
		pygame.time.set_timer(self.LEMONOID_TIMER, self.lemonoid_frequency)
		self.explosions.empty()

	def reset(self) -> None:

		self.lemonoids.empty()
		self.explosions.empty()
		self.player.sprite.reset()

	def save(self) -> None:

		print('Saving...')
		with open('Saves/save.txt', 'w') as save:

			save.write(f'HIGHSCORE = {self.highscore}')

		print('Saving Completed Successfully')

class Text:

	def __init__(self, game: Game) -> None:

		self.game = game
		self.texts = []

		# Texts

		self.fps_text1 = h3_font.render('FPS:', False, GREY, BLACK)
		self.fps_text1_rect = self.fps_text1.get_rect(topleft = (0, 0))

		self.fps_text2 = None
		self.fps_text2_rect = None

		# Play
		self.score_text = None
		self.score_text_rect = None

		self.play_text1 = h3_font.render('Score', False, DARK_GREY)
		self.play_text1_rect = self.play_text1.get_rect(center = (CENTER_X, 170))

		self.highscore_text = None
		self.highscore_text_rect = None

		self.play_text2 = h3_font.render('Highscore', False, DARK_GREY)
		self.play_text2_rect = self.play_text2.get_rect(center = (CENTER_X, 65))

		self.lives_text = None
		self.lives_text_rect = None

		self.play_text3 = h3_font.render('Lives', False, DARK_GREY)
		self.play_text3_rect = self.play_text3.get_rect(center = (CENTER_X, HEIGHT - 40))

		# Game Over
		self.game_over_text1 = h1_font.render('GAME OVER', False, WHITE)
		self.game_over_text1_rect = self.game_over_text1.get_rect(center = (CENTER_X, CENTER_Y))

		self.game_over_text2 = h3_font.render('Press [SPACE] to retry', False, YELLOW)
		self.game_over_text2_rect = self.game_over_text2.get_rect(center = (CENTER_X, CENTER_Y + 45))

	def update(self) -> None:

		fps = round(clock.get_fps(), 1)
		fps_colour = GREEN if fps > 60 else YELLOW if fps < 60 and fps > 10 else RED
		self.fps_text2 = h3_font.render(str(fps), False, fps_colour, BLACK)
		self.fps_text2_rect = self.fps_text2.get_rect(topleft = (75, 0))

		if self.game.get_state() == self.game.S_PLAY:

			self.score_text = h1_font.render(str(self.game.score), False, WHITE)
			self.score_text_rect = self.score_text.get_rect(center = (CENTER_X, 120))

			self.highscore_text = h2_font.render(str(self.game.highscore), False, GREY)
			self.highscore_text_rect = self.highscore_text.get_rect(center = (CENTER_X, 30))

			self.lives_text = h1_font.render(str(self.game.player.sprite.lives), False, [RED, RED, YELLOW, GREEN][self.game.player.sprite.lives])
			self.lives_text_rect = self.lives_text.get_rect(midbottom = (CENTER_X, HEIGHT - 40))

			self.texts = [

				[self.fps_text1, self.fps_text1_rect],
				[self.fps_text2, self.fps_text2_rect],

				[self.score_text, self.score_text_rect],
				[self.play_text1, self.play_text1_rect],

				[self.highscore_text, self.highscore_text_rect],
				[self.play_text2, self.play_text2_rect],

				[self.lives_text, self.lives_text_rect],
				[self.play_text3, self.play_text3_rect]

			]

		elif self.game.get_state() == self.game.S_GAME_OVER:

			self.texts = [

				[self.game_over_text1, self.game_over_text1_rect],
				[self.game_over_text2, self.game_over_text2_rect]

			]

		else: 
			
			self.texts = [
				[self.fps_text1, self.fps_text1_rect],
				[self.fps_text2, self.fps_text2_rect]
			]

class Player(pygame.sprite.Sprite):

	def __init__(self, game: Game) -> None:

		super().__init__()

		self.game = game

		# Constant Vars
		self.SIZE = 2
		self.ACCELERATION_VEL = 0.999
		self.SPEED = 3
		self.FIRE_RATE = 0
		self.FIRE_RATES = {0: 8} # ship index: fire rate
		self.ACCURACIES = {0: 1} # ship index: accuracy (fire spread) in degrees
		self.MAX_LIVES = 3
		self.BLINK_FREQUENCY = 250
		self.BLINK_TIMER = pygame.USEREVENT + 1
		self.EXPLOSION_SHAKE_VEL = 4

		# Vars
		self.x_vel = 0
		self.y_vel = 0
		self.angle = 0
		self.fire_buffer = 0
		self.ship_index = 0
		self.lives = self.MAX_LIVES
		self.collided = False
		self.dead = False
		self.death_time = 0
		self.blink_index = 0
		self.invincible = True

		# Images
		self.og_image = pygame.transform.scale_by(pygame.image.load(f'Images/Player/Ship{self.ship_index}/Normal.png'), self.SIZE).convert_alpha()
		self.shoot_image = pygame.transform.scale_by(pygame.image.load(f'Images/Player/Ship{self.ship_index}/Shoot.png'), self.SIZE).convert_alpha()
		self.thruster_image = pygame.transform.scale_by(pygame.image.load(f'Images/Player/Ship{self.ship_index}/Thruster.png'), self.SIZE).convert_alpha()
		self.blink_image = pygame.transform.scale_by(pygame.image.load(f'Images/Player/Ship{self.ship_index}/Blink.png'), self.SIZE).convert_alpha()

		self.break_images = [pygame.transform.scale_by(pygame.image.load(f'Images/Player/Ship{self.ship_index}/Break/Break{i}.png'), self.SIZE).convert_alpha() for i in range(3)]
		self.particle_images = [pygame.transform.scale_by(pygame.image.load(f'Images/Player/Ship{self.ship_index}/Break/Particle{i}.png'), self.SIZE).convert_alpha() for i in range(2)]

		# Image, Rect, Mask, Pos
		self.image = self.og_image
		self.rect = self.image.get_rect(center = (CENTER_X, CENTER_Y))
		self.mask = pygame.mask.from_surface(self.image)
		self.pos = pygame.math.Vector2(self.rect.center)

		# SFX
		self.shoot_sfx = pygame.mixer.Sound('Audio/SFX/Player/Shoot.wav')

		# Lasers Fired
		self.lasers_fired = pygame.sprite.Group()

		self.set_fire_rate()

	def update(self, dt: float | int) -> None: 
		
		self.rect.center = self.pos
		self.mask = pygame.mask.from_surface(self.image)
		self.input(dt)
		self.wrap_around()

	def input(self, dt: float | int) -> None:

		keys_pressed = pygame.key.get_pressed()
		mouse_pressed = pygame.mouse.get_pressed()[0]
		mouse_pos = pygame.mouse.get_pos()

		# Movement
		self.move(self.angle, keys_pressed[pygame.K_w], dt)

		# Direction
		if self.fire_buffer != 0: self.rotate_to(mouse_pos, self.og_image)
		if self.fire_buffer == 0: self.rotate_to(mouse_pos, self.shoot_image)
		if keys_pressed[pygame.K_w] and randint(0, 1) == 0: self.rotate_to(mouse_pos, self.thruster_image)
		if self.blink_index == 1: self.rotate_to(mouse_pos, self.blink_image)

		if mouse_pressed or keys_pressed[pygame.K_SPACE]: self.shoot(dt)
		elif not mouse_pressed and not keys_pressed[pygame.K_SPACE]: self.set_fire_rate()

		# Collisions
		if pygame.sprite.spritecollide(self, self.game.lemonoids, False, pygame.sprite.collide_rect) and not self.collided and not self.dead and not self.invincible:

			if pygame.sprite.spritecollide(self, self.game.lemonoids, False, pygame.sprite.collide_mask):

				self.hit()
				self.collided = True

			else: self.collided = False

	def hit(self) -> None:

		self.lives -= 1
		self.death_animation()
		self.dead = True

	def death_animation(self) -> None:

		# Explosion
		self.game.explosions.add(

			Explosion(
				type = 0, 
				pos = self.pos, 
				game = self.game, 
				frames = self.game.explosion_frames
			)

		)

		# Particles
		for i in range(len(self.break_images)): 
			 
			self.game.particles.add(

				Particle(
					start_pos = self.pos, 
			 		angle = self.angle + 120 * i,
					image = self.break_images[i], 
					move_speed = randint(100, 200), 
					rotation_speed = randint(100, 1000),
					fade_speed = 50,
					game = self.game
				)

			)

		for i in range(randint(8, 32)): 
			
			self.game.particles.add(

				Particle(
					start_pos = self.pos,
			 		angle = randint(0, 360),
					image = self.particle_images[i % len(self.particle_images)], 
					move_speed = randint(100, 200), 
					rotation_speed = randint(100, 1000),
					fade_speed = 150,
					game = self.game
				)

			)

		# Shake
		self.game.shake_offset = (cos(self.angle) * 16, sin(self.angle) * 16)

		for i in range(self.EXPLOSION_SHAKE_VEL): self.game.shake_offsets.append((1, 1))

		self.game.shake_offsets.append((-1.8, -1.8))
		for i in range(self.EXPLOSION_SHAKE_VEL): self.game.shake_offsets.append((1, 1))

		for i in range(16):
			
			self.game.shake_offsets.append((uniform(-0.5, -0.8), uniform(-0.5, -0.8)))
			for i in range(self.EXPLOSION_SHAKE_VEL): self.game.shake_offsets.append((1, 1))

		self.game.shake_offsets.append((0, 0))
		
		self.death_time = pygame.time.get_ticks()

	def blink(self) -> None:
		self.blink_index = (self.blink_index % 2) + 1

	def wrap_around(self) -> None:

		if self.pos.x > WIDTH + self.image.get_width() / 2: self.pos.x = 0 - self.image.get_width() / 2
		elif self.pos.x < 0 - self.image.get_width() / 2: self.pos.x = WIDTH + self.image.get_width() / 2
		if self.pos.y > HEIGHT + self.image.get_height() / 2: self.pos.y = 0 - self.image.get_height() / 2
		elif self.pos.y < 0 - self.image.get_height() / 2: self.pos.y = HEIGHT + self.image.get_height() / 2

	def move(self, angle: int, momentum: int, dt: float | int) -> None:

		self.x_vel += cos(radians(angle)) * self.ACCELERATION_VEL * momentum * self.SPEED * dt
		self.x_vel = self.ACCELERATION_VEL * self.x_vel
		self.pos.x += self.x_vel + self.game.shake_offset[0]

		self.y_vel += sin(radians(angle)) * self.ACCELERATION_VEL * momentum * self.SPEED * dt
		self.y_vel = self.ACCELERATION_VEL * self.y_vel
		self.pos.y -= self.y_vel + self.game.shake_offset[1]

	def rotate_to(self, pos: tuple, og_image: pygame.Surface) -> None:
		
		x_distance = pos[0] - self.pos.x
		y_distance = pos[1] - self.pos.y
		angle_to = degrees(atan2(-y_distance, x_distance) % (2 * pi))
		self.angle = round(angle_to, 2)
		self.image = pygame.transform.rotate(og_image, self.angle).convert_alpha()
		self.rect = self.image.get_rect(center = self.pos)

	def shoot(self, dt: int | float) -> None:

		if self.fire_buffer < 0: self.set_fire_rate()
		elif self.fire_buffer == 0:
			
			if SFX: self.shoot_sfx.play()
			self.lasers_fired.add(

				Laser(
					start_pos = self.pos, 
		  			angle = self.angle + uniform(-(self.ACCURACIES[self.ship_index] / 2), self.ACCURACIES[self.ship_index] / 2),
					size = self.SIZE,
					laser_index = self.ship_index, 
					game = self.game
				)

			)

		self.fire_buffer -= round(100 * dt)

	def set_fire_rate(self) -> None:

		self.FIRE_RATE = self.FIRE_RATES[self.ship_index]
		self.fire_buffer = self.FIRE_RATE

	def respawn(self) -> None:

		self.game.respawn()
		self.pos = pygame.math.Vector2((CENTER_X, CENTER_Y))
		self.x_vel, self.y_vel, self.angle = 0, 0, 0
		self.collided = False
		self.dead = False
		self.death_time = 0
		self.blink_index = 0
		pygame.time.set_timer(self.BLINK_TIMER, self.BLINK_FREQUENCY, 6)

	def reset(self) -> None:

		self.lives = self.MAX_LIVES
		self.image = self.og_image
		self.pos = pygame.math.Vector2((CENTER_X, CENTER_Y))
		self.x_vel, self.y_vel, self.angle = 0, 0, 0
		self.collided = False
		self.dead = False
		self.death_time = 0
		self.blink_index = 0
		self.lasers_fired.empty()

class Cursor(pygame.sprite.Sprite):

	def __init__(self, game: Game) -> None:

		super().__init__()

		self.game = game
		self.ROTATE_SPEED = 500
		self.angle = 0
		self.index = {self.game.S_PLAY: 1, self.game.S_GAME_OVER: 0}[self.game.get_state()]

		self.cursor_unfocus_image = pygame.transform.scale_by(pygame.image.load(f'Images/Cursor/Cursor/Unfocus.png'), 3).convert_alpha()
		self.cursor_focus_image = pygame.transform.scale_by(pygame.image.load(f'Images/Cursor/Cursor/Focus.png'), 3).convert_alpha()
		self.focussed = False
		
		self.crosshair_unfocus_image = pygame.transform.scale_by(pygame.image.load(f'Images/Cursor/Crosshair/Unfocus.png'), 3).convert_alpha()
		self.crosshair_focus_image = pygame.transform.scale_by(pygame.image.load(f'Images/Cursor/Crosshair/Focus.png'), 3).convert_alpha()
		self.focussed = False

		self.images = [[self.cursor_unfocus_image, self.cursor_focus_image], [self.crosshair_unfocus_image, self.crosshair_focus_image]]
		self.image = self.images[self.index][self.focussed]

		self.rect = self.image.get_rect(center = pygame.mouse.get_pos())
		self.pos = pygame.math.Vector2(self.rect.center)

	def update(self, dt: float | int) -> None:

		self.rect.center = self.pos
		self.index = {self.game.S_PLAY: 1, self.game.S_GAME_OVER: 0}[self.game.get_state()]
		self.image = self.images[self.index][self.focussed]
		self.input()

		if self.focussed and self.game.get_state() == self.game.S_PLAY: self.rotate(dt)

		self.rect = self.image.get_rect(center = self.pos)

	def input(self) -> None:

		self.pos = pygame.mouse.get_pos()
		self.focussed = pygame.mouse.get_pressed()[0]

	def rotate(self, dt: float | int) -> None:

		self.angle = (self.angle % 360) + self.ROTATE_SPEED * dt
		self.image = pygame.transform.rotate(self.images[self.index][self.focussed], self.angle).convert_alpha()

class Laser(pygame.sprite.Sprite):

	def __init__(self, start_pos: tuple, angle: int | float, size: int | float, laser_index: int, game: Game) -> None:

		super().__init__()
		
		self.laser_index = laser_index
		self.game = game
		self.ANGLE = angle
		self.SIZE = size
		self.SPEEDS = {0: 1000} # laser index: speed
		self.collided = 0

		self.image = pygame.transform.rotate(pygame.transform.scale_by(pygame.image.load(f'Images/Laser/Laser{self.laser_index}.png'), self.SIZE), self.ANGLE).convert_alpha()
		self.hit_image = pygame.transform.rotate(pygame.transform.scale_by(pygame.image.load(f'Images/Laser/Hit.png'), self.SIZE), self.ANGLE).convert_alpha()
		self.mask = pygame.mask.from_surface(self.image)

		self.rect = self.image.get_rect(center = start_pos)
		self.pos = pygame.math.Vector2(self.rect.center)

	def update(self, dt: int | float) -> None:

		if self.collided >= 2: self.kill()
		self.rect.center = self.pos

		self.move(dt)
		self.input()

	def input(self) -> None:

		if self.pos.y <= 0 - (self.image.get_height() / 2) or self.pos.y >= HEIGHT + (self.image.get_height() / 2): self.kill()
		if self.pos.x <= 0 - (self.image.get_width() / 2) or self.pos.x >= WIDTH + (self.image.get_width() / 2): self.kill()

		if pygame.sprite.spritecollide(self, self.game.lemonoids, False, pygame.sprite.collide_rect):
			if pygame.sprite.spritecollide(self, self.game.lemonoids, False, pygame.sprite.collide_mask):
				self.hit()

	def move(self, dt: int | float) -> None:

		x = cos(radians(self.ANGLE)) * self.SPEEDS[self.laser_index] * dt
		y = sin(radians(self.ANGLE)) * self.SPEEDS[self.laser_index] * dt
		self.pos += pygame.math.Vector2((x, -y)) + pygame.math.Vector2(self.game.shake_offset)

	def hit(self) -> None:

		self.image = self.hit_image
		self.rect = self.image.get_rect(center = self.pos)
		self.collided += 1
		
class Lemonoid(pygame.sprite.Sprite):

	def __init__(self, angle: int, move_speed: int, size: int | float, game: Game, pos: tuple = None) -> None:

		super().__init__()

		# Constant Vars
		self.game = game
		self.HEALTHS = {1: 10, 2: 4, 3: 2, 4: 1} # size: health
		self.SIZES = {1: 1, 2: 0.5, 3: 0.25, 4: 0.125} # size: relative image size
		self.SCORES = {1: 100, 2: 50, 3: 20, 4: 10} # size: score gained when destroyed
		self.MOVE_SPEED = move_speed
		self.ROTATE_SPEED = 100 * size
		self.DIRECTION = angle
		self.DAMAGE = 1
		self.MAX_HEALTH = self.HEALTHS[size]
		self.EXPLOSION_SHAKE_VEL = 8
		
		# Vars
		self.angle = angle
		self.health = self.MAX_HEALTH
		self.colliding = False
		self.size = size

		# Images
		self.og_image = pygame.transform.rotate(pygame.transform.scale_by(pygame.image.load('Images/Lemonoid/Lemonoid.png'), self.SIZES[self.size] * 10), self.angle).convert_alpha()
		self.particle_images = [pygame.image.load(f'Images/Lemonoid/Break/Particle{i}.png').convert_alpha() for i in range(2)]
		self.image = self.og_image

		# Rects, Vectors, Masks
		if self.size == 1: self.rect = self.image.get_rect(center = (CENTER_X + cos(radians(self.angle)) * WIDTH, CENTER_Y - sin(radians(self.angle)) * WIDTH))
		else: self.rect = self.image.get_rect(center = pos)
		self.mask = pygame.mask.from_surface(self.image)
		self.pos = pygame.math.Vector2(self.rect.center)

		# SFX
		self.hit_sfx = pygame.mixer.Sound('Audio/SFX/Lemonoid/Hit.wav')
		self.explosion_sfx = pygame.mixer.Sound('Audio/SFX/Lemonoid/Explosion.wav')
		self.explosion_sfx_2 = pygame.mixer.Sound('Audio/SFX/Lemonoid/Explosion2.wav')

		# Health Bar
		if self.size != 4: 
			
			self.health_bar = pygame.sprite.GroupSingle(
				
				Health_Bar(
					offset = (0, -50) if self.size == 3 else (0, 0),
					size = 0.5 if self.size == 3 else (1 / self.size), 
					parent = self
				)

			)

	def update(self, dt: float | int) -> None:

		self.rect.center = self.pos
		self.mask = pygame.mask.from_surface(self.image)

		if self.size != 4:

			self.health_bar.update()
			self.health_bar.draw(screen)
			self.health_bar.sprite.segment.update()
			self.health_bar.sprite.segment.draw(screen)

		self.move(dt)
		self.rotate(dt)
		self.wrap_around()
		self.input()

	def input(self) -> None:

		if pygame.sprite.spritecollide(self, self.game.player.sprite.lasers_fired, False, pygame.sprite.collide_rect):

			collided_lasers = pygame.sprite.spritecollide(self, self.game.player.sprite.lasers_fired, False, pygame.sprite.collide_mask)
				
			if collided_lasers and not self.colliding: 
				
				self.hit(relative_collision_pos = pygame.sprite.collide_mask(self, collided_lasers[0]))
				self.colliding = True

			else: self.colliding = False
			
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

	def death_animation(self, size: int | float) -> None:

		# Shake
		if size == 1:

			self.game.shake_offset = (cos(self.game.player.sprite.angle) * 16, sin(self.game.player.sprite.angle) * 16)

			for i in range(self.EXPLOSION_SHAKE_VEL): self.game.shake_offsets.append((1, 1))

			self.game.shake_offsets.append((-1.8, -1.8))
			for i in range(self.EXPLOSION_SHAKE_VEL): self.game.shake_offsets.append((1, 1))

			for i in range(16):
				
				self.game.shake_offsets.append((uniform(-0.5, -0.8), uniform(-0.5, -0.8)))
				for i in range(self.EXPLOSION_SHAKE_VEL): self.game.shake_offsets.append((1, 1))

			self.game.shake_offsets.append((0, 0))

		# Explosion
		self.game.explosions.add(

			Explosion(
				type = 0 if size == 1 else 1, 
			 	pos = self.pos, 
				frames = self.game.explosion_frames, 
				game = self.game
			)

		)

		# Particles
		for i in range(int(25 / size)):
			
			self.game.particles.add(

				Particle(
					start_pos = self.pos,
					angle = (360 / int(25 / size)) * i,
					image = choice(self.particle_images), 
					move_speed = randint(100, 500) / size,
					rotation_speed = randint(100, 500) * size,
					fade_speed = 100 * size,
					game = self.game
				)

			)	

	def hit(self, relative_collision_pos: tuple | pygame.math.Vector2) -> None:

		self.health -= self.DAMAGE

		# SFX
		if SFX: self.hit_sfx.play()
		self.game.add_score(5)
		
		# Flash Effect
		array = pygame.PixelArray(self.image)
		array.replace((255, 228, 0), (255, 255, 255))
		array.close()

		if self.health > 0:

			# Position of Collision with Laser
			screen_collision_pos = (self.rect.topleft[0] + relative_collision_pos[0], self.rect.topleft[1] + relative_collision_pos[1])

			x = self.pos.x - screen_collision_pos[0]
			y = self.pos.y - screen_collision_pos[1]
			angle = (int(degrees(atan2(-y, x) % (2 * pi))) + 180) % 360
			
			# Particles
			for i in range(randint(2, 16)): 
			
				self.game.particles.add(

					Particle( 
						start_pos = screen_collision_pos,
						angle = randint(angle - 15, angle + 15),
						image = self.particle_images[i % len(self.particle_images)], 
						move_speed = randint(100, 200),
						rotation_speed = randint(100, 1000),
						fade_speed = 400,
						game = self.game
					)

				)
		
		else: self.death()

	def death(self) -> None:

		if self.size != 4:

			# New Lemonoids
			for i in range(3):

				self.game.lemonoids.add(

					Lemonoid(
						pos = self.pos,
						angle = self.DIRECTION + ((75 - randint(0, 30)) * (i - 1)), 
						move_speed = self.MOVE_SPEED * 1.5,
						size = self.size + 1, 
						game = self.game
					)

				)

			# Delete Heath Bar
			self.health_bar.sprite.segment.empty()
			self.health_bar.empty()

		# Score, Animation, SFX
		if SFX: 
			
			if self.size == 1: self.explosion_sfx.play()
			else: self.explosion_sfx_2.play()

		self.game.add_score(self.SCORES[self.size])
		self.death_animation(self.size)
		self.kill()

class Explosion(pygame.sprite.Sprite):

	def __init__(self, type: int, pos: tuple | pygame.math.Vector2, game: Game, frames: list = None) -> None:

		super().__init__()

		self.TYPE = type
		self.game = game
		self.ROTATE_SPEED = 20
		self.FADE_SPEED = 550
		self.finished = False
		self.alpha = 256
		
		if type == 0: 
			
			self.frames = frames
			self.frame_index = 0

		if type == 1:

			self.og_image = pygame.transform.scale_by(pygame.image.load(f'Images/Explosion/Flash.png'), 0.25).convert_alpha()

		self.image = self.og_image if type == 1 else self.frames[self.frame_index] 
		self.rect = self.image.get_rect(center = pos)
		self.pos = pygame.math.Vector2(self.rect.center)

	def update(self, dt: float | int) -> None:
		
		if self.TYPE == 0: self.rotate(dt)
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

	def __init__(self, offset: tuple, size: int | float, parent: Lemonoid, type: str | None = 'Base') -> None:

		super().__init__()

		self.SIZE = size
		self.TYPE = type
		self.OFFSET = offset
		self.parent = parent
		self.pos = (self.parent.pos.x + self.OFFSET[0], self.parent.pos.y + self.OFFSET[1])
		self.colour = (255, 0, 0)

		if self.TYPE == 'Base':

			self.MAX_HEALTH = self.parent.MAX_HEALTH
			self.health = self.parent.health
			self.health_percent = self.health / self.MAX_HEALTH

			self.image = pygame.transform.scale_by(pygame.image.load(f'Images/Health Bar/Base.png'), self.SIZE).convert_alpha()
			self.rect = self.image.get_rect(center = (self.parent.pos.x + self.OFFSET[0], self.parent.pos.y + self.OFFSET[1]))
			self.pos = pygame.math.Vector2(self.rect.center)
			self.segment = pygame.sprite.GroupSingle(Health_Bar(size = self.SIZE, offset = self.OFFSET, parent = self, type = 'Child'))

		if self.TYPE == 'Child':

			self.full_image = pygame.transform.scale_by(pygame.image.load('Images/Health Bar/Full.png'), self.SIZE).convert_alpha()
			self.empty_image = pygame.transform.scale_by(pygame.image.load('Images/Health Bar/Empty.png'), self.SIZE).convert_alpha()
			self.images = [self.full_image, self.empty_image]
			self.image_index = 0

			self.image = self.images[self.image_index]
			self.rect = self.image.get_rect(center = ((self.parent.rect.topleft[0] + self.image.get_width() + 2) - self.image.get_width() * (((1 - self.parent.health_percent) * 2) % 1), self.parent.rect.topleft[1]))
			self.pos = pygame.math.Vector2(self.rect.topleft)

	def update(self) -> None: 

		if self.TYPE == 'Base':

			self.health = self.parent.health
			self.health_percent = self.health / self.MAX_HEALTH
			self.pos = pygame.math.Vector2((self.parent.pos.x + self.OFFSET[0], self.parent.pos.y - self.OFFSET[1]))
			self.rect.center = self.pos
			self.change_colour()

		if self.TYPE == 'Child':

			self.position()
			self.change_colour()

			if self.parent.health_percent < 1 / self.parent.MAX_HEALTH: self.pos.x = self.parent.rect.topleft[0] + (2 * self.SIZE) 
			if self.parent.health_percent > 0.5: self.image_index = 0
			if self.parent.health_percent <= 0.5: self.image_index = 1

			self.image = self.images[self.image_index]
			self.rect = self.image.get_rect(topleft = self.pos)

	def change_colour(self) -> None:

		if self.TYPE == 'Base': 

			if self.health_percent > 0.5: new_colour = ((255 * (1 - self.health_percent)) * 2, 255, 0)
			if self.health_percent <= 0.5: new_colour = (255, (255 * self.health_percent) * 2, 0)

			array = pygame.PixelArray(self.image)
			array.replace(self.colour, new_colour)
			array.close()

			self.colour = new_colour
		
		if self.TYPE == 'Child': 

			if self.parent.health_percent > 0.5: new_colour = ((255 * (1 - self.parent.health_percent)) * 2, 255, 0)
			if self.parent.health_percent <= 0.5: new_colour = (255, (255 * self.parent.health_percent) * 2, 0)

			array = pygame.PixelArray(self.image)
			array.replace(self.colour, new_colour)
			array.close()

			self.colour = new_colour

	def position(self) -> None:

		self.pos.x = (self.parent.rect.topleft[0] + self.image.get_width() + (2 * self.SIZE)) - self.image.get_width() * (((1 - self.parent.health_percent) * 2) % 1)
		self.pos.y = self.parent.rect.topleft[1]

class Particle(pygame.sprite.Sprite):

	def __init__(self, start_pos: tuple | pygame.math.Vector2, angle: int | float, image: pygame.surface.Surface, move_speed: int, rotation_speed: int, fade_speed: int, game: Game) -> None:

		super().__init__()
		
		self.game = game
		self.ANGLE = angle
		self.MOVE_SPEED = move_speed
		self.ROTATE_SPEED = rotation_speed
		self.FADE_SPEED = fade_speed
		
		self.rotation_angle = 0
		self.alpha = 256

		self.og_image = image
		self.image = self.og_image

		self.rect = self.image.get_rect(center = start_pos)
		self.pos = pygame.math.Vector2(self.rect.center)

	def update(self, dt: int | float) -> None:

		self.rect.center = self.pos

		self.move(dt)
		self.rotate(dt)
		self.fade(dt)
		self.input()

	def input(self) -> None:

		if self.pos.y <= 0 - (self.image.get_height() / 2) or self.pos.y >= HEIGHT + (self.image.get_height() / 2): self.kill()
		if self.pos.x <= 0 - (self.image.get_width() / 2) or self.pos.x >= WIDTH + (self.image.get_width() / 2): self.kill()

	def move(self, dt: int | float) -> None:

		x = cos(radians(self.ANGLE)) * self.MOVE_SPEED * dt
		y = sin(radians(self.ANGLE)) * self.MOVE_SPEED * dt
		self.pos += pygame.math.Vector2((x, -y)) + pygame.math.Vector2(self.game.shake_offset)

	def rotate(self, dt: int | float) -> None:

		self.rotation_angle = (self.rotation_angle % 360) + self.ROTATE_SPEED * dt
		self.image = pygame.transform.rotate(self.og_image, self.rotation_angle).convert_alpha()
		self.rect = self.image.get_rect(center = self.pos)

	def fade(self, dt: float | int) -> None:

		self.alpha -= self.FADE_SPEED * dt
		self.image.set_alpha(self.alpha)
		if self.alpha <= 0: self.kill()

def main():

	game = Game()
	text = game.text
	player = game.player
	lasers_fired = player.sprite.lasers_fired
	lemonoids = game.lemonoids
	explosions = game.explosions
	cursor = game.cursor
	particles = game.particles

	pygame.display.set_caption('Lemonoids')

	previous_time = time()
	while True:

		dt = time() - previous_time
		previous_time = time()

		for event in pygame.event.get():

			if event.type == pygame.QUIT:

				game.save()
				pygame.quit()
				exit()

			if game.get_state() == game.S_PLAY:

				if event.type == game.LEMONOID_TIMER:

					angle = randint(0, 360)
					new_lemonoid = Lemonoid(angle = angle, move_speed = 75, size = 1, game = game)
					lemonoids.add(new_lemonoid)

				if event.type == player.sprite.BLINK_TIMER:
					player.sprite.blink()

			if game.get_state() == game.S_GAME_OVER:

				if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:

					game.reset()
					game.set_state(game.S_PLAY)

		screen.fill(BG_COLOUR)

		if game.get_state() == game.S_PLAY:

			# Game
			game.update()
			if game.shake_offsets: game.shake(game.shake_offsets.pop(0))

			# Particles
			particles.update(dt)
			particles.draw(screen)

			# Explosions
			explosions.update(dt)
			explosions.draw(screen)

			# Lasers
			lasers_fired.draw(screen)
			lasers_fired.update(dt)

			# Player
			player.update(dt)

			if not player.sprite.dead:

				player.draw(screen)

			elif player.sprite.dead:

				if pygame.time.get_ticks() - player.sprite.death_time >= 1500:
						
					if player.sprite.lives <= 0: game.game_over()
					else: player.sprite.respawn()

			
			# Lemonoids
			lemonoids.draw(screen)
			lemonoids.update(dt)

		# Text
		text.update()
		[screen.blit(line[0], line[1]) for line in text.texts]

		# Cursor
		cursor.update(dt)
		cursor.draw(screen)

		pygame.display.update()
		clock.tick(FPS)

if __name__ == '__main__': main()