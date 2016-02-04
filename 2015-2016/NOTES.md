2/3/16
- Tried out some training with a few different config sets
- fs_neat seems to be a very bad initial_connection scheme for us, since we already have the features we want and know we want it to be connected. It seems like it isn't adding enough connections and gets stuck with only one of them doing shit. gonna try fully connected to fix this.
- Added some little bonus for hitting the ball. Not sure what the weight for that should be.

2/4/16
- Fixed a dumb bug that prevented us from being able to see how well it was doing
- Played with config parameters (tanh activation function, hidden nodes, probabilities, weight bounds)
- Trained pop. 30 for 30 generations, had a decent AI! Was beating chaser, and human sometimes
