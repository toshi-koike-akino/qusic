# (c) Toshiaki Koike-Akino, 2022
# quantum maestro (qaestro) teaching for quantum musician (qusician); VQC circuits

import pennylane as qml
import pennylane.numpy as np
import argparse
import qusic
import chord
from tqdm import tqdm
import os

# args
def get_args():
    parser = argparse.ArgumentParser(__file__)
    # general args
    parser.add_argument('--verb', action='store_true', help='verbose')
    parser.add_argument('--seed', default=1, type=int, help='seed for main')

    # add args
    add_args(parser)
    
    return parser.parse_args()

# add args to inherit
def add_args(parser):
    # inherit qusic args
    qusic.qusic_args(parser)
    
    # qaestro args
    qaestro_args(parser)

    # defaults
    #parser.set_defaults(ansatz='StronglyEntanglingLayers')
    parser.set_defaults(ansatz='RandomLayers')
    parser.set_defaults(layers=[2, 7])
    parser.set_defaults(wires=['C', 'D', 'E', 'F', 'G', 'A', 'B']) # single octave (w/o sharp)
    parser.add_argument('--chords', default=['CM', 'Dm', 'Em', 'FM', 'GM', 'Am', 'Bdm'], type=str,
                        help='chords to learn')
    
# quantum maestro teacher args (optimizer args)
def qaestro_args(parser):
    parser = parser.add_argument_group('qaestro')
    parser.add_argument('--opt', default='AdamOptimizer', 
                        choices=['AdamOptimizer', 'AdagradOptimizer', 'GradientDescentOptimizer', 
                                 'MomentumOptimizer', 'NesterovMomentumOptimizer', 'RMSPropOptimizer', 'QNGOptimizer', 
                                 #'ShotAdaptiveOptimizer', 'LieAlgebraOptimizer', 'RotosolveOptimizer', 'RotoselectOptimizer',
                                 ],
                        help='optimizer. (some are not tested)')
    parser.add_argument('--lr', default=0.01, type=float, help='learning rate (stepsize)')
    parser.add_argument('--epoch', default=300, type=int, help='number of epochs')

# optimizer selction
def get_opt(args):
    opt = getattr(qml, args.opt)(stepsize=args.lr)
    return opt

# maestro teaching for a qusician student model
def teach(args, student):
    # teacher
    teacher = get_opt(args)
    if args.verb: print('teacher:', teacher)
    
    # chords to learn
    chords = chord.get_chords(chords=args.chords)
    chords.append(['-']) # break
    if args.verb: print('chords to learn:', args.chords, chords)
    
    #
    wires = args.wires.copy()
    wires.append('-') # break
    print(args.wires)
    
    # cost to reduce miss-fingering
    def miss_finger(weights, **kwargs):
        # melody-line note given
        #note = np.random.choice(len(wires), size=2)[-1] # random choice of melody note (size=None, 1 not working?)
        melody = wires[note] # melody line note
        if args.verb: print('melody', note, melody)
        
        # harmony to learn
        harmony = chords[note] # chord notes
        if args.verb: print('harmony', harmony)        
        
        # teach playing
        inputs = student.notes2basis(melody) # notes to basis
        targets = student.notes2basis(harmony) # notes to basis        
        
        # skill set
        student.set_weights(weights)

        # student plays
        outputs = student(inputs, sample=False) 
        if args.verb: print('inputs/targets/outputs', inputs, targets, outputs)
        
        # binary cross entropy loss
        outputs = 0.5 * (outputs + 1) # (1,-1) to (0,1) prob domain
        eps = 1e-8
        loss = -targets * np.log(1.0 - outputs + eps) - (1 - targets) * np.log(outputs + eps)
        loss = loss.mean()
        
        return loss
    
    # train loop
    weights = student.weights
    loss_all = list()
    train = np.random.choice(len(wires), size=args.epoch) # random choice of melody note to train

    for epoch in tqdm(range(args.epoch), leave=True, desc='teaching'):
        note = train[epoch]
        weights, loss = teacher.step_and_cost(miss_finger, weights, note=note)
        #student.set_weights(weights)

        print(epoch, loss) #, weights, student.weights)
        loss_all.append(loss)
    
    # update weights
    student.set_weights(weights)
    #student.save()
    
    return student, loss_all
        
# plot
def plot(loss, title='plot', path='plots'):
    import matplotlib.pyplot as plt
    plt.plot(loss)
    plt.grid()
    plt.xlabel('Teaching Epoch')
    plt.ylabel('BCE Loss')   
    plt.title(title)

    # save
    fname = f'{title}.png'
    if path != None:
        os.makedirs(path, exist_ok=True)
        fname = os.path.join(path, fname)        
    plt.savefig(fname)
    plt.show()

def save(model, fname):
    #model.save(fname=fname, path='models') # not working :(
    model.save_weights()
    model = qusic.get_model(args, verb=args.verb) # re-instantiate, avoiding pickling error
    model.load_weights()
    model.save(fname=fname, path='models')
    model.draw()

    return model # new instance with copied weights

# main
def main(args):
    if args.verb: print('# args:', args)

    # random seed
    qusic.seeding(args.seed, verb=args.verb)
        
    # qusic player
    model = qusic.get_model(args, verb=args.verb)
    model.draw()
    #model.save()
    
    # teach qusic player
    model, loss = teach(args, model)
    model.draw()
    
    # save
    title = '_'.join(map(str, args.layers))
    fname = f'{args.ansatz}_{title}.pkl'
    model = save(model, fname)
    
    # plot loss   
    fname = f'{args.ansatz}_{title}'
    plot(loss, title=fname, path='plots')
    
    return model

# main
if __name__ == '__main__':
    args = get_args()
    
    model = main(args)

    