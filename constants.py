def splashscreen_size(img_size: tuple[int | float, int | float], screen_size: tuple[int, int]) -> tuple[float, float]:

	if img_size[0] > screen_size[0]: img_size = (screen_size[0], (screen_size[0] / img_size[0]) * img_size[1])
	if img_size[1] > screen_size[1]: img_size = ((screen_size[1] / img_size[1]) * img_size[0], screen_size[1]) 

	return img_size

# Screen Setup
WINDOW_W, WINDOW_H = 1000, 750
CENTER_X, CENTER_Y = WINDOW_W / 2, WINDOW_H / 2
SCALE = 1
WIDTH, HEIGHT = WINDOW_W * SCALE, WINDOW_H * SCALE
X0 = CENTER_X - (WINDOW_W / 2) * SCALE
Y0 = CENTER_Y - (WINDOW_H / 2) * SCALE
X1 = CENTER_X + (WINDOW_W / 2) * SCALE
Y1 = CENTER_Y + (WINDOW_H / 2) * SCALE

# Game
FPS = 144
DEBUG = True

# Colours
BG_COLOUR = '#101010'
BLACK = '#000000'
DARK_GREY = '#404040'
GREY = '#808080'
WHITE = '#ffffff'
GREEN = '#33ff00'
YELLOW = '#ffea00'
RED = '#ff2600'
DARK_RED = '#801300'

# Audio (0-1; 0 = off, 1 = full volume)
SFX_VOL = 1
MUSIC_VOL = 0

# Explosion
EXPLOSION_FRAME_COUNT = 20 # (1-360, higher = slower load time, higher possible explosion rotate speed, lower = vice versa)