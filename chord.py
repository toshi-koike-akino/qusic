# Toshiaki Koike-Akino, 2022
# Chord ansatz 

import pennylane as qml

wires = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
dev = qml.device('default.qubit', wires=wires, shots=1)

# harmony triplet
harmony = [['c', 'e', 'g'], # CM
           ['d', 'f', 'a'], # Dm
#           ['e', 'g', 'b'], # Em
#           ['f', 'a', 'c'], # FM
#           ['g', 'b', 'd'], # GM
#           ['a', 'c', 'e'], # Am
#           ['b', 'd', 'f'], # Bdm
           ]

# chord ansatz
def chord():
    for triplet in harmony:
        print(triplet)
        qml.CNOT(wires=[triplet[0], triplet[1]])        
        qml.CNOT(wires=[triplet[0], triplet[2]])

@qml.qnode(dev)
def circuit(melody):
    # basis encoding
    qml.BasisEmbedding(melody, wires=wires)
    
    # chord ansatz
    chord()
    
    return qml.sample(wires=wires)

melody = {
    'c': [1,0,0,0,0,0,0],
    'd': [0,1,0,0,0,0,0],
    'e': [0,0,1,0,0,0,0],
    'f': [0,0,0,1,0,0,0],
    'g': [0,0,0,0,1,0,0],
    'a': [0,0,0,0,0,1,0],
    'b': [0,0,0,0,0,0,1],
}
for note in wires:
    print(note)
    print(circuit(melody[note]))
