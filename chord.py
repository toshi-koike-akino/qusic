# Toshiaki Koike-Akino, 2022
# Chord ansatz 

import pennylane as qml
import argparse

def get_wires():
    wires = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
    return wires

def get_device(wires, shots=1):
    dev = qml.device('default.qubit', wires=wires, shots=shots)
    return dev

def get_chords(chords=['CM', 'Dm', 'Em', 'FM', 'GM', 'Am', 'Bdm']):
    # harmony triplet
    harmony = {
        'CM': ['c', 'e', 'g'], # CM
        'Dm': ['d', 'f', 'a'], # Dm
        'Em': ['e', 'g', 'b'], # Em
        'FM': ['f', 'a', 'c'], # FM
        'GM': ['g', 'b', 'd'], # GM
        'Am': ['a', 'c', 'e'], # Am
        'Bdm': ['b', 'd', 'f'], # Bdm
    }
    triplets = list()
    for chord in chords:
        triplets.append(harmony[chord])
    return triplets

# chord ansatz
def chord_ansatz(chords):
    for triplet in chords:
        #print(triplet)
        qml.CNOT(wires=[triplet[0], triplet[1]])        
        qml.CNOT(wires=[triplet[0], triplet[2]])


def get_melody(note):
    melody = {
        'c': [1,0,0,0,0,0,0],
        'd': [0,1,0,0,0,0,0],
        'e': [0,0,1,0,0,0,0],
        'f': [0,0,0,1,0,0,0],
        'g': [0,0,0,0,1,0,0],
        'a': [0,0,0,0,0,1,0],
        'b': [0,0,0,0,0,0,1],
    }
    return melody[note]

def main(args, verb=False):
    # chord ansats selection
    chords = get_chords(args.chords)
    if verb: print('chords', chords)
    
    # quantum circuit
    wires = get_wires()
    if verb: print('wires', wires)

    dev = get_device(wires, shots=args.shots)
    if verb: print('dev', dev)
    
    #@qml.qnode(dev)
    def circuit(melody):
        # basis encoding
        qml.BasisEmbedding(melody, wires=wires)
        
        # chord ansatz
        chord_ansatz(chords)
        
        return qml.sample(wires=wires)

    qnode = qml.QNode(circuit, dev)
    
    # play each strings
    for note in wires:
        if verb: print('note', note)
        
        inputs = get_melody(note) # basis string
        if verb: print('inputs', inputs)
        
        outputs = qnode(inputs)
        print(note, outputs)

def get_args():
    parser = argparse.ArgumentParser(__file__)
    parser.add_argument('--verb', action='store_true', help='verbose')
    parser.add_argument('--chords', default=['CM', 'Dm', 'Em', 'FM', 'GM', 'Am', 'Bdm'], 
                        type=str, nargs='+', help='selected chord ansatz')
    parser.add_argument('--shots', default=1, type=int, help='number of shots')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    main(args, verb=args.verb)
