# (c) Toshiaki Koike-Akino, 2022
# quantum concert
import pennylane as qml
import pennylane.numpy as np
import argparse
import qusic
import twinkle
import Synthesizer_in_Python.synthesizer as syn

# args
def get_args():
    parser = argparse.ArgumentParser(__file__)
    # general
    parser.add_argument('--verb', action='store_true', help='verbose')
    parser.add_argument('--seed', default=1, type=int, help='seed for main')
    
    # add args
    add_args(parser)
    
    return parser.parse_args()

# qoncert args
def qoncert_args(parser):
    parser = parser.add_argument_group('qoncert')
    parser.add_argument('--melody', default=3, type=int, help='melody line octave')
    parser.add_argument('--harmony', default=4, type=int, help='harmony line octave')
    parser.add_argument('--record', default='play.npy', type=str, help='recording numpy file')
    parser.add_argument('--volume', default=0.8, type=float, help='harmony volume relative to melody')
    parser.add_argument('--delay', default=100, type=int, help='harmony delay')
    # synthesis
    parser.add_argument('--sound', default='piano', choices=['piano', 'organ', 'acoustic', 'edm'],
                        type=str, help='instrument sound type')
    parser.add_argument('--rate', default=44.1e3, type=float, help='sampling rate (Hz)')
    parser.add_argument('--duration', default=0.5, type=float, help='whole-note sound duration (sec)')
    parser.add_argument('--wav', default='play.wav', type=str, help='recording wave file')

# add args
def add_args(parser):
    # qusic args
    qusic.qusic_args(parser)
    
    # qoncert args
    qoncert_args(parser)

    # defaults
    #parser.set_defaults(wires=['C', 'D', 'E', 'F', 'G', 'A', 'B']) # single octave (w/o sharp)

# melody
def get_melody(model, score):
    melody = list()
    for note in score:
        basis = model.notes2basis(note)
        melody.append(basis)
    return np.stack(melody)

# play
def play(model, melody):
    played = list()
    for note in melody:
        typing = model(note, sample=True)
        played.append(typing)
    return np.stack(played)
    
# record
def record(music, fname='play.npy', path=None):
    if path != None:
        os.makedirs(path, exist_ok=True)
        fname = os.path.join(path, fname)
    if args.verb: print('recording', fname, music[0].shape, music[1].shape)
    np.save(fname, music)
    #melody, played = np.load('play.npy')

def synthesize(args, notes, octave=4):
    signals = list()
    for k in range(len(notes)):
        if notes[k] == 1:
            note = args.wires[k]
            signal = syn.generate(args.sound, note, octave, args.duration)
            # stroke dealy
            shift = (len(signals) + 1) * args.delay
            signal = np.roll(signal, shift)
            #print('signal', signal.shape)
            signals.append(signal)
            
    if len(signals) == 0: # break
        signal = syn.generate(args.sound, 'C', octave, args.duration)
        signals.append(signal * 0.0)
        
    signals = np.vstack(signals)
    #print('signals', signals.shape)
    #signals = np.sum(signals, axis=0)
    signals = np.mean(signals, axis=0)
    #print('sum', signals.shape)
    return signals


# encore; play again to synthesize wave
def encore(args, music, fname='play.wav'):
    melody, harmony = music
    #harmony = melody + np.roll(melody, 2, axis=1) + np.roll(melody, 4, axis=1) # target
    wave = list()
    # synthesize one by one
    for left, right in zip(melody, harmony): # left-hand melody, right-hand harmony
        if args.verb: print('left/right', left, right)
        L = synthesize(args, left, octave=args.melody) # melody play
        R = synthesize(args, right, octave=args.harmony) # harmony play
        signal = (L + R * args.volume) / (1.0 + args.volume)
        wave.append(signal)
    wave = np.hstack(wave)
    
    # save wav
    if args.verb: print('saving', fname, wave.shape)
    syn.writeArrayToWavFilename(wave, args.rate, fname)
    
    # play wav
    if args.verb: print('listen to ', fname)
    twinkle.init(2)
    twinkle.play_notes(fname, len(melody) * args.duration)

    
    
# main
def main(args):
    if args.verb: print('# args:', args)

    # random seed
    qusic.seeding(args.seed, verb=args.verb)
    
    # qusic player
    model = qusic.get_model(args, verb=args.verb)
    model.draw()
    #model.save()
    #model(np.random.randint(2, size=7))
    args.wires = model.wires.copy()

    # score
    score = twinkle.get_score(octave=0) # no octave info
    if args.verb: print('score:', score)
    
    # melody lines
    melody = get_melody(model, score)
    if args.verb: print('melody:', melody)

    # play harmony lines
    harmony = play(model, melody)
    if args.verb: print('harmony:', harmony)

    # record his playing
    music = (melody, harmony)
    record(music, fname=args.record)
    
    # encore
    encore(args, music, fname=args.wav)
    
    

if __name__ == '__main__':
    args = get_args()
    
    main(args)
