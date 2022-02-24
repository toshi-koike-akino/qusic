# (c) Toshiaki Koike-Akino, 2022
# VQC music player
import pennylane as qml
import pennylane.numpy as np
import argparse
import dill as pickle
#import pickle
import os

# args
def get_args():
    parser = argparse.ArgumentParser(__file__)
    # general
    parser.add_argument('--verb', action='store_true', help='verbose')
    parser.add_argument('--seed', default=1, type=int, help='seed for main')
    
    # qusic args
    qusic_args(parser)
    
    return parser.parse_args()

# qusic args
def qusic_args(parser):
    parser = parser.add_argument_group('qusic')
    parser.add_argument('--ansatz', default='BasicEntanglerLayers', 
                        choices=['BasicEntanglerLayers', 'StronglyEntanglingLayers', 'RandomLayers'],
                        type=str, help='ansatz')
    parser.add_argument('--layers', default=[1, 7], type=int, nargs=2, help='anwatz layers size (for RandomLayers)')
    parser.add_argument('--wires', default=['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4'], 
                        type=str, nargs='+', help='qubit wires to associate with notes')
    parser.add_argument('--dev', default='default.qubit', type=str, help='QPU device')
    parser.add_argument('--qseed', default=42, type=int, help='RandomLayers random seed')
    parser.add_argument('--shots', default=1, type=int, help='number of quantum shots')
    parser.add_argument('--load', default=None, type=str, help='loading model file')

# quantum musician (qusician) class
class Qusic():
    def __init__(self, 
                 layers=[1,7], wires=['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4'],
                 dev='default.qubit', ansatz='BasicEntanglerLayers', shots=1, qseed=42,
                 verb=False,
                 ):
        self.layers = layers
        self.wires = wires
        self.shots = shots
        self.verb = verb
        self.qseed = qseed if ansatz == 'RandomLayers' else -1

        self.dev = qml.device(dev, wires=self.wires)
        self.dev_shots = qml.device(dev, wires=self.wires, shots=self.shots)
        if self.verb: print('shots:', self.shots, 'layers:', self.layers, 'wires:', self.wires, 'dev:', self.dev)
        
        # quantum ansatz: default RandomLayers
        self.ansatz = getattr(qml, ansatz)
        if self.verb: print('ansatz:', self.ansatz)
        
        # weights
        self.shape = self.ansatz.shape(*self.layers)
        if self.verb: print('shape:', self.shape)
        
        weights = self.init_weights(self.shape)
        self.set_weights(weights)
        if self.verb: print('weights:', self.weights)
        
        # quantum node
        self.qnode = qml.QNode(self.circuit, device=self.dev)
        self.qnode_shots = qml.QNode(self.circuit, device=self.dev_shots)
        if self.verb: print('qnode:', self.qnode)
        
    # initialize weights
    def init_weights(self, shape):
        return np.random.randn(*shape, requires_grad=True)
    
    # set 
    def set_weights(self, weights):
        self.weights = weights
    
    # qcircuit
    def circuit(self, inputs, sample=False):
        # basis embedding
        qml.BasisEmbedding(inputs, wires=self.wires)
        
        # ansatz
        if self.qseed == -1:
            self.ansatz(weights=self.weights, wires=self.wires)
        else: # RandomLayers
            self.ansatz(weights=self.weights, wires=self.wires, seed=self.qseed)            
        
        # measure
        if sample:
            return qml.sample(wires=self.wires)
        else:
            return tuple([qml.expval(qml.PauliZ(i)) for i in self.wires])

    # forward; given one-hot-encoded note
    def __call__(self, inputs, sample=False):
        if self.verb: print('sample:', sample, 'inputs:', inputs.shape, inputs)

        # VQC
        if sample:
            outputs = self.qnode_shots(inputs, sample=sample)        
        else:
            outputs = self.qnode(inputs, sample=sample)        
        if self.verb: print('outputs:', outputs.shape, outputs)

        return outputs
    
    # notes list to wires basis; ['C4', 'D4'] -> [1,1,0,0,0,0,0]
    def notes2basis(self, notes):
        basis = np.zeros(len(self.wires), dtype=int)
        # search note in wires
        for k in range(len(self.wires)):
            if self.wires[k] in notes:
                basis[k] = 1
        return basis
    
    # wires basis to notes list; [1,1,0,0,0,0,0] -> ['C4', 'D4']
    def basis2notes(self, basis):
        notes = list()
        # search wire in basis
        for k in range(len(basis)):
            if basis[k]:
                notes.append(self.wires[k])
        return notes
    
    # draw
    def draw(self, inputs=None):
        drawer = qml.draw(self.qnode, expansion_strategy='device')
        if inputs is None:
            inputs = np.zeros(len(self.wires))
        print(drawer(inputs))
        
        spec = qml.specs(self.qnode)(inputs)
        print('# spec', spec)
    
    # save model    
    def save(self, fname='model.pkl', path=None):
        if path != None:
            os.makedirs(path, exist_ok=True)
            fname = os.path.join(path, fname)
        if self.verb: print('saving model:', fname)
        with open(fname, 'wb') as file:
            pickle.dump(self, file)
    
    def save_weights(self, fname='weights.npy', path=None):
        if path != None:
            os.makedirs(path, exist_ok=True)
            fname = os.path.join(path, fname)
        if self.verb: print('saving weights:', fname)
        with open(fname, 'wb') as file:
            np.save(file, self.weights)        
        
    # load model (not for cls but self)
    def load(self, fname='model.pkl', path=None):
        if path != None:
            fname = os.path.join(path, fname)
        if self.verb: print('loading model:', fname)
        with open(fname, 'rb') as file:
            model = pickle.load(file)
        self.__dict__.update(model.__dict__)

    def load_weights(self, fname='weights.npy', path=None):
        if path != None:
            fname = os.path.join(path, fname)
        if self.verb: print('loading weights:', fname)
        with open(fname, 'rb') as file:
            self.weights = np.load(file)

    # load model (not for self but cls)
    @classmethod
    def load_model(cls, fname='model.pkl', path=None, verb=False):
        if path != None:
            fname = os.path.join(path, fname)
        if verb: print('loading model:', fname)
        with open(fname, 'rb') as file:
            model = pickle.load(file)
        return model

                
