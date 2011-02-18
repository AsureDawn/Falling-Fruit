#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

from time import sleep
from random import randint
from itertools import cycle as itercycle
import threading
import pygame

fruitstand = {}
fruitstand['basket'] = pygame.sprite.Group()
fruitstand['level'] = int()
fruitstand['score'] = int()
fruitstand['exit'] = False

land = pygame.sprite.Group()

cycle = itercycle(range(1,4))
surfaceslock = threading.Lock()

# min/max time, maxfruit for each level
# when score reaches value of nextlevel,
#  stats are altered accordingly.
levels = []
levels.append(({'maxfruit' : 5,  'mintime'  : 1,
                'maxtime'  : 5, 'nextlevel': 10 ** 3,
                'speed' : 1}))
levels.append(({'maxfruit' : 6,  'mintime'  : 1,
                'maxtime'  : 4,  'nextlevel': 3 * 10 ** 3,
                'speed' : 1.5}))
levels.append(({'maxfruit' : 15, 'mintime'  : 1,
                'maxtime'  : 3,  'nextlevel': 6 * 10 ** 3,
                'speed' : 2}))
levels.append(({'maxfruit' : 30, 'mintime'  : 1,
                'maxtime'  : 2,  'nextlevel': 10 ** 100,
                'speed' : 3}))

# Setup pygame
pygame.init()

WINDOWWIDTH = 600
WINDOWHEIGHT = 280
WINDOWSIZE = (WINDOWWIDTH, WINDOWHEIGHT)
MOVELEFT = 1
MOVERIGHT = 2
FROGSHOOTSLOPE = 5.0/4.0

pygame.display.set_caption('The fruit are falling!')

window = pygame.display.set_mode(WINDOWSIZE)
screen = pygame.display.get_surface()
firingrange = pygame.display.get_surface()
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))
clock = pygame.time.Clock()

pygame.mouse.set_visible(False)

fruit_img_path = os.path.join("data", "fruit.png")
frog_img_path = os.path.join("data", "frog.png")

def imgldr(imgpath):
    try:
        image = pygame.image.load(imgpath)
        image = image.convert_alpha()
    except(pygame.error):
        print("Cannot load image: %s" % (imgpath))
        raise SystemExit from message
    return image

fruit_image = imgldr(fruit_img_path)
fruit_image = fruit_image.subsurface(fruit_image.get_bounding_rect())
frog_image = imgldr(frog_img_path)
frog_image = frog_image.subsurface(frog_image.get_bounding_rect())

FRUITHEIGHT = fruit_image.get_height()

class Fruit(pygame.sprite.Sprite):
    """Moves the fruit based on position in fruitstand"""

    def __init__(self, xpos, rof):
        pygame.sprite.Sprite.__init__(self)
        self.image = fruit_image
        self.rect = self.image.get_rect()
        self.xpos = xpos
        self.ypos = int() - FRUITHEIGHT
        self.rof = rof # rate of fall
        self.rect.move_ip(self.xpos, self.ypos)

    def update(self, movey):
        """Move the fruit based on position in fruitstand"""
        self.rect.move_ip(0, movey)
        self.ypos += movey

