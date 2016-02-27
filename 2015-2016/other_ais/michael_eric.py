# ------------------- IMPORTANT ------------------- #
# This code must be run in python 2.7, not Python 3 #
# ------------------------------------------------- #

from __future__ import division  # Make it more Python 3 like: float division.
import math
from collections import deque

global paddle_positions_ai, other_paddle_positions_ai, ball_positions_ai

# Removes old samples, to reduce memory usage
# Note: You can think of deques as lists for our purposes.
MAX_SAMPLES_TO_KEEP = 10
paddle_positions_ai = deque(maxlen=MAX_SAMPLES_TO_KEEP)
other_paddle_positions_ai = deque(maxlen=MAX_SAMPLES_TO_KEEP)
ball_positions_ai = deque(maxlen=MAX_SAMPLES_TO_KEEP)



def pong_ai(paddle_frect, other_paddle_frect, ball_frect, table_size):
    '''return "up" or "down", depending on which way the paddle should go to
    align its centre with the centre of the ball, assuming the ball will
    not be moving

    Arguments:
    paddle_frect: a rectangle representing the coordinates of the paddle
                  paddle_frect.pos[0], paddle_frect.pos[1] is the top-left
                  corner of the rectangle.
                  paddle_frect.size[0], paddle_frect.size[1] are the dimensions
                  of the paddle along the x and y axis, respectively

    other_paddle_frect:
                  a rectangle representing the opponent paddle. It is formatted
                  in the same way as paddle_frect
    ball_frect:   a rectangle representing the ball. It is formatted in the
                  same way as paddle_frect
    table_size:   table_size[0], table_size[1] are the dimensions of the table,
                  along the x and the y axis respectively

    The coordinates look as follows:

         x
     0 -->
     |
   y v
    '''

    # Housekeeping
    record_all_positions(paddle_frect, other_paddle_frect, ball_frect, table_size)

    # Obtains a few variables, just to demonstrate abilities
    ball_velocity = get_velocity_matrix(ball_positions_ai, 2)
    ball_speed = get_speed_from_velocity_matrix(ball_velocity)
    ball_angle = get_angle_from_velocity_matrix(ball_velocity)
    other_paddle_direction = other_paddle_movement(2)

    # Determine our paddle location
    paddle_is_left = other_paddle_frect.pos[0] > table_size[0]/2

    # Actual Mover
    location_to_go_to = vertical_correction_factor(get_bounce_point(table_size,paddle_is_left),table_size, other_paddle_frect.pos, ball_speed)

    if paddle_frect.pos[1]+paddle_frect.size[1]/2 < location_to_go_to:
        return "down"
    else:
        return "up"


def record_all_positions(paddle_frect, other_paddle_frect, ball_frect, table_size):
    ''' Updates the historical position data'''
    global paddle_positions_ai, other_paddle_positions_ai, ball_positions_ai

    # Appends new data to the global variables
    paddle_positions_ai.append(paddle_frect.pos[1])
    other_paddle_positions_ai.append(other_paddle_frect.pos[1])
    ball_positions_ai.append([ball_frect.pos[0], ball_frect.pos[1]])


def get_velocity_matrix(positions_local, n):
    ''' n  : number of positions_local to average
       pos : list of lists containing all recorded positions_local

       delta_pos[0] is x direction
       delta_pos[1] is y  direction
       '''
    delta_pos = [0,0]
    if len(positions_local) > n:
        for i in range(len(positions_local) - n, len(positions_local)):
            delta_pos[0] += positions_local[i][0] - positions_local[i-1][0]
            delta_pos[1] += positions_local[i][1] - positions_local[i-1][1]
        return [delta_pos[0]/(n-1), delta_pos[1]/(n-1)]

    else:
        return [1,1]


def get_speed_from_velocity_matrix(matrix):
    if matrix[1] == 0:
        matrix[1] = 0.1
    return math.sqrt(matrix[0]**2 + matrix[1]**2)


def get_angle_from_velocity_matrix(matrix):
    if matrix[1] == 0:
        matrix[1] = 0.1
    return math.tan(matrix[0] / matrix[1])


