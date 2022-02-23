# q~~m~~usic: Quantum Music

This project is to use a **variational quantum circuit (VQC)** for music playing, inspired by a logo of [QHack 2022](https://github.com/XanaduAI/QHack).

![qusic](./images/music-gcf30a667d_1920.png)

## Chord Ansatz

A user may give a **melody**, while we wish a VQC would generate a matched **harmony**. 
One simplest possibility is the use of specific **chords** depending on **notes** of the melody.

Let's consider 7-qubit quantum processor, where each qubit is associated with a piano string of C, D, E, F, G, A, and B notes at an octave 4.
Given a melody note, the quantum measurement may produce a chord; e.g., C-major chord given C-note melody.
Such chord ansatz may be realized by controlled-nots (**CNOTs**) like the figure below.

![chord](./images/chord.png)

Given limited number of qubits, some may need to compromise with *'wrapped'* chords.
More qubits may be able to realize more variations (more octaves and flat/sharp strings).
Note that each chord ansatz will interfere each other, and thus we need more tricks.
You may see the interference when running [chord.py](./chord.py) with more chord ansatz.


## QAOA Ansatz

The above CNOTs chord ansatz has no variational parameters, and less interesting. 
Can we make a cost Hamiltonian to realize chords, and then use [quantum approximate optimization algorithm (QAOA)](https://arxiv.org/abs/1411.4028)?
TDB...

## Prerequiste

We may use the package manager [pip](https://pip.pypa.io/en/stable/) for python=3.9.
We use [Pennylane](https://pennylane.ai/).
```bash
pip install pennylane=0.21.0
pip install pygame=2.1.2
pip install argparse
```
Other versions should work.


## Sound Synthesize

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

Under development.

## Usage

```bash
??
```

# q~~g~~uitar: Quantum Guitar

![quitar](./images/electric-guitar-g8af22bc71_1920.jpg)
<!--
![quitar](./images/guitar-g9261592a2_1920.jpg)
-->

Under development.

# License

[MIT](https://choosealicense.com/licenses/mit/).
Copyright (c) 2022 Toshi Koike-Akino.
This project is provided 'as-is', without warranty of any kind. In no event shall the authors be liable for any claims, damages, or other such variants.