# model
def get_model(args, verb=False):
    if args.load == None:
        model = Qusic(layers=args.layers, wires=args.wires, 
                      dev=args.dev, ansatz=args.ansatz, 
                      shots=args.shots, qseed=args.qseed,
                      verb=verb)
    else:
        model = Qusic.load_model(args.load, verb=verb)
    if verb: print('get_model:', model)
    return model

# seed
def seeding(seed, verb=False):
    if seed > 0:
        np.random.seed(seed)
        if verb: print('seeding:', seed)
    
# example use case
if __name__ == '__main__':
    args = get_args()
    if args.verb: print('#args:', args)

    # seed simulation    
    seeding(args.seed, verb=args.verb)

    # get qusic model
    model = get_model(args, verb=args.verb)

    # toy inputs    
    inputs = np.random.randint(2, size=(len(args.wires)))
    print(inputs)
    
    # toy outputs
    outputs = model(inputs)
    print(outputs)
    outputs = model(inputs, sample=True)
    print(outputs)
    
    # draw model/spec
    model.draw(inputs)

    # save model
    model.save(fname='model1.pkl', path='models')
    # load model for new instance
    model = Qusic(layers=[0,0], verb=args.verb)
    model.load(fname='model1.pkl', path='models')
    model.draw(inputs)
    # load model from class
    model = Qusic.load_model(fname='model1.pkl', path='models')
    # re-draw
    model.draw(inputs)
    
    # save weights
    model.save_weights()
    model = Qusic()
    model.draw()
    model.load_weights()
    model.draw()
    
    # basis<->notes
    basis = model.notes2basis(['C4', 'G4'])
    print(basis)
    notes = model.basis2notes(basis)
    print(notes)