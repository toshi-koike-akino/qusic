# q~~m~~usic: Quantum Music

This project is to use a **variational quantum circuit (VQC)** for music playing, inspired by a logo of [QHack 2022](https://github.com/XanaduAI/QHack).

![qusic](./images/qusic.png)
<!--
![qusic](./images/music-gcf30a667d_1920.png)
-->


## Chord Ansatz

A user may give a **melody**, while we wish a VQC would generate a matched **harmony**. 
One simplest possibility is the use of specific **chords** depending on **notes** of the melody.

Let's consider 7-qubit quantum processor, where each qubit is associated with a piano string of C, D, E, F, G, A, and B notes at an octave 4.
Given a melody note, the quantum measurement may produce a chord; e.g., *C-major* chord given *C-note* melody.
Such chord ansatz may be realized by controlled-nots (**CNOTs**) like the figure below.

![chord](./images/chord.png)

Given limited number of qubits, some may need to compromise with *'wrapped'* chords.
More qubits may be able to realize more variations (more octaves and flat/sharp strings).

Nevertheless, it should be noted that each chord ansatz will interfere each other, and thus we need more tricks.
You may see the interference when running [chord.py](./chord.py) with more chord ansatz.
```bash
python chord.py
C [1 1 1 1 0 0 1] # C-D-E-F-B ... anti-harmony
D [1 1 0 1 0 0 0] 
E [0 1 1 0 1 0 0]
F [0 0 1 1 0 1 0]
G [0 0 0 1 1 0 1]
A [1 0 1 0 0 1 0] # Am ... OK
B [0 1 0 1 0 0 1] # Bdm ... OK
```
Only exclusive chords in the end like a pair of Am and Bdm would work together.
For example, we may pick exclusive chord ansatzs like:
```bash
python chord.py --chords CM Dm
C [1 0 1 0 1 0 0] # CM ... OK
D [0 1 0 1 0 1 0] # Dm ... OK
E [0 0 1 0 0 0 0] # no harmony ... just melody of E-note.
```


## VQC Ansatz

The above CNOTs chord ansatz has no variational parameters, and less interesting. 
<!--
Can we make a cost Hamiltonian to realize chords, and then use [quantum approximate optimization algorithm (QAOA)](https://arxiv.org/abs/1411.4028)?
-->
In this project, we wish to design VQC to raise a *quantum pianist* or a *quantum guitarist* (hopefully with a passion to deviate from regular behaviors depending on his mood: i.e., quantum states/errors). 
Let's solve it with **quantum machine learning (QML)** framework.

## Prerequisite

We may use the package manager [pip](https://pip.pypa.io/en/stable/) for python=3.9.
We use [Pennylane](https://pennylane.ai/).
```bash
pip install pennylane=0.21.0
pip install pygame=2.1.2
pip install argparse
pip install dill=0.3.4
pip install tqdm=4.62.3
pip install matplotlib=3.5.1
```
Other versions should work.


## Sound Synthesis

We first synthesize sounds, based on a submodule [Synthesizer_in_Python](https://github.com/joaocarvalhoopen/Synthesizer_in_Python).
A wrapper script [synth.py](synth.py) to generate wav files in Sounds directory, e.g., as
```bash
python synth.py --octaves 4 --notes C D E F G A B --sound piano acoustic
```
We may hear a piano note like [C4.wav](./audios/C4.wav).

Sound checking with [twinkle.py](twinkle.py) as:
```bash
python twinkle.py --duration 0.1
```
You should hear *twinkle star*, otherwise revisit above.

# q~~p~~iano: Quantum Piano

![qiano](./images/piano-g43a982641_1920.jpg)
<!--
![qiano](./images/piano-g1093989be_1920.jpg)
![qiano](./images/piano-g43b83d891_1280.jpg)
-->


## q~~m~~usician: Quantum Musician Ansatz

Let's invite three of our *qusicians*, who prefers a particular ansatzs:
- *qusician*-Alice: [BasicEntanglerLayers](https://pennylane.readthedocs.io/en/stable/code/api/pennylane.BasicEntanglerLayers.html)
- *qusician*-Bob: [StronglyEntanglingLayers](https://pennylane.readthedocs.io/en/stable/code/api/pennylane.StronglyEntanglingLayers.html)
- *qusician*-Charlie: [RandomLayers](https://pennylane.readthedocs.io/en/stable/code/api/pennylane.RandomLayers.html)

A *qusician* plays the piano based on a melody line, by embedding with [BasisEmbedding](https://pennylane.readthedocs.io/en/stable/code/api/pennylane.BasisEmbedding.html).
Our qusician-Charlie may look like below:
```python
wires = ['C', 'D', 'E', 'F', 'G', 'A', 'B'] # 1-octave strings
skill = np.random.randn(layer, 7, requires_grad=True) # skill weights

@qml.device(device, wires=wires, shots=1)
def qusician(melody):
    # melody line given; 'C'-note for [1,0,0,0,0,0,0]
    qml.BasisEmbedding(features=melody, wires=wires)
    # think better harmony
    qml.RandomLayers(weights=skill, wires=wires)
    # type keyboard
    return qml.sample(wires=wires) # hope 'CM' chord [1,0,1,0,1,0,0] for 'C'-note melody
```

The *qusician* python class is introduced in [qusic.py](./qusic.py).
Our *qusician*-Charlie would visit us by calling as:
```python
python qusic.py --ansatz RandomLayers --layers 2 7
```

Note that, without teaching them, they are just novice-level players because the variational parameters are random at beginning. 
Also note that the tarent depends on how he/she thinks (i.e., quantum ansatz) and how deep he/she thinks (i.e., the number of quantum layers).
Let's introduce our q~~m~~aestro who may instruct them to play the piano.

## q~~m~~aestro: Quantum Maestro Teacher

Our *qaestro* teacher is introduced in [qaestro.py](./qaestro.py). 
He may use a particular teaching style, like [AdamOptimizer](https://pennylane.readthedocs.io/en/stable/code/api/pennylane.AdamOptimizer.html).
He tries to minimize students' *mis-fingering* (as a cost), where he asked how likely the students want to type keyboards given melody note, and judges a penalty based on binary cross-entropy (BCE) loss, like below.
```python
qaestro = qml.AdamOptimizer() # different teaching style is available

def mis_finger(weights):
    melogy = np.random.choice(wires) # melody note given
    typing = qusician(melody) # qusician answers melody typing
    harmony = chords[melody] # target harmony
    penalty = BCE(typing, harmony) # how much close to the target
    return penalty
weights = qaestro.step(mis_finger, weights) # qaestro's guide
```

## Teaching Perforamnce

### q~~m~~usician-Alice (BasicEntanglerLayers):

Let's see how *qusician*-Alice would be trained by our qaestro:
```bash
python qaestro.py --ansatz BasicEntanglerLayers --layers 2 7 --epoch 2000 --showfig
```
Her skill is improved with large deviation as below.
![basic2](./plots_demo/BasicEntanglerLayers_2_7.png)

After training, she looks like below:
```python
>> model.draw()
 C: ──RX(-6.88e-06)──╭C────────────────────────────────────────────────────────────────────────╭X──RX(-0.000264)──╭C──────────────────────╭X──┤ ⟨Z⟩ 
 D: ──RX(1.09e-05)───╰X──╭C───RX(2.09e-05)─────────────────────────────────────────────────────│──────────────────╰X──╭C──────────────────│───┤ ⟨Z⟩ 
 E: ──RX(-1.56)──────────╰X──╭C──────────────RX(-0.853)────────────────────────────────────────│──────────────────────╰X──╭C──────────────│───┤ ⟨Z⟩ 
 F: ──RX(-1.3)───────────────╰X─────────────╭C────────────RX(1.66)─────────────────────────────│──────────────────────────╰X──╭C──────────│───┤ ⟨Z⟩ 
 G: ──RX(1.36)──────────────────────────────╰X───────────╭C──────────RX(-2.37)─────────────────│──────────────────────────────╰X──╭C──────│───┤ ⟨Z⟩ 
 A: ──RX(-2.15)──────────────────────────────────────────╰X─────────╭C──────────RX(-0.000427)──│──────────────────────────────────╰X──╭C──│───┤ ⟨Z⟩ 
 B: ──RX(8.41e-05)──────────────────────────────────────────────────╰X─────────────────────────╰C──RX(-0.00425)───────────────────────╰X──╰C──┤ ⟨Z⟩ 
 ```

Unfortunately, even with more deep thinking (32-layer ansatz), her skill seems not that great:
```bash
python qaestro.py --ansatz BasicEntanglerLayers --layers 32 7 --epoch 2000 --showfig
```
![basic32](./plots_demo/BasicEntanglerLayers_32_7.png)

### q~~m~~usician-Bob (StronglyEntanglingLayers):

Let's check how our *quasician*-Bob would do:
```bash
python qaestro.py --ansatz StronglyEntanglingLayers --layers 2 7 --epoch 2000 --showfig
```
![strong2](./plots_demo/StronglyEntanglingLayers_2_7.png)

It seems that his skill is comparable to *qusician*-Alice.
However, he seems more serious in the piano training if he uses deeper insights with 32-layer ansatz:
```bash
python qaestro.py --ansatz StronglyEntanglingLayers --layers 32 7 --epoch 2000 --showfig
```
![strong32](./plots_demo/StronglyEntanglingLayers_32_7.png)

His playing looks more stable with less scolding by *qaestro*.
Note that [StronglyEntanglingLayers](https://pennylane.readthedocs.io/en/stable/code/api/pennylane.StronglyEntanglingLayers.html) have three-fold more variational parameters per layer than [BasicEntanglerLayers](https://pennylane.readthedocs.io/en/stable/code/api/pennylane.BasicEntanglerLayers.html).


## q~~m~~usician-Charlie (RandomLayers):

How skillful is our *qusician*-Charlie?
```bash
python qaestro.py --ansatz RandomLayers --layers 2 7 --epoch 2000 --showfig
```
![rand2](./plots_demo/RandomLayers_2_7.png)

His playing seems awful and receives a lot of penalty by *qaestro*.
However, we found that he would be more serious in the piano training if he considers deeper insights with 32-layer ansatz:
```bash
python qaestro.py --ansatz RandomLayers --layers 32 7 --epoch 2000 --showfig
```
![rand32](./plots_demo/RandomLayers_32_7.png)

Then, he may be more skillful than *qusician*-Alice, while the number of variational parameters is equivalent.

<!--
After training, he looks like below:
```python
>> model.draw()
 C: ──╭C───────────────RZ(-0.528)──RY(0.252)──RY(1.33)─────────────────────────────────────────────────────────────────────────────╭C───────────────────────╭C───────────╭X──RZ(0.293)─────RY(0.00413)──╭C──────────────────────────────────────────────╭X───RX(0.00563)───RY(-1.59)──────────────╭X──RY(0.503)───RY(0.817)─────────────────────────────────────────╭X──────────────╭C───────────────────────────────────────────────╭X───RY(-0.207)─────────────╭C──RX(1.07)────RX(0.5)─────RZ(-0.174)───────────RY(-0.133)──RZ(0.169)─────────────────────────────────────────────────────┤ ⟨Z⟩ 
 D: ──╰X───────────────RY(-1.58)───RZ(-3.13)─────────────╭X──RZ(0.591)──────────────╭X─────────────╭X─────────────╭C──RY(0.00162)──╰X───────────────────────│────────────╰C──RZ(-0.0107)───RX(-1.64)────│───────────────────────────────────────────────│───╭X─────────────RY(1.2)────RZ(1.12)────│───RY(0.742)──────────────────╭C─────────────────╭C──RY(0.681)───│───────────────│─────────────╭C──────────────────╭C──RY(-1.23)──│───╭X───────────RX(-1.21)──│───RY(0.727)───RZ(1.01)────────────────────╭X───RZ(0.151)───RY(0.0354)────RX(-0.675)─────RY(1.86)───RX(-1.19)──RY(0.649)──┤ ⟨Z⟩ 
 E: ───────────────╭X──RY(1.32)────RY(2.2)────RY(-0.31)──│───RY(0.77)────RZ(-1.51)──│───RZ(0.731)──│──────────────│─────────────────────────────────────────│────────────╭C──RZ(-0.681)───╭C────────────│──────────────────╭X──RX(1.56)─────RZ(-0.329)──│───╰C────────────╭X──────────────────────│──────────────────────────╭C──│───RX(0.775)──────│───RZ(0.4)─────│───RX(0.812)───│───RZ(1.23)──│───────────────╭X──│───RX(0.681)──│───│───────────────────────╰X──RY(0.497)───RY(-0.532)──────────────╭C──│────RZ(0.626)───RY(1.07)──────RZ(1.53)───────RX(-2.07)────────────────────────┤ ⟨Z⟩ 
 F: ───RX(1.56)────│───RZ(-1.59)─────────────────────────╰C──RY(-0.183)──RY(0.181)──│───RX(-1.99)──│───RX(-2.26)──│───RZ(2.58)──────────────────────────────│────────────│────────────────│─────────────│──────────────────│────────────────────────────│─────────────────│───────────────────────╰C──RZ(0.54)───────────────│───│──────────────╭X──│───RX(-0.945)──│───RY(-1.56)───│───RX(1.04)──│───RX(2.09)────│───│──────────────│───╰C───────────RZ(0.313)──────────────────────────────────────────│───│───╭X───────────RZ(-0.0744)───RY(-0.00282)───RZ(0.594)────────────────────────┤ ⟨Z⟩ 
 G: ───────────────╰C───────────────────────────────────────────────────────────────╰C─────────────│──────────────│─────────────────────────────╭C──────────╰X───────────╰X──RX(-1.54)────│─────────────╰X─────────────╭X──│────────────────────────────│───╭X────────────╰C──────────RZ(0.0243)──────RZ(-0.448)──RX(1.52)───│───│───RY(1.15)───│───│───────────────│───────────────│─────────────│───────────────╰C──│───RY(0.773)──│────RZ(-0.192)──RX(0.379)──────RZ(-0.623)──RY(0.801)───RY(-0.213)──│───│───╰C───────────RX(-0.0304)───RZ(0.315)───────────────────────────────────────┤ ⟨Z⟩ 
 A: ───RZ(-0.249)──────RX(-2.22)───────────────────────────────────────────────────────────────────╰C──RX(0.746)──│───RY(-0.828)────RY(-1.05)───╰X───────────RX(0.0455)──╭C───────────────│────────────────────────────╰C──│───RX(0.00595)──────────────╰C──╰C─────────────RX(1.61)───RZ(0.0447)──────RX(0.503)──────────────╰X──│──────────────│───╰X──RX(1.2)─────│───RY(-0.639)──│───RX(1.75)──│───RY(-0.833)──────│───RZ(-2.41)──│────RY(0.876)──────────────────────────────────────────────────────│───╰C───RY(0.778)───────────────────────────────╭X────────────────────────────────┤ ⟨Z⟩ 
 B: ───RZ(-0.384)─────────────────────────────────────────────────────────────────────────────────────────────────╰X──RZ(0.364)─────RZ(-0.903)───RZ(-1.15)───────────────╰X──RY(0.00567)──╰X─────────────RY(-0.00778)──────╰C──RZ(-1.52)─────────────────────────────────────────────────────────────────────────────────────────╰X─────────────╰C──────────────────╰C──────────────╰X────────────╰X──────────────────╰X─────────────╰C──────────────────────────────────────────────────────────────────╰X───────RY(0.743)───RX(-0.00879)──RZ(-0.00567)──╰C──────────RY(1.6)───────────────┤ ⟨Z⟩ 
```
-->

## q~~c~~oncert: Quantum Concert

Let's listen to how our *qusician* Alice, Bob, and Charlie would play the piano.
... Coming soon.


# q~~g~~uitar: Quantum Guitar

![quitar](./images/electric-guitar-g8af22bc71_1920.jpg)
<!--
![quitar](./images/guitar-g9261592a2_1920.jpg)
-->

Under development.

# Extensions

Our *quantum musician* may consider if he feels good:
- Volume
- Tempo 
- Arpeggio/Stroke
- Trend of melody
- ...

# License

[MIT](https://choosealicense.com/licenses/mit/).
Copyright (c) 2022 Toshi Koike-Akino.
This project is provided 'as-is', without warranty of any kind. In no event shall the authors be liable for any claims, damages, or other such variants.
