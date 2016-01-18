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
    
    if turn_number == 1:
        initialize(paddle_frect, other_paddle_frect, table_size)

    net = nn.create_feed_forward_phenotype(winner) 
    turn_number += 1
