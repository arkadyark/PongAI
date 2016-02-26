# Made by Arkady Arkhangorodsky and Kasra Koushan

from neat import nn
import pickle, os

turn_number = 1
net = None

def pong_ai(paddle_frect, other_paddle_frect, ball_frect, table_size):
    '''
    Inputs to the neural network: x/y of both paddles, x/y of the ball, turn number
    Other game parameters leave out for now, may require more training to make
    it more robust to slightly adapted games and use those, but the above is the
    bare minimum. Needs the x coordinates of the paddles to be able to play on
    either side.
    '''

    global turn_number, net

    if turn_number == 1:
        net = initialize()

    turn_number += 1

    inputs = [
        # Ball position
        ball_frect.pos[0],
        ball_frect.pos[1],
        # Player position
        paddle_frect.pos[0],
        paddle_frect.pos[1],
        # Opponent position
        other_paddle_frect.pos[0],
        other_paddle_frect.pos[1]
        # Maybe - ball velocity, previous few opponent positions, turn number
    ]
    print inputs
    output = net.serial_activate(inputs)[0]
    print output
    if output < -0.1:
        return "down"
    elif output < 0.1:
        return "none"
    else:
        return "up"

def initialize():
    module_dir = os.path.dirname(os.path.abspath(__file__))
    textfile_path = os.path.join(module_dir, 'nn_winner_genome')
    with open(textfile_path, 'rb') as f:
        genome = pickle.load(f)

    print genome
    return nn.create_feed_forward_phenotype(genome)
