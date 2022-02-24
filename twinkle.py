# Toshiaki Koike-Akino, 2022
# inspired by https://pyshine.com/How-to-play-piano-using-Python/
from threading import Thread
import pygame as pg
import time
import argparse
import os

# args
def add_args(parser):
    parser = parser.add_argument_group('twinkle')
    #parser.add_argument('--sound', default='piano', type=str, help='sound folder in path')
    parser.add_argument('--path', default='Sounds/piano', type=str, help='sound path')
    parser.add_argument('--duration', default=0.4, type=float, help='sound duration')

def get_args():
    parser = argparse.ArgumentParser(__file__)
    add_args(parser)
    return parser.parse_args()

# twinkle score
def get_score():
    twinkle = [
        'C4','C4','G4','G4','A4','A4','G4','G4',
        'F4','F4','E4','E4','D4','D4','C4','C4',
        'G4','G4','F4','F4','E4','E4','D4','D4',
        'G4','G4','F4','F4','E4','E4','D4','D4',
        'C4','C4','G4','G4','A4','A4','G4','G4',
        'F4','F4','E4','E4','D4','D4','C4','C4',
        ]
    return twinkle    

# play note
def play_notes(notePath, duration):
    #time.sleep(duration)
    pg.mixer.Sound(notePath).play()
    time.sleep(duration)
    #print(notePath)

# init pygame mixer
def init(num_channels=10):
    pg.mixer.init()
    pg.init()
    pg.mixer.set_num_channels(num_channels)

# main
def main(args, score, verb=False):
    init(len(score))
    
    # play score one by one
    for note in score:
        if verb: print(note)
        fname = '{}.wav'.format(note)
        fname = os.path.join(args.path, fname)
        th = Thread(target=play_notes, args=(fname, args.duration))

        th.start()
        th.join()

if __name__ == '__main__':
    args = get_args()    
    score = get_score()
    main(args, score)
    