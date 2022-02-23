#https://pyshine.com/How-to-play-piano-using-Python/
from threading import Thread
import pygame as pg
import time

twinkle = ['c4','c4','g4','g4','a4','a4','g4','g4',
	   'f4','f4','e4','e4','d4','d4','c4','c4',
	   'g4','g4','f4','f4','e4','e4','d4','d4',
	   'g4','g4','f4','f4','e4','e4','d4','d4',
	   'c4','c4','g4','g4','a4','a4','g4','g4',
	   'f4','f4','e4','e4','d4','d4','c4','c4',
	   ]

pg.mixer.init()
pg.init()
pg.mixer.set_num_channels(len(twinkle))

def play_notes(notePath, duration):
    time.sleep(duration)
    pg.mixer.Sound(notePath).play()
    time.sleep(duration)
    print(notePath)

sound = 'piano'
path = f'Sounds/{sound}/'

#th = {}
for note in twinkle:
    print(note)
    #fname = path+'{}.ogg'.format(note)
    fname = path+'{}.wav'.format(note.upper())
    th = Thread(target=play_notes, args=(fname, 0.2))

    th.start()
    th.join()

