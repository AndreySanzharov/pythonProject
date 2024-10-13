import pygame

STOPPED_PLAYING = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(STOPPED_PLAYING)


numbers_of_sounds = list(range(0, 7))
curr_number = 0


def play_music():
    global curr_number
    pygame.mixer.music.load(r'data\sound_{}.mp3'.format(curr_number))
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.15)
    curr_number += 1
    curr_number = curr_number % len(numbers_of_sounds)