def get_bounce_point(table_size_local, paddle_is_left):
    ''' Return where (on the top of bottom of the field) the ball will bounce'''

    v = get_velocity_matrix(ball_positions_ai, 3)

    TABLE_HEIGHT = table_size_local[1]
    if paddle_is_left:
        PADDLE_POSITION = 25
    else:
        PADDLE_POSITION = table_size_local[0] - 25

    # Whether the ball is moving up or down (true = up, false = down)
    ball_direction = v[1] < 0

    x = ball_positions_ai[len(ball_positions_ai)-1][0]
    y = ball_positions_ai[len(ball_positions_ai)-1][1]

    # Take distance from paddle to current paddle position:
    RIGHT_PADDLE_POSITION = table_size_local[0] - 20  # Table Size, and 20 from edge
    LEFT_PADDLE_POSITION = 20

    ball_to_paddle = PADDLE_POSITION - x

    #Find total vertical displacment of ball until reaching paddle
    time_to_hit = ball_to_paddle / v[0]
    total_y_displacment = time_to_hit * v[1]


    #Find the un-bounced final position of ball
    final_y_nobounce = y + total_y_displacment

    #Find final position of ball after bouncing
    if final_y_nobounce < 0:
        # Ball bounce on top of table
        # Determine number of bounces and direction of ball after last bounce
        bounce_count = (final_y_nobounce + y) // TABLE_HEIGHT
        distance_from_wall_at_impact = (final_y_nobounce + y) % TABLE_HEIGHT
    elif final_y_nobounce > TABLE_HEIGHT:
        # Ball bounce at bottom of table
        # Determine number of bounces and direction of ball after last bounce
        bounce_count = (final_y_nobounce - y) // TABLE_HEIGHT
        distance_from_wall_at_impact = (final_y_nobounce - y) % TABLE_HEIGHT
    else:
        # Ball doesn't bounce on wall
        bounce_count = 0
        ball_y_location_at_impact = final_y_nobounce
        distance_from_wall_at_impact = False


    # Determine if x component of velocity flips from current at the predicted time of impact
    if_x_velocity_flip = bounce_count % 2 == 1


    # Find direction of ball immediately before impact
    # (true = up, false = down)
    if if_x_velocity_flip:
        ball_direction_at_impact = not ball_direction
    else:
        ball_direction_at_impact = ball_direction

    # Find X position of the ball at impact based on previous findings
    if v[0] < 0 and not paddle_is_left:
        # Ball moving to the opponent
        ball_y_location_at_impact = TABLE_HEIGHT / 2
    elif v[0] > 0 and paddle_is_left:
        ball_y_location_at_impact = TABLE_HEIGHT / 2

    else:
        if ball_direction_at_impact and distance_from_wall_at_impact:
            ball_y_location_at_impact = distance_from_wall_at_impact
        elif distance_from_wall_at_impact:
            ball_y_location_at_impact = TABLE_HEIGHT - distance_from_wall_at_impact

    return [ball_y_location_at_impact, ball_direction_at_impact, bounce_count]

    # Sort of Done


def vertical_correction_factor(data_packet_from_bp, table_size_local, other_paddle_location_matrix, ball_speed):
    y_input = data_packet_from_bp[0]
    ball_direction_at_impact = data_packet_from_bp[1]
    bounce_count = data_packet_from_bp[2]
    #Insert Attack Strat Here

    y_input = y_input
    
    if not ball_direction_at_impact and y_input != table_size_local[1]/2:
	# Ball traveling down at impact
	y_result = y_input
    elif ball_direction_at_impact and y_input != table_size_local[1]/2:
	# Ball traveling down at impact
	y_result = y_input
    elif y_input == table_size_local[1]/2:
	# Paddle to center
	y_result = y_input
    
    return y_result


def other_paddle_movement(n):
    ''' Determines whether the other paddle is moving up or down
        n : number of positions to average '''
    #v = get_velocity_matrix(other_paddle_positions_ai, n)[1]

    # TESTING #
    # TESTING #
    v = 0
    # TESTING #

    # How slow the paddle must be moving to be considered not to be moving
    zero = 1

    if(v < -zero): return -1
    if(v > -zero): return 1
    return 0

