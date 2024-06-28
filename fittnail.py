def execute(img_size: tuple[int, int], screen_size: tuple[int, int]) -> tuple[int, int]:

	if img_size[0] > screen_size[0]: img_size = (screen_size[0], (screen_size[0] / img_size[0]) * img_size[1])
	if img_size[1] > screen_size[1]: img_size = ((screen_size[1] / img_size[1]) * img_size[0], screen_size[1]) 

	return img_size