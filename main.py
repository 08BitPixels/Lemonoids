import pygame
import os

from time import time
from math import atan2, cos, sin, degrees, radians, pi
from random import randint, uniform, choice
from typing import Union

from constants import (

	splashscreen_size,
	WINDOW_W, WINDOW_H, WIDTH, HEIGHT, CENTER_X, CENTER_Y, SCALE, X0, Y0, X1, Y1, FPS, # screen setup
	DEBUG, 
	SFX_VOL, MUSIC_VOL, # audio
	EXPLOSION_FRAME_COUNT,
	BG_COLOUR, BLACK, DARK_GREY, GREY, WHITE, RED, YELLOW, GREEN # colours

)

# PYGAME SETUP
pygame.init()
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
clock = pygame.time.Clock()

# Fonts
h1_font = pygame.font.Font('Fonts/pixel_font.ttf', int(75 * SCALE))
h2_font = pygame.font.Font('Fonts/pixel_font.ttf', int(50 * SCALE))
h3_font = pygame.font.Font('Fonts/pixel_font.ttf', int(25 * SCALE))

# Window Setup
pygame.display.set_icon(pygame.image.load('Images/UI/Icon.ico'))
pygame.display.set_caption('Lemonoids | INITIALISING...')
screen.fill(BG_COLOUR)
# Cover
cover = pygame.image.load('Images/UI/Cover/Cover.png').convert_alpha()
cover = pygame.transform.scale(cover, splashscreen_size(img_size = cover.get_size(), screen_size = (WIDTH, HEIGHT))).convert_alpha()
screen.blit(cover, cover.get_rect(center = (CENTER_X, CENTER_Y)))
pygame.display.update()

class Game:

	def __init__(
			
			self, 
			screen: dict[str, int | float],
			game: dict[str, int | float],
			audio: dict[str, int | float],
			colours: dict[str, str], 
			fonts: dict[str, pygame.font.Font],
			explosions: dict[str, int]
		
		) -> None:

		'''
		screen: dict[
				'scale': int | float
			],
			game: dict[
				'debug': bool
			],
			audio: dict[
				'sfx_vol': int | float,
				'music_vol': int | float
			],
			colours: dict[
				'black': str, 
				'dark_grey': str, 
				'grey': str, 
				'white': str, 
				'red': str, 
				'yellow': str, 
				'green': str
			], 
			fonts: dict[
				'h1': pygame.font.Font, 
				'h2': pygame.font.Font, 
				'h3': pygame.font.Font,
			],
			explosions: dict[
				'frame_count': int
			]
		]
		'''

		def load_explosion_frames() -> list:

			def create_explosion_frames(frame_count: int) -> list:

				frames = []

				os.makedirs('Images/Explosion/Frames')
				for i in range(frame_count):

					image = pygame.transform.scale_by(pygame.transform.rotate(pygame.image.load('Images/Explosion/God-Rays.png'), i), 0.5).convert_alpha()
					frames.append(image)
					pygame.image.save(image, f'Images/Explosion/Frames/{i}.png')
					pygame.display.set_caption(f'Lemonoids | INITIALISING... Creating New Explosion Frames... {round(i / frame_count * 100, 1)}%')
					pygame.display.update()

				return frames

			frames = []

			if os.path.isdir('Images/Explosion/Frames'):

				frame_count = len([entry for entry in os.listdir('Images/Explosion/Frames') if os.path.isfile(os.path.join('Images/Explosion/Frames', entry))])

				if frame_count != self.EXPLOSION_FRAME_COUNT:

					for path in os.listdir('Images/Explosion/Frames'): os.remove(f'Images/Explosion/Frames/{path}')
					os.rmdir('Images/Explosion/Frames')
					frames = create_explosion_frames(self.EXPLOSION_FRAME_COUNT)

				else:
					
					for i in range(frame_count):

						frames.append(pygame.image.load(f'Images/Explosion/Frames/{i}.png'))
						pygame.display.set_caption(f'Lemonoids | INITIALISING... {round(i / frame_count * 100, 1)}%')

			else: frames = create_explosion_frames(self.EXPLOSION_FRAME_COUNT)

			return frames
		
		start_time = time()

		self.STATES = {'play': 0, 'game_over': 1}
		self.MUSIC_VOL = audio['music_vol']
		self.SFX_VOL = audio['sfx_vol']
		self.COLOURS = colours
		self.FONTS = fonts
		self.SCALE = screen['scale']
		self.EXPLOSION_FRAME_COUNT = explosions['frame_count']
		self.DEBUG = game['debug']

		self.state = self.STATES['play']
		self.score = 0
		with open('Saves/save.txt', 'r') as save: self.highscore = int(save.readlines()[0].strip('HIGHSCORE = '))
		self.shake_offset = (0.0, 0.0)
		self.shake_offsets: list[tuple[float, float]] = []
		self.explosion_frames = load_explosion_frames()

		self.player = pygame.sprite.GroupSingle(Player(game = self))
		self.cursor = Cursor(game = self)
		self.lemonoids: pygame.sprite.Group = pygame.sprite.Group()
		for i in range(3): self.lemonoids.add(Lemonoid(angle = randint(0, 360), move_speed = 75, size = 1, game = self))
		self.explosions: pygame.sprite.Group = pygame.sprite.Group()
		self.text = Text(game = self)
		self.particles: pygame.sprite.Group = pygame.sprite.Group()
		self.life_count_meter: pygame.sprite.Group = pygame.sprite.Group()
		for i in range(self.player.sprite.MAX_LIVES): self.life_count_meter.add(Life_Count_Meter(game = self, index = i, origin = (CENTER_X, Y1 - 79)))

		# Music
		self.game_music = pygame.mixer.Sound('Audio/Music/game_music.wav')
		self.game_music.set_volume(self.MUSIC_VOL)
		if self.MUSIC_VOL > 0: self.game_music.play(-1)

		self.lemonoid_frequency = 15000
		self.LEMONOID_TIMER = pygame.USEREVENT + 0
		pygame.time.set_timer(self.LEMONOID_TIMER, self.lemonoid_frequency)

		print(f'Game Initialised {round(time() - start_time, 1)}s')

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

	def get_state(self) -> int:
		return self.state

	def set_state(self, state: int) -> None:
		self.state = state

	def shake(self, offset: tuple) -> None:
		self.shake_offset = (self.shake_offset[0] * offset[0], self.shake_offset[1] * offset[1])

	def add_shake_offsets(self, velocity: int) -> None:

		self.shake_offset = (cos(self.player.sprite.angle) * 16, sin(self.player.sprite.angle) * 16)

		for i in range(velocity): self.shake_offsets.append((1, 1))

		self.shake_offsets.append((-1.8, -1.8))
		for i in range(velocity): self.shake_offsets.append((1, 1))

		for i in range(16):
			
			self.shake_offsets.append((uniform(-0.5, -0.8), uniform(-0.5, -0.8)))
			for i in range(velocity): self.shake_offsets.append((1, 1))

		self.shake_offsets.append((0, 0))

	def play_sfx(self, sfx: pygame.mixer.Sound) -> None:
		if self.SFX_VOL > 0: sfx.play()

	def load_sfx(self, path: str) -> pygame.mixer.Sound:
		
		sfx = pygame.mixer.Sound(path)
		sfx.set_volume(self.SFX_VOL)
		return sfx

	def load_img(self, path: str) -> pygame.surface.Surface:
		return pygame.transform.scale_by(pygame.image.load(path), self.SCALE).convert_alpha()

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
		self.particles.empty()
		self.life_count_meter.empty()

	def game_over(self) -> None:

		self.score = 0
		self.state = self.STATES['game_over']
		self.reset()

	def set_game(self) -> None:

		self.reset()
		self.respawn()

		for i in range(self.player.sprite.MAX_LIVES): 
			self.life_count_meter.add(
				Life_Count_Meter(
					game = self,
					index = i, 
					origin = (CENTER_X, Y1 - 79)
				)
			)

	def save(self) -> None:

		print('Saving... 0%')
		with open('Saves/save.txt', 'w') as save: save.write(f'HIGHSCORE = {self.highscore}')
		print('Saving... 100%')

class Text:

	def __init__(self, game: Game) -> None:

		self.game = game
		self.COLOURS = game.COLOURS
		self.FONTS = game.FONTS
		self.texts: list[tuple[pygame.surface.Surface, pygame.rect.Rect]] = []

		# Texts

		self.fps_text1 = self.FONTS['h3'].render('FPS', False, self.COLOURS['grey'], self.COLOURS['black'])
		self.fps_text1_rect = self.fps_text1.get_rect(topleft = (X0, Y0))

		self.fps_text2 = pygame.surface.Surface((0, 0))
		self.fps_text2_rect = self.fps_text2.get_rect()

		# Play
		self.score_text = pygame.surface.Surface((0, 0))
		self.score_text_rect = self.score_text.get_rect()

		self.play_text1 = self.FONTS['h3'].render('Score', False, self.COLOURS['dark_grey'])
		self.play_text1_rect = self.play_text1.get_rect(center = (CENTER_X, Y0 + 170 * SCALE))

		self.highscore_text = pygame.surface.Surface((0, 0))
		self.highscore_text_rect = self.highscore_text.get_rect()

		self.play_text2 = self.FONTS['h3'].render('Highscore', False, self.COLOURS['dark_grey'])
		self.play_text2_rect = self.play_text2.get_rect(center = (CENTER_X, Y0 + 70 * SCALE))

		self.lives_text = pygame.surface.Surface((0, 0))
		self.lives_text_rect = self.lives_text.get_rect()

		self.lives_text_shadow = pygame.surface.Surface((0, 0))
		self.lives_text_shadow_rect = self.lives_text_shadow.get_rect()

		self.play_text3 = pygame.surface.Surface((0, 0))
		self.play_text3_rect = self.play_text3.get_rect()

		# Game Over
		self.game_over_text1 = self.FONTS['h1'].render('GAME OVER', False, self.COLOURS['white'])
		self.game_over_text1_rect = self.game_over_text1.get_rect(center = (CENTER_X, CENTER_Y))

		self.game_over_text2 = self.FONTS['h3'].render('Press [SPACE] to retry', False, self.COLOURS['yellow'])
		self.game_over_text2_rect = self.game_over_text2.get_rect(center = (CENTER_X, CENTER_Y + 45 * SCALE))

	def update(self) -> None:

		fps = round(clock.get_fps(), 1)
		fps_colour = self.COLOURS['green'] if fps > 60 else self.COLOURS['yellow'] if fps < 60 and fps > 10 else self.COLOURS['red']

		self.fps_text2 = self.FONTS['h3'].render(str(fps), False, fps_colour, self.COLOURS['black'])
		self.fps_text2_rect = self.fps_text2.get_rect(topleft = self.fps_text1_rect.topright)

		if self.game.get_state() == self.game.STATES['play']:

			self.score_text = self.FONTS['h1'].render(str(self.game.score), False, self.COLOURS['white'])
			self.score_text_rect = self.score_text.get_rect(center = (CENTER_X, Y0 + 120 * SCALE))

			self.highscore_text = self.FONTS['h2'].render(str(self.game.highscore), False, self.COLOURS['grey'])
			self.highscore_text_rect = self.highscore_text.get_rect(center = (CENTER_X, Y0 + 30 * SCALE))

			self.play_text3 = self.FONTS['h3'].render('Lives' if self.game.player.sprite.lives != 1 else 'Life', False, self.COLOURS['dark_grey'])
			self.play_text3_rect = self.play_text3.get_rect(center = (CENTER_X, Y1 - 30 * SCALE))

			self.lives_text = self.FONTS['h1'].render(str(self.game.player.sprite.lives), False, [self.COLOURS['red'], self.COLOURS['red'], self.COLOURS['yellow'], self.COLOURS['green']][self.game.player.sprite.lives] if self.game.player.sprite.lives <= 3 else self.COLOURS['green'])
			self.lives_text_rect = self.lives_text.get_rect(midbottom = (CENTER_X, Y1 - 40 * SCALE))

			self.lives_text_shadow = self.FONTS['h1'].render(str(self.game.player.sprite.lives), False, self.COLOURS['black'])
			self.lives_text_shadow.set_alpha(128)
			self.lives_text_shadow_rect = self.lives_text.get_rect(midbottom = (CENTER_X, Y1 - 35 * SCALE))

			self.texts = [

				(self.fps_text1, self.fps_text1_rect),
				(self.fps_text2, self.fps_text2_rect),

				(self.score_text, self.score_text_rect),
				(self.play_text1, self.play_text1_rect),

				(self.highscore_text, self.highscore_text_rect),
				(self.play_text2, self.play_text2_rect),

				(self.lives_text_shadow, self.lives_text_shadow_rect),
				(self.lives_text, self.lives_text_rect),
				(self.play_text3, self.play_text3_rect)

			]

		elif self.game.get_state() == self.game.STATES['game_over']:

			self.texts = [

				(self.game_over_text1, self.game_over_text1_rect),
				(self.game_over_text2, self.game_over_text2_rect)

			]

		else: 
			
			self.texts = [
				(self.fps_text1, self.fps_text1_rect),
				(self.fps_text2, self.fps_text2_rect)
			]

class Cursor:

	def __init__(self, game: Game) -> None:

		self.game = game
		self.ROTATE_SPEED = 500
		self.angle = 0.0
		self.index = {self.game.STATES['play']: 1, self.game.STATES['game_over']: 0}[self.game.get_state()]

		self.cursor_unfocus_image = pygame.transform.scale_by(pygame.image.load('Images/UI/Cursor/Cursor/Unfocus.png'), 3).convert_alpha()
		self.cursor_focus_image = pygame.transform.scale_by(self.game.load_img('Images/UI/Cursor/Cursor/Focus.png'), 3).convert_alpha()
		self.focussed = False
		
		self.crosshair_unfocus_image = pygame.transform.scale_by(pygame.image.load('Images/UI/Cursor/Crosshair/Unfocus.png'), 3).convert_alpha()
		self.crosshair_focus_image = pygame.transform.scale_by(pygame.image.load('Images/UI/Cursor/Crosshair/Focus.png'), 3).convert_alpha()
		self.focussed = False

		self.images = [[self.cursor_unfocus_image, self.cursor_focus_image], [self.crosshair_unfocus_image, self.crosshair_focus_image]]
		self.image = self.images[self.index][self.focussed]
		self.cursor = pygame.cursors.Cursor((self.image.get_width() // 2, self.image.get_height() // 2), self.image)

	def update(self, dt: float) -> None:
		
		def input() -> None:

			self.focussed = pygame.mouse.get_pressed()[0]
			if self.focussed and self.game.get_state() == self.game.STATES['play']: rotate()

		def rotate() -> None:

			self.angle = (self.angle % 360) + self.ROTATE_SPEED * dt
			self.image = pygame.transform.rotate(self.images[self.index][self.focussed], self.angle).convert_alpha()

		self.cursor = pygame.cursors.Cursor((self.image.get_width() // 2, self.image.get_height() // 2), self.image)
		pygame.mouse.set_cursor(self.cursor)

		self.index = {self.game.STATES['play']: 1, self.game.STATES['game_over']: 0}[self.game.get_state()]
		self.image = self.images[self.index][self.focussed]
		input()

class Player(pygame.sprite.Sprite):

	def __init__(self, game: Game) -> None:

		super().__init__()

		self.game = game

		# Constant Vars
		self.SIZE = 2.5
		self.ACCELERATION_VEL = 0.999
		self.SPEED = 3
		self.MAX_SPEED = 3
		self.FIRE_RATE = 0
		self.FIRE_RATES = {0: 8} # ship index: fire rate
		self.ACCURACIES = {0: 1} # ship index: accuracy (fire spread) in degrees
		self.MAX_LIVES = 3
		self.BLINK_FREQUENCY = 250
		self.BLINK_TIMER = pygame.USEREVENT + 1
		self.EXPLOSION_SHAKE_VEL = 4
		self.MAX_HEALTH = 4

		# Vars
		self.x_vel = 0.0
		self.y_vel = 0.0
		self.angle = 0.0
		self.fire_buffer = 0
		self.ship_index = 0
		self.lives = self.MAX_LIVES
		self.collided = False
		self.dead = False
		self.death_time = 0
		self.blink_index = 0
		self.health = self.MAX_HEALTH

		# Images
		self.og_image = pygame.transform.scale_by(self.game.load_img(f'Images/Player/Ship{self.ship_index}/Normal.png'), self.SIZE).convert_alpha()
		self.shoot_image = pygame.transform.scale_by(self.game.load_img(f'Images/Player/Ship{self.ship_index}/Shoot.png'), self.SIZE).convert_alpha()
		self.thruster_image = pygame.transform.scale_by(self.game.load_img(f'Images/Player/Ship{self.ship_index}/Thruster.png'), self.SIZE).convert_alpha()
		self.blink_image = pygame.transform.scale_by(self.game.load_img(f'Images/Player/Ship{self.ship_index}/Blink.png'), self.SIZE).convert_alpha()

		self.break_images = [pygame.transform.scale_by(self.game.load_img(f'Images/Player/Ship{self.ship_index}/Break/Break{i}.png'), self.SIZE).convert_alpha() for i in range(3)]
		self.particle_images = [pygame.transform.scale_by(self.game.load_img(f'Images/Player/Ship{self.ship_index}/Break/Particle{i}.png'), self.SIZE).convert_alpha() for i in range(2)]

		# Image, Rect, Mask, Pos
		self.image = self.og_image
		self.rect = self.image.get_rect(center = (CENTER_X, CENTER_Y))
		self.mask = pygame.mask.from_surface(self.image)
		self.pos = pygame.math.Vector2(self.rect.center)

		# SFX
		self.shoot_sfx = self.game.load_sfx('Audio/SFX/Player/Shoot.wav')
		self.death_sfx = self.game.load_sfx('Audio/SFX/Player/Death.wav')
		self.hit_sfx = self.game.load_sfx('Audio/SFX/Player/Hit.mp3')

		self.lasers_fired: pygame.sprite.Group = pygame.sprite.Group()
		self.health_bar = pygame.sprite.GroupSingle(Health_Bar(game = self.game, offset = (0, -40), size = 0.75, parent = self))

		self.set_fire_rate()

	def update(self, dt: float) -> None:
		
		def input() -> None:
			
			def hit(damage: int) -> None:
	
				def death_animation() -> None:

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
					self.game.add_shake_offsets(velocity = self.EXPLOSION_SHAKE_VEL)
					self.game.play_sfx(self.death_sfx)
				
					self.death_time = pygame.time.get_ticks()

				self.health -= damage

				if self.health <= 0:

					self.dead = True
					self.lives -= 1
					self.health_bar.sprite.segment.empty()
					self.health_bar.empty()
					death_animation()

				else: self.game.play_sfx(self.hit_sfx)
		
			def move(angle: float, momentum: int) -> None:

				self.x_vel += cos(radians(angle)) * self.ACCELERATION_VEL ** 2 * momentum * self.SPEED * dt
				if self.x_vel > self.MAX_SPEED: self.x_vel = self.MAX_SPEED
				if self.x_vel < -self.MAX_SPEED: self.x_vel = -self.MAX_SPEED
				self.pos.x += self.x_vel + self.game.shake_offset[0]

				self.y_vel += sin(radians(angle)) * self.ACCELERATION_VEL ** 2 * momentum * self.SPEED * dt
				if self.y_vel > self.MAX_SPEED: self.y_vel = self.MAX_SPEED
				if self.y_vel < -self.MAX_SPEED: self.y_vel = -self.MAX_SPEED
				self.pos.y -= self.y_vel + self.game.shake_offset[1]

			def rotate_to(pos: tuple, og_img: pygame.surface.Surface) -> None:
		
				x_distance = pos[0] - self.pos.x
				y_distance = pos[1] - self.pos.y
				angle_to = degrees(atan2(-y_distance, x_distance) % (2 * pi))
				self.angle = round(angle_to, 2)
				self.image = pygame.transform.rotate(og_img, self.angle).convert_alpha()
				self.rect = self.image.get_rect(center = self.pos)

			def shoot() -> None:

				if self.fire_buffer < 0: self.set_fire_rate()
				elif self.fire_buffer == 0:
					
					self.game.play_sfx(self.shoot_sfx)
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

			keys_pressed = pygame.key.get_pressed()
			mouse_pressed = pygame.mouse.get_pressed()[0]
			mouse_pos = pygame.mouse.get_pos()

			# Movement
			if not self.dead: move(self.angle, keys_pressed[pygame.K_w])

			# Direction
			if self.fire_buffer != 0: rotate_to(mouse_pos, self.og_image)
			if self.fire_buffer == 0: rotate_to(mouse_pos, self.shoot_image)
			if keys_pressed[pygame.K_w] and randint(0, 1) == 0: rotate_to(mouse_pos, self.thruster_image)
			if self.blink_index == 1: rotate_to(mouse_pos, self.blink_image)

			if (mouse_pressed or keys_pressed[pygame.K_SPACE]) and not self.dead: shoot()	
			elif not mouse_pressed and not keys_pressed[pygame.K_SPACE] and not self.dead: self.set_fire_rate()

			# Collisions
			if pygame.sprite.spritecollide(self, self.game.lemonoids, False, pygame.sprite.collide_rect) and not self.dead and not self.game.DEBUG:

				collided_lemonoids = pygame.sprite.spritecollide(self, self.game.lemonoids, False, pygame.sprite.collide_mask)

				if collided_lemonoids:

					hit(5 - collided_lemonoids[0].size)
					collided_lemonoids[0].death(False)
					self.collided = True

				else: self.collided = False
		
		def wrap_around() -> None:

			if self.pos.x > X1 + self.image.get_width() / 2: self.pos.x = X0 - self.image.get_width() / 2
			elif self.pos.x < X0 - self.image.get_width() / 2: self.pos.x = X1 + self.image.get_width() / 2
			if self.pos.y > Y1 + self.image.get_height() / 2: self.pos.y = Y0 - self.image.get_height() / 2
			elif self.pos.y < Y0 - self.image.get_height() / 2: self.pos.y = Y1 + self.image.get_height() / 2

		self.rect.center = (round(self.pos.x), round(self.pos.y))
		self.mask = pygame.mask.from_surface(self.image)
		input()
		wrap_around()

		if not self.dead:

			self.health_bar.update()
			self.health_bar.sprite.segment.update()

			self.health_bar.draw(screen)
			self.health_bar.sprite.segment.draw(screen)
			self.health_bar.sprite.render_font()

	def blink(self) -> None:
		self.blink_index = (self.blink_index % 2) + 1

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
		self.health = self.MAX_HEALTH
		self.health_bar = pygame.sprite.GroupSingle(Health_Bar(game = self.game, offset = (0, -40), size = 0.75, parent = self))
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
		self.health = self.MAX_HEALTH
		self.health_bar = pygame.sprite.GroupSingle(Health_Bar(game = self.game, offset = (0, -40), size = 0.75, parent = self))
		self.lasers_fired.empty()

class Laser(pygame.sprite.Sprite):

	def __init__(
			
			self, 
			start_pos: tuple[int, int] | pygame.math.Vector2, 
			angle: int | float, size: int | float, 
			laser_index: int,
			game: Game
		
		) -> None:

		super().__init__()
		
		self.laser_index = laser_index
		self.game = game
		self.ANGLE = angle
		self.SIZE = size
		self.SPEEDS = {0: 1000} # laser index: speed
		self.DAMAGES = {0: 1} # laser index: damage to lemonoid
		self.collided = 0

		self.image = pygame.transform.rotate(pygame.transform.scale_by(self.game.load_img(f'Images/Laser/Laser{self.laser_index}.png'), self.SIZE), self.ANGLE).convert_alpha()
		self.hit_image = pygame.transform.rotate(pygame.transform.scale_by(self.game.load_img('Images/Explosion/Flash.png'), self.SIZE / 8), self.ANGLE).convert_alpha()
		self.mask = pygame.mask.from_surface(self.image)

		self.rect = self.image.get_rect(center = start_pos)
		self.pos = pygame.math.Vector2(self.rect.center)

	def update(self, dt: int | float) -> None:
		
		def input() -> None:

			if self.pos.y <= Y0 - (self.image.get_height() / 2) or self.pos.y >= Y1 + (self.image.get_height() / 2): self.kill()
			if self.pos.x <= X0 - (self.image.get_width() / 2) or self.pos.x >= X1 + (self.image.get_width() / 2): self.kill()

		def move() -> None:

			x = cos(radians(self.ANGLE)) * self.SPEEDS[self.laser_index] * dt
			y = sin(radians(self.ANGLE)) * self.SPEEDS[self.laser_index] * dt
			self.pos += pygame.math.Vector2((x, -y)) + pygame.math.Vector2(self.game.shake_offset)

		if self.collided >= 1: self.kill()
		self.rect.center = (round(self.pos.x), round(self.pos.y))

		move()
		input()

	def hit(self) -> None:

		self.image = self.hit_image
		self.rect = self.image.get_rect(center = self.pos)
		self.collided += 1
		
class Lemonoid(pygame.sprite.Sprite):

	def __init__(
			
			self,
			game: Game, 
			angle: float, 
			move_speed: int | float, 
			size: int, 
			pos: tuple | pygame.math.Vector2 = (0, 0)

		) -> None:

		super().__init__()

		# Constant Vars
		self.game = game
		self.HEALTHS = {1: 10, 2: 4, 3: 2, 4: 1} # size: health
		self.SCORES = {1: 100, 2: 50, 3: 20, 4: 10} # size: score gained when destroyed
		self.MOVE_SPEED = move_speed
		self.ROTATE_SPEED = randint(75, 125) * size
		self.DIRECTION = angle + 180 % 360
		self.MAX_HEALTH = self.HEALTHS[size]
		self.EXPLOSION_SHAKE_VEL = 4
		
		# Vars
		self.angle = self.DIRECTION
		self.size = size
		self.health = self.MAX_HEALTH
		self.colliding = {'laser': False, 'lemonoid': False}
		self.colliding_first = False
		self.first_frame = True
		self.outside_frame_on_spawn = True
		self.dead = False

		# Images
		self.og_image = pygame.transform.scale_by(self.game.load_img(f'Images/Lemonoid/Normal/{self.size}.png'), 2.5).convert_alpha()
		self.particle_images = [self.game.load_img(f'Images/Lemonoid/Break/Particle{i}.png').convert_alpha() for i in range(2)]
		self.image = pygame.transform.rotate(self.og_image, self.angle).convert_alpha()

		# Rects, Vectors, Masks, Pos
		if self.size == 1: self.rect = self.image.get_rect(center = (CENTER_X + cos(radians(angle)) * max(WIDTH, HEIGHT), CENTER_Y - sin(radians(angle)) * max(WIDTH, HEIGHT)))
		else: self.rect = self.image.get_rect(center = pos)
		self.mask = pygame.mask.from_surface(self.image)
		self.pos = pygame.math.Vector2(self.rect.center)

		# SFX
		self.hit_sfx = self.game.load_sfx('Audio/SFX/Lemonoid/Hit.wav')
		self.explosion_sfx = self.game.load_sfx('Audio/SFX/Lemonoid/Explosion.wav')
		self.explosion_sfx_2 = self.game.load_sfx('Audio/SFX/Lemonoid/Explosion2.wav')
		for sfx in [self.hit_sfx, self.explosion_sfx, self.explosion_sfx_2]: sfx.set_volume(sfx.get_volume() * 0.3)

		# Health Bar
		if self.size != 4: 
			
			self.health_bar = pygame.sprite.GroupSingle(
				
				Health_Bar(
					game = self.game,
					offset = (0, -50) if self.size == 3 else (0, 0),
					size = 0.5 if self.size == 3 else (1 / self.size), 
					parent = self
				)

			)

	def update(self, dt: float) -> None:

		def input() -> None:

			# Laser Collisions
			if pygame.sprite.spritecollide(self, self.game.player.sprite.lasers_fired, False, pygame.sprite.collide_rect):

				collided_lasers = pygame.sprite.spritecollide(self, self.game.player.sprite.lasers_fired, False, pygame.sprite.collide_mask)

				if collided_lasers and not self.colliding['laser']: 
					
					collision_pos = pygame.sprite.collide_mask(self, collided_lasers[0])
					self.hit(relative_collision_pos = collision_pos if collision_pos else (0, 0), damage = collided_lasers[0].DAMAGES[collided_lasers[0].laser_index], object = collided_lasers[0])
					for laser in collided_lasers: laser.hit()
					self.colliding['laser'] = True

				else: self.colliding['laser'] = False
			
			# Other Lemonoid Collisions
			other_lemonoids = self.game.lemonoids.copy()
			other_lemonoids.remove(self)

			if pygame.sprite.spritecollide(self, other_lemonoids, False, pygame.sprite.collide_rect):

				collided_lemonoids = pygame.sprite.spritecollide(self, other_lemonoids, False, pygame.sprite.collide_mask)

				if collided_lemonoids and not self.colliding['lemonoid']:

					if self.first_frame: self.colliding_first = True

					if not self.colliding_first: 
						
						collision_pos = pygame.sprite.collide_mask(self, collided_lemonoids[0])
						self.hit(relative_collision_pos = collision_pos if collision_pos else (0, 0), damage = 4 - (collided_lemonoids[0].size - 1), object = self)
						collided_lemonoids[0].hit(relative_collision_pos = pygame.sprite.collide_mask(self, collided_lemonoids[0]), damage = 4 - (self.size - 1), object = self)
					
						self.colliding['lemonoid'] = True

				else:
					
					if self.colliding_first: self.colliding_first = False
					self.colliding['lemonoid'] = False

		def move() -> None:

			x = cos(radians(self.DIRECTION)) * self.MOVE_SPEED * dt
			y = sin(radians(self.DIRECTION)) * self.MOVE_SPEED * dt
			self.pos += (x + self.game.shake_offset[0], -y - self.game.shake_offset[1])

		def rotate() -> None:

			self.angle = (self.angle % 360) + self.ROTATE_SPEED * dt
			self.image = pygame.transform.rotate(self.og_image, self.angle).convert_alpha()
			self.rect = self.image.get_rect(center = self.pos)

		def wrap_around() -> None:

			if self.pos.x >= X1 + self.og_image.get_width() / 2: self.pos.x = X0 - self.og_image.get_width() / 2
			elif self.pos.x <= X0 - self.og_image.get_width() / 2: self.pos.x = X1 + self.og_image.get_width() / 2
			elif self.pos.y >= Y1 + self.og_image.get_width() / 2: self.pos.y = Y0 - self.og_image.get_width() / 2
			elif self.pos.y <= Y0 - self.og_image.get_width() / 2: self.pos.y = Y1 + self.og_image.get_width() / 2

		def check_outside_frame() -> bool:
			return ((self.pos.x >= X1 + self.og_image.get_width() / 2) or (self.pos.x <= X0 - self.og_image.get_width() / 2) or (self.pos.y >= Y1 + self.og_image.get_width() / 2) or (self.pos.y <= Y0 - self.og_image.get_width() / 2))

		self.rect.center = (round(self.pos.x), round(self.pos.y))
		self.mask = pygame.mask.from_surface(self.image)

		move()
		rotate()
		if not self.outside_frame_on_spawn: wrap_around()
		input()

		if self.outside_frame_on_spawn and not check_outside_frame(): self.outside_frame_on_spawn = False
		if self.first_frame: self.first_frame = False

	def render_debug(self) -> None:

		diagonal = (WIDTH ** 2 + HEIGHT ** 2) ** 0.5 * 2

		pygame.draw.line(
			surface = screen, 
			color = 'Blue', 
			start_pos = self.pos, 
			end_pos = (self.pos.x + cos(radians(self.DIRECTION)) * diagonal, self.pos.y - sin(radians(self.DIRECTION)) * diagonal), 
			width = round(2 * SCALE)
		)
		pygame.draw.line(
			surface = screen, 
			color = 'Dark Blue', 
			start_pos = self.pos, 
			end_pos = (self.pos.x - cos(radians(self.DIRECTION)) * diagonal, self.pos.y + sin(radians(self.DIRECTION)) * diagonal), 
			width = round(2 * SCALE)
		)
		pygame.draw.line(
			surface = screen, 
			color = 'Red', 
			start_pos = self.pos, 
			end_pos = (self.pos.x + cos(radians(self.angle)) * self.og_image.get_width() * (2 / 3), self.pos.y - sin(radians(self.angle)) * self.og_image.get_width() * (2 / 3)), 
			width = round(2 * SCALE)
		)

	def render_health_bar(self) -> None:

		if self.size != 4 and self.health > 0:

			self.health_bar.update()
			self.health_bar.sprite.segment.update()
			self.health_bar.draw(screen)
			self.health_bar.sprite.segment.draw(screen)
			self.health_bar.sprite.render_font()

	def hit(self, relative_collision_pos: tuple[int, int] | pygame.math.Vector2, damage: int, object: Union[Laser, 'Lemonoid']) -> None:

		def death() -> None:

			def death_animation() -> None:

				# Shake
				if self.size == 1: self.game.add_shake_offsets(velocity = self.EXPLOSION_SHAKE_VEL)

				# Explosion
				self.game.explosions.add(

					Explosion(
						type = 0 if self.size == 1 else 1, 
						pos = self.pos, 
						frames = self.game.explosion_frames, 
						game = self.game
					)

				)

				# Particles
				for i in range(int(25 / self.size)):
					
					self.game.particles.add(

						Particle(
							start_pos = self.pos,
							angle = (360 / int(25 / self.size)) * i,
							image = choice(self.particle_images), 
							move_speed = randint(100, 500) / self.size,
							rotation_speed = randint(100, 500) * self.size,
							fade_speed = 100 * self.size,
							game = self.game
						)

					)	

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
			if self.size == 1: self.game.play_sfx(self.explosion_sfx)
			else: self.game.play_sfx(self.explosion_sfx_2)

			if isinstance(object, Laser): self.game.add_score(self.SCORES[self.size])
			death_animation()
			self.kill()
			self.dead = True

		self.health -= damage

		# SFX
		self.game.play_sfx(self.hit_sfx)
		if isinstance(object, Laser): self.game.add_score(5)
		
		# Flash Effect
		array = pygame.PixelArray(self.image)
		array.replace((255, 228, 0), (255, 255, 255))
		array.close()

		# Position of Collision
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

		if self.health <= 0 and not self.dead: death()

class Explosion(pygame.sprite.Sprite):

	def __init__(
			
			self, 
			game: Game, 
			type: int,
			pos: tuple | pygame.math.Vector2, 
			frames: list = []
			
		) -> None:

		super().__init__()

		self.TYPE = type
		self.game = game
		self.ROTATE_SPEED = 40
		self.FADE_SPEED = 550
		self.finished = False
		self.alpha = 256.0
		
		if type == 0: 
			
			self.frames = frames
			self.frame_index = 0.0

		if type == 1:

			self.og_image = pygame.transform.scale_by(self.game.load_img('Images/Explosion/Flash.png'), 0.25).convert_alpha()

		self.image = self.og_image if type == 1 else self.frames[int(self.frame_index)] 
		self.rect = self.image.get_rect(center = pos)
		self.pos = pygame.math.Vector2(self.rect.center)

	def update(self, dt: float) -> None:

		def fade() -> None:

			self.alpha -= self.FADE_SPEED * dt
			self.image.set_alpha(int(self.alpha))
			if self.alpha <= 0: self.kill()
		
		def rotate() -> None:

			self.frame_index = (self.frame_index + self.ROTATE_SPEED * dt) % len(self.frames)
			self.image = self.frames[int(self.frame_index)]
			self.rect = self.image.get_rect(center = self.pos + pygame.math.Vector2(self.game.shake_offset))

		if self.TYPE == 0: rotate()
		fade()
		self.pos.x += self.game.shake_offset[0]
		self.pos.y -= self.game.shake_offset[1]

class Health_Bar(pygame.sprite.Sprite):

	def __init__(
			
			self, 
			game: Game, 
			offset: tuple, 
			size: int | float, 
			parent: Union[Player, Lemonoid, 'Health_Bar']
		
		) -> None:

		super().__init__()

		self.game = game
		self.SIZE = size
		self.OFFSET = offset
		self.parent = parent
		self.pos: pygame.math.Vector2 = pygame.math.Vector2(0, 0)
		self.colour = (255, 0, 0)

		if isinstance(self.parent, (Player, Lemonoid)):

			self.COLOURS = {'white': WHITE, 'black': BLACK}
			self.MAX_HEALTH = self.parent.MAX_HEALTH
			self.health = self.parent.health
			self.health_percent = self.health / self.MAX_HEALTH

			self.image = pygame.transform.scale_by(self.game.load_img('Images/Health Bar/Base.png'), self.SIZE).convert_alpha()
			self.rect = self.image.get_rect(center = (self.parent.pos.x + self.OFFSET[0], self.parent.pos.y + self.OFFSET[1]))
			self.pos = pygame.math.Vector2(self.rect.center)
			self.segment: pygame.sprite.GroupSingle = pygame.sprite.GroupSingle(Health_Bar(game = self.game, size = self.SIZE, offset = self.OFFSET, parent = self))

			# Text
			self.font = pygame.font.Font('Fonts/pixel_font.ttf', int(15 * SCALE))
			self.font.set_bold(True)

			self.text = pygame.surface.Surface((0, 0))
			self.text_rect = self.text.get_rect()

			self.text_shadow = pygame.surface.Surface((0, 0))
			self.text_shadow_rect = self.text_shadow.get_rect()

		if isinstance(self.parent, Health_Bar):

			self.full_image = pygame.transform.scale_by(self.game.load_img('Images/Health Bar/Full.png'), self.SIZE).convert_alpha()
			self.empty_image = pygame.transform.scale_by(self.game.load_img('Images/Health Bar/Empty.png'), self.SIZE).convert_alpha()
			self.images = [self.full_image, self.empty_image]
			self.image_index = 0

			self.image = self.images[self.image_index]
			self.rect = self.image.get_rect(center = ((self.parent.rect.topleft[0] + self.image.get_width() + 2) - self.image.get_width() * (((1 - self.parent.health_percent) * 2) % 1), self.parent.rect.topleft[1]))
			self.pos = pygame.math.Vector2(self.rect.topleft)

	def update(self) -> None: 
		
		def change_colour() -> None:
		
			health_percent = self.health_percent if isinstance(self.parent, (Player, Lemonoid)) else self.parent.health_percent

			if health_percent > 0.5: new_colour = (round((255 * (1 - health_percent)) * 2), 255, 0)
			if health_percent <= 0.5: new_colour = (255, round((255 * health_percent) * 2), 0)

			array = pygame.PixelArray(self.image)
			array.replace(self.colour, new_colour)
			array.close()

			self.colour = new_colour

		if isinstance(self.parent, (Player, Lemonoid)):

			self.health = self.parent.health
			self.health_percent = self.health / self.MAX_HEALTH
			
			self.pos = pygame.math.Vector2((self.parent.pos.x + self.OFFSET[0], self.parent.pos.y - self.OFFSET[1]))
			self.rect.center = (round(self.pos.x), round(self.pos.y))

			self.text = self.font.render(str(self.health), False, self.COLOURS['white'])
			self.text_rect = self.text.get_rect(midright = (self.pos[0] - self.image.get_width() / 2 - self.image.get_width() / 20, self.pos[1] - self.image.get_height() / 10))

			self.text_shadow = self.font.render(str(self.health), False, self.COLOURS['black'])
			self.text_shadow.set_alpha(128)
			self.text_shadow_rect = self.text.get_rect(midright = (self.text_rect.midright[0], self.text_rect.midright[1] + self.image.get_height() / 10))

			change_colour()

		if isinstance(self.parent, Health_Bar):

			self.pos.x = (self.parent.rect.topleft[0] + self.image.get_width() + (2 * self.SIZE)) - self.image.get_width() * (((1 - self.parent.health_percent) * 2) % 1)
			self.pos.y = self.parent.rect.topleft[1]

			change_colour()

			if self.parent.health_percent < 1 / self.parent.MAX_HEALTH: self.pos.x = self.parent.rect.topleft[0] + (2 * self.SIZE) 
			if self.parent.health_percent > 0.5: self.image_index = 0
			if self.parent.health_percent <= 0.5: self.image_index = 1

			self.image = self.images[self.image_index]
			self.rect = self.image.get_rect(topleft = self.pos)

	def render_font(self) -> None:

		screen.blit(self.text_shadow, self.text_shadow_rect)
		screen.blit(self.text, self.text_rect)

class Particle(pygame.sprite.Sprite):

	def __init__(
			
		self, 
		start_pos: tuple | pygame.math.Vector2, 
		angle: int | float, 
		image: pygame.surface.Surface, 
		move_speed: int | float, 
		rotation_speed: int | float, 
		fade_speed: int | float, 
		game: Game

	) -> None:

		super().__init__()
		
		self.game = game
		self.ANGLE = angle
		self.MOVE_SPEED = move_speed
		self.ROTATE_SPEED = rotation_speed
		self.FADE_SPEED = fade_speed
		
		self.rotation_angle = 0.0
		self.alpha = 256.0

		self.og_image = image
		self.image = self.og_image

		self.rect = self.image.get_rect(center = start_pos)
		self.pos = pygame.math.Vector2(self.rect.center)

	def update(self, dt: int | float) -> None:

		def input() -> None:

			if self.pos.y <= Y0 - (self.image.get_height() / 2) or self.pos.y >= Y1 + (self.image.get_height() / 2): self.kill()
			if self.pos.x <= X0 - (self.image.get_width() / 2) or self.pos.x >= X1 + (self.image.get_width() / 2): self.kill()

		def move() -> None:

			x = cos(radians(self.ANGLE)) * self.MOVE_SPEED * dt
			y = sin(radians(self.ANGLE)) * self.MOVE_SPEED * dt
			self.pos += pygame.math.Vector2((x, -y)) + pygame.math.Vector2(self.game.shake_offset)

		def rotate() -> None:

			self.rotation_angle = (self.rotation_angle % 360) + self.ROTATE_SPEED * dt
			self.image = pygame.transform.rotate(self.og_image, self.rotation_angle).convert_alpha()
			self.rect = self.image.get_rect(center = self.pos)

		def fade() -> None:

			self.alpha -= self.FADE_SPEED * dt
			self.image.set_alpha(int(self.alpha))
			if self.alpha <= 0: self.kill()

		self.rect.center = (round(self.pos.x), round(self.pos.y))

		move()
		rotate()
		fade()
		input()

class Life_Count_Meter(pygame.sprite.Sprite):

	def __init__(
			
			self, 
			game: Game, 
			origin: tuple, 
			index: int
			
		) -> None:

		super().__init__()

		self.game = game
		self.player = self.game.player.sprite
		self.INDEX = index
		self.SIZE = 4
		self.OFFSET = 10
		self.ORIGIN = origin
		self.ship = {'index': self.player.ship_index, 'max_lives': self.player.MAX_LIVES}

		self.image = pygame.transform.rotate(pygame.transform.scale_by(self.game.load_img(f'Images/UI/Life Count Meter/Ship{self.ship['index']}.png'), self.SIZE), 90).convert_alpha()
		self.rect = self.image.get_rect(center = (self.ORIGIN[0] - (((self.image.get_width() + self.OFFSET) * (self.ship['max_lives'] - 1)) / 2), self.ORIGIN[1]))
		self.pos = pygame.math.Vector2(self.rect.center)

	def update(self, player_lives: int) -> None:

		self.rect.center = (round(self.pos.x), round(self.pos.y))

		if player_lives - 1 < self.INDEX: self.kill()
		self.pos[0] = (self.ORIGIN[0] - (((self.image.get_width() + self.OFFSET) * (player_lives - 1)) / 2)) + (self.OFFSET + self.image.get_width()) * self.INDEX

def main() -> None:

	game = Game(
		screen = {
			'scale': SCALE,
		},
		game = {
			'debug': DEBUG,
		},
		audio = {
			'sfx_vol': SFX_VOL,
			'music_vol': MUSIC_VOL
		},
		colours = {
			'black': BLACK, 
			'dark_grey': DARK_GREY, 
			'grey': GREY, 
			'white': WHITE, 
			'red': RED, 
			'yellow': YELLOW, 
			'green': GREEN
		},
		fonts = {
			'h1': h1_font,
			'h2': h2_font,
			'h3': h3_font
		},
		explosions = {
			'frame_count': EXPLOSION_FRAME_COUNT
		}
	)
	text = game.text
	player = game.player
	lasers_fired = player.sprite.lasers_fired
	lemonoids = game.lemonoids
	explosions = game.explosions
	cursor = game.cursor
	particles = game.particles
	life_count_meter = game.life_count_meter

	pygame.display.set_caption('Lemonoids')

	previous_time = time()
	while True:

		dt = time() - previous_time
		previous_time = time()

		# pygame event loop
		for event in pygame.event.get():

			if event.type == pygame.QUIT:

				game.save()
				pygame.quit()
				exit()

			if game.get_state() == game.STATES['play']:

				if event.type == game.LEMONOID_TIMER:

					angle = randint(0, 360)
					new_lemonoid = Lemonoid(angle = angle, move_speed = 75, size = 1, game = game)
					lemonoids.add(new_lemonoid)

				if event.type == player.sprite.BLINK_TIMER:
					player.sprite.blink()

			if game.get_state() == game.STATES['game_over']:

				if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:

					game.set_game()
					game.set_state(game.STATES['play'])


		# rendering game
		# ------------------
		screen.fill(BG_COLOUR)

		if game.get_state() == game.STATES['play']:

			# Debug
			if game.DEBUG: 

				pygame.draw.line(screen, DARK_GREY, (X0, CENTER_Y), (X1, CENTER_Y), 1)
				pygame.draw.line(screen, DARK_GREY, (CENTER_X, Y0), (CENTER_X, Y1), 1)
			
				pygame.draw.line(screen, DARK_GREY, (CENTER_X - 10, CENTER_Y), (CENTER_X + 10, CENTER_Y), round(3 * SCALE))
				pygame.draw.line(screen, DARK_GREY, (CENTER_X, CENTER_Y - 10), (CENTER_X, CENTER_Y + 10), round(3 * SCALE))

				pygame.draw.polygon(screen, DARK_GREY, [(X0, Y0), (X0 + WIDTH, Y0), (X0 + WIDTH, Y0 + HEIGHT), (X0, Y0 + HEIGHT)], 1)

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
			lemonoids.update(dt)
			lemonoids.draw(screen)
			if game.DEBUG: [lemonoid.render_debug() for lemonoid in lemonoids]
			for lemonoid in lemonoids: lemonoid.render_health_bar()

			# Life Count Meter
			life_count_meter.update(player_lives = player.sprite.lives)
			life_count_meter.draw(screen)

		# Text
		text.update()
		for line in text.texts: screen.blit(line[0], line[1])

		# Cursor
		cursor.update(dt)

		pygame.display.update()
		clock.tick(FPS)
		# ------------------

if __name__ == '__main__': main()