class Frog(pygame.sprite.Sprite):
    """Moves the frog based on user input"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = frog_image
        self.rect = self.image.get_rect()
        self.xpos = round(WINDOWWIDTH / 2)
        self.flipped = False
        self.shooting = False
        self.rect.move_ip(self.xpos, WINDOWHEIGHT -
                                     self.image.get_height())

    def _shoot(self):
        for xpos in range(WINDOWWIDTH):
            if self.shooting is True:
                if self.flipped is False:
                    if xpos - self.xpos > WINDOWHEIGHT:
                        return
                    pygame.draw.line(firingrange, (255, 50, 50), (self.xpos + self.image.get_height(), WINDOWHEIGHT - self.image.get_height()), (xpos + self.image.get_height(), WINDOWHEIGHT + self.xpos - xpos - self.image.get_height()), 2)
                    for fruit in fruitstand['basket']:
                        if fruit.rect.collidepoint((xpos, WINDOWHEIGHT+self.xpos-xpos)):
                                print('Fruit shot!')
                                fruit.kill()
                                fruitstand['score'] += 100
                                return
                else:
                    if WINDOWHEIGHT - xpos - self.image.get_height() > WINDOWHEIGHT:
                        return
                    pygame.draw.line(firingrange, (255, 50, 50), (self.xpos, WINDOWHEIGHT - self.image.get_height()), (self.xpos - xpos, WINDOWHEIGHT - xpos - self.image.get_height()), 2)
                    for fruit in fruitstand['basket']:
                        if fruit.rect.collidepoint((self.xpos-xpos, WINDOWHEIGHT-xpos-self.image.get_height())):
                                print('Fruit shot!')
                                fruit.kill()
                                fruitstand['score'] += 100
                                return
            else:
                firingrange.blit(background, (0, 0))
                break
            sleep(.003)

    def update(self, direction=None, shoot=None):
        """Move frog left or right, or make him shoot"""
        if shoot is None: 
            if direction is MOVELEFT:
                if self.flipped is False:
                    with surfaceslock:
                        self.image = pygame.transform.flip(self.image, True, False)
                    self.flipped = True
                if self.xpos > 0:
                    self.xpos -= 1
                    self.rect.move_ip(-1, 0)
            elif direction is MOVERIGHT:
                if self.flipped is True:
                    with surfaceslock:
                        self.image = pygame.transform.flip(self.image, True, False)
                    self.flipped = False
                if self.xpos < WINDOWWIDTH - self.rect[2]:
                    self.xpos += 1
                    self.rect.move_ip(1, 0)
        elif shoot is True:
            self.shooting = True
            self._shoot()
        elif shoot is False:
            self.shooting = False


frog = Frog()
frog.add(land)

def main():
    fruitpopulator = threading.Thread(target=addfruit, args=(Fruit,))
    fruitpopulator.daemon = True
    fruitpopulator.start()

    while True:
        with surfaceslock:
            screen.blit(background, (0, 0))
            screen.blit(firingrange, (0, 0))
            fruitstand['basket'].draw(screen)
            land.draw(screen)
            pygame.display.flip()
        clock.tick(60)
        fruitfall()
        if frogmoving.is_set() is False:
            movefrog = threading.Thread(target=move, args=(MOVELEFT, stopfrog,))
            movefrog.daemon = True
        input(pygame.event.get())
        if fruitstand['score'] >= levels[fruitstand['level']]['nextlevel']:
            fruitstand['level'] += 1
            print('Level up!')

        if fruitstand['exit'] is True:
            # Exit and begin clean-up
            return

def addfruit(Fruit):
    # Get level information and num of fruit from fruitstand
    numfruit = len(fruitstand['basket'])

    while True:
        # Take a nap, waking every once in a while
        sleep(randint(levels[fruitstand['level']]['mintime'],
                      levels[fruitstand['level']]['maxtime']) / 4)
        if numfruit < levels[fruitstand['level']]['maxfruit']:
            # Add another fruit if there aren't too many
            fruitstand['basket'].add(Fruit(randint(1, WINDOWWIDTH - 24), randint(1, 3)))

def fruitfall():
    """Drops fruit by amount depending on the rate
       of fall and level.
       """
    cycleit = cycle.__next__()
    #print(fruitstand['basket'].sprites)

    for fruit in fruitstand['basket']:
        if fruit.rof <= cycleit:
            # The fruits are falling!
            fruit.update(fruit.rof *
                         levels[fruitstand['level']]['speed'])

            if fruit.ypos >= WINDOWHEIGHT - FRUITHEIGHT:
                fruit.kill()

def move(movedir, stopfrog):
    while True:
        if stopfrog.is_set() is True:
            break
        frog.update(direction=movedir)
        if fruitstand['level'] <= 3:
            sleep(1 / (1.6 ** (fruitstand['level'] + 8)))
        else:
            sleep(1 / (1.6 ** 11))
    frogmoving.clear()
    stopfrog.clear()

stopfrog = threading.Event()
frogmoving = threading.Event()

def input(events):
    if frogmoving.is_set() is False:
        stopfrog.clear() # Allows overlapping button presses
    for event in events:
        if (event.type == pygame.QUIT or
             (event.type == pygame.KEYDOWN and
              event.key == pygame.K_ESCAPE)):
                  fruitstand['exit'] = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if frogmoving.is_set() is False:
                    frogmoving.set()
                    movefrog = threading.Thread(target=move, args=(MOVELEFT, stopfrog,))
                    movefrog.daemon = True
                    movefrog.start()
            elif event.key == pygame.K_RIGHT:
                if frogmoving.is_set() is False:
                    movefrog = threading.Thread(target=move, args=(MOVERIGHT, stopfrog,))
                    movefrog.daemon = True
                    frogmoving.set()
                    movefrog.start()
            elif event.key == pygame.K_SPACE:
                stopfrog.set() # Frog can't move and shoot at once
                frog.update(shoot=False) # Frog can't shoot while shooting
                shootingfrog = threading.Thread(target=frog.update, kwargs={'shoot':True})
                shootingfrog.daemon = True
                shootingfrog.start() # Make frog shoot
                #frog.update(shoot=True) # Make frog shoot
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                stopfrog.set()
            elif event.key == pygame.K_RIGHT:
                stopfrog.set()
            elif event.key == pygame.K_SPACE:
                frog.update(shoot=False)
        #else:
        #    print('%s ' % (event.type))

if __name__ == '__main__':
    main()
