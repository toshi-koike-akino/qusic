# Toshiaki Koike-Akino, 2022
# VQC music player
import pennylane as qml
import pennylane.numpy as np
import argparse
import dill as pickle
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
    parser.add_argument('--ansatz', default='RandomLayers', type=str, help='ansatz')
    parser.add_argument('--layer', default=[1, 7], type=int, nargs=2, help='anwatz layer size (for RandomLayers)')
    parser.add_argument('--wires', default=['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4'], 
                        type=str, nargs='+', help='qubit wires to associate with notes')
    parser.add_argument('--dev', default='default.qubit', type=str, help='QPU device')
    parser.add_argument('--qseed', default=42, type=int, help='RandomLayers random seed')
    parser.add_argument('--shots', default=1, type=int, help='number of quantum shots')

# quantum musician (qusician) class
class Qusic():
    def __init__(self, 
                 layer=[1,7], wires=['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4'],
                 dev='default.qubit', ansatz='RandomLayers', qseed=42, shots=1,
                 verb=False,
                 ):
        self.layer = layer
        self.wires = wires
        self.shots = shots
        self.qseed = qseed
        self.verb = verb
        if self.verb: print('qseed:', self.qseed)

        self.dev = qml.device(dev, wires=self.wires, shots=self.shots)
        if self.verb: print('shots:', self.shots, 'layer:', self.layer, 'wires:', self.wires, 'dev:', self.dev)
        
        # quantum ansatz: default RandomLayers
        self.ansatz = getattr(qml, ansatz)
        if self.verb: print('ansatz:', self.ansatz)
        
        # weights
        self.shape = self.ansatz.shape(*self.layer)
        if self.verb: print('shape:', self.shape)
        
        self.weights = self.init_weights(self.shape)
        if self.verb: print('weights:', self.weights)
        
        # quantum node
        self.qnode = qml.QNode(self.circuit, device=self.dev)
        if self.verb: print('qnode:', self.qnode)
        
    # initialize weights
    def init_weights(self, shape):
        return np.random.randn(*shape, requires_grad=True)
    
    # qcircuit
    def circuit(self, inputs, sample=False):
        # basis embedding
        qml.BasisEmbedding(inputs, wires=self.wires)
        
        # random ansatz
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
        outputs = self.qnode(inputs, sample=sample)        
        if self.verb: print('outputs:', outputs.shape, outputs)

        return outputs
    
    # draw
    def draw(self, inputs=None):
        drawer = qml.draw(self.qnode, expansion_strategy='device')
        if inputs is None:
            inputs = np.zeros(len(args.wires))
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
        
    # load model (not for self but cls)
    @classmethod
    def load(cls, fname='model.pkl', path=None, verb=False):
        if path != None:
            fname = os.path.join(path, fname)
        if verb: print('loading model:', fname)
        with open(fname, 'rb') as file:
            model = pickle.load(file)
        return model
                
# model
def get_model(args, verb=False):
    model = Qusic(layer=args.layer, wires=args.wires, 
                  dev=args.dev, ansatz=args.ansatz, 
                  qseed=args.qseed, shots=args.shots, 
                  verb=verb)
    if verb: print(model)
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
    outputs = model(inputs, sample=True)
    print(outputs)
    
    # draw model/spec
    model.draw(inputs)

    # save model
    model.save()
    # load model from scratch
    model = Qusic.load()
    # re-draw
    model.draw(inputs)
    
