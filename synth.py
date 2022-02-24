# Toshiaki Koike-Akino, 2022
# wrapping synthesizer in https://github.com/joaocarvalhoopen/Synthesizer_in_Python
# creating wave files in Sounds/{sound}/{note}{octave}.wav
import Synthesizer_in_Python.synthesizer as syn
import os
import argparse

# create wav
def main(args, verb=True):
    sounds = args.sounds
    octaves = args.octaves
    duration = args.duration
    rate = args.rate
    notes = args.notes

    for sound in sounds:
        for octave in octaves:
            for note in notes:
                path = f'Sounds/{sound}'
                os.makedirs(path, exist_ok=True)
                fname = f'{path}/{note}{octave}.wav'
                if verb: print('#saving', fname)

                signal = syn.generate(sound, note, octave, duration)
                syn.writeArrayToWavFilename(signal, rate, fname)

# args to inherit
def add_args(parser):
    parser = parser.add_argument_group(__file__)
    parser.add_argument('--sounds', default=['piano', 'organ', 'acoustic', 'edm'],
                        type=str, nargs='+', help='sound type')
    parser.add_argument('--notes', default=['C', 'C#', 'D', 'D#', 'E', 'F',
                                            'F#', 'G', 'G#', 'A', 'A#', 'B'],
                        type=str, nargs='+', help='sound note')
    parser.add_argument('--rate', default=44.1e3, type=float, help='sampling rate')
    parser.add_argument('--duration', default=1.0, type=float, help='sound duration (sec)')
    parser.add_argument('--octaves', default=[4], type=int, nargs='+',
                        help='sound octave')

# example args
def get_args():
    parser = argparse.ArgumentParser(__file__)

    add_args(parser)

    return parser.parse_args()

# example main
if __name__ == '__main__':

    args = get_args()
    
    main(args)
    
