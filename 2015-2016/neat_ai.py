# Made by Arkady Arkhangorodsky and Kasra Koushan

from neat import nn
import pickle

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
    output = net.serial_activate(inputs)
    print output[0]
    if output < 0.4:
        return "down"
    elif output < 0.6:
        return "none"
    else:
        return "up"

def initialize():
    with open('nn_winner_genome', 'rb') as f:
        genome = pickle.load(f)

    return nn.create_feed_forward_phenotype(genome)
