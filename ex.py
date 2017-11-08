import pygame
import sys
from texts import FontWrapper, MultiLineFontWrapper

pygame.init()

#big_size = width, height = 1280, 960
size = width, height = 640, 480
black = 0, 0, 0


def done_callback(self):
    print(self, 'Done')

#
try:
    f = pygame.font.Font('Pixeled.ttf', 20)
    bias = -10
except OSError:
    f = pygame.font.Font(pygame.font.get_default_font(), 30)
    bias = 0
my_text = MultiLineFontWrapper(f, 'This is kinda of a nice way to do the text thing,'
                                  ' but I want to have more than two lines to see if there is really a '
                                  'difference!'.upper(), 30, bias=bias, done=done_callback, done_arg='self')


screen = pygame.display.set_mode(size)


while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(black)
    my_text.blit(screen, pos=(50, 130))
    pygame.display.flip()


