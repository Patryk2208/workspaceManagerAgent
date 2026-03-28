## Currently active project (unfinished), todo some decision on model training

### tool architecture
An idea to implement an AI tool to manage the Sway's (Linux window manager) windows in real time, according to what's being done, user preferences, just adapting to the current setup. 
The implementation is as follows, an "actor" program, a daemon, written in Go, that acts as a server and enforces the changes made by the model, model can request the state of the desktop to be changed accordingly to the preferred setup.
Then the "model" so a Pyhton model implementation, written in pyTorch, basically a program that runs a loop, where it collects a state from the actor, pushes it to the model, the model does the inference step and then the request to the actor is made
to reflect those changes. A basic rest, with some validation. The tools is quite complete.

### model architecture
The problem the model is to solve is how to learn the optimal layout of the windows on the screen, now this is not an ideal scenario for standard ml approaches. 
The input is basically screen layout, grid+types of windows+some metadata, on that the model has to infer an optimal layout. My idea was to use 2 main steps:
1. Generating some "good" initial layouts programmatically, so that the network can learn the basic correct approaches, this can be done quite easily, just inputting the general ideas behind optimization to the model, this is the current step, some "expert" dataset can be created for more complex scenarios too, but currently im implelmenting an alg to create those "good" layouts.
2. After we have a somewhat good network, we can go into the main training part, we wanna use Reinforcement Learning, i am kinda waiting with this step once we have a course on RL at uni, or a can learn the implemneteation logic, but from the conceptual standpoint, what we want is to give "bad" signals to the model upon doing sth "wrong", now that "wrong" is basically gonna be a moment, where a user has to correc the model, so conceptually it seems nice, but i have no idea yet as to the extent of the dataset size needed to make such program work well.

Currently as i mentioned the project stands on that good_layout_generation as i called it, the current step is to implement that alg, then an alg to scramble this good layout and feed a model such a pair of a before-after state, so it can learn the basics.
