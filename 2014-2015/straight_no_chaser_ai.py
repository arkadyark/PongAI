# TODO
# Graphic debugging
# - Where the ball is headed
# - Trace of the full trajectory
# - Where we project the ball to be headed
# - Projected velocity/real velocity

import math

turn_number = 1
MAX_ANGLE = 45  # Dangerous, he might change it
PADDLE_BOUNCE = 1.2  # Ditto
opponent_vel_history = 20  # Number of moves to average opponent velocity over
opponent_target_history = 20  # Number of trajectories to average opponent target over
history_weights = [1 / i for i in range(1, 21)]


def move_getter(paddle_frect, other_paddle_frect, ball_frect, table_size):
    """
    return "up" or "down", depending on which way the paddle should go to
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
0             x
     |------------->
     |
     |             
     |
 y   v
    """

    global turn_number

    # Initialize stuff on the first turn
    if turn_number == 1:
        initialize(paddle_frect, other_paddle_frect, table_size)
    turn_number += 1
    # Update the ball/opponent velocity
    if move_getter.previous_ball_pos is not None:
        move_getter.ball_vel = get_vel(move_getter.previous_ball_pos, ball_frect.pos)
        move_getter.opponent_vel = other_paddle_frect.pos[1] - move_getter.previous_opponent_pos
    move_getter.previous_ball_pos = ball_frect.pos
    move_getter.previous_opponent_pos = other_paddle_frect.pos[1]
    if len(move_getter.previous_opponent_vel) >= opponent_vel_history:
        move_getter.previous_opponent_vel.pop(0)
    move_getter.previous_opponent_vel.append(move_getter.opponent_vel)
    move_getter.opponent_vel = sum(move_getter.previous_opponent_vel) / float(len(move_getter.previous_opponent_vel))
    # Update the direction the ball is moving
    moving_left = move_getter.ball_vel[0] < 0
    moving_away = moving_left != move_getter.is_left_paddle
    # Update the edge of the paddle that the ball is moving towards
    if moving_left:
        paddle_edge = other_paddle_frect.pos[0] + paddle_frect.size[0]
        other_paddle_edge = paddle_frect.pos[0]
    else:
        paddle_edge = paddle_frect.pos[0]
        other_paddle_edge = other_paddle_frect.pos[0] + paddle_frect.size[0]

    # Ball is coming to me
    if not moving_away:
        trajectory = get_ball_trajectory(move_getter.ball_vel, ball_frect.pos, paddle_edge, table_size[1])
        estimated_ball_pos = trajectory['position'] + ball_frect.size[1] / 2
        # Check if the ball is out of reach
        if out_of_reach(paddle_frect, trajectory, True):
            # Out of reach, don't bother
            if not turn_number % 10:
                print "I can't reach the ball, moving to centre"
            move_getter.target_y = table_size[1] * 0.5
        else:
            if not turn_number % 1:
                print "The ball is actually coming to:", estimated_ball_pos, "in", trajectory["time"]
                # Get possible places I can hit that ball at
        possible_collision_positions = get_possible_positions(trajectory, paddle_frect)
        # Optimize over these possible positions
        paddle_target_position = get_optimal_target(possible_collision_positions, estimated_ball_pos, paddle_frect,
                                                    other_paddle_frect, move_getter.ball_vel, ball_frect, paddle_edge,
                                                    other_paddle_edge)
        move_getter.target_y = estimated_ball_pos

    # Ball is going at opponent
    else:
        trajectory = get_ball_trajectory(move_getter.ball_vel, ball_frect.pos, paddle_edge, table_size[1], 0)
        if not turn_number % 1:
            print "The ball is actually coming to:", trajectory['position'], "in", trajectory["time"]
        # Check if reachable
        if out_of_reach(other_paddle_frect, trajectory, False):
            # Move to middle if point is over
            if not turn_number % 10:
                print "The opponent can't reach the ball, moving to centre"
            paddle_target_position = paddle_frect.pos[1] + paddle_frect.size[1] / 2
            move_getter.target_y = table_size[1] / 2
        else:
            # Assuming opponent continues their trajectory
            collision_opponent_y = other_paddle_frect.pos[1] + move_getter.opponent_vel * trajectory['time']
            collision_opponent_y = max(0, min(collision_opponent_y, table_size[1]))
            # Get the projected rebound velocity
            projected_vel = get_projected_vel(collision_opponent_y, other_paddle_frect, trajectory['position'],
                                              ball_frect)
            # Get the projected trajectory of the return of the ball
            return_trajectory = get_ball_trajectory(projected_vel, (paddle_edge, trajectory['position']),
                                                    other_paddle_edge, table_size[1])
            # TODO - put this in a function
            # Weighted average of opponent trajectory
            if len(move_getter.previous_opponent_target) >= opponent_target_history:
                move_getter.previous_opponent_target.pop(0)
            move_getter.previous_opponent_target.append(return_trajectory['position'])
            # Gets where the return will go on our side
            return_position = most_likely_return_position()

            if not turn_number % 10:
                print "I think the opponent will hit it to:", return_position
            paddle_target_position = paddle_frect.pos[1] + paddle_frect.size[1] / 2
            move_getter.target_y = return_position

    # Computes the direction we should as a simple function of targets
    if paddle_target_position < move_getter.target_y:
        return "down"
    else:
        return "up"


def get_projected_vel(collision_y, paddle_frect, trajectory_position, ball_frect):
    """
    Return the projected velocity (as a 2-tuple) of the ball after colliding with the paddle
    """
    projected_theta = get_angle(collision_y, paddle_frect.size[1], trajectory_position + 0.5 * ball_frect.size[1],
                                not move_getter.is_left_paddle)
    projected_vel = [math.cos(projected_theta) * move_getter.ball_vel[0] - \
                     math.sin(projected_theta) * move_getter.ball_vel[1],
                     math.sin(projected_theta) * move_getter.ball_vel[0] + \
                     math.cos(projected_theta) * move_getter.ball_vel[1]]
    projected_vel[0] = -projected_vel[0]
    projected_vel = [math.cos(-projected_theta) * projected_vel[0] - \
                     math.sin(-projected_theta) * projected_vel[0],
                     math.sin(-projected_theta) * projected_vel[0] + \
                     math.cos(-projected_theta) * projected_vel[1]]
    if abs(projected_vel[0]) < 1:
        projected_vel[0] = 0.95 * (2 * (not move_getter.is_left_paddle - 1))
    projected_vel = (projected_vel[0] * PADDLE_BOUNCE, projected_vel[1] * PADDLE_BOUNCE)
    return projected_vel


def out_of_reach(paddle_frect, trajectory, me):
    '''
    Return whether or not the paddle can potentially reach the ball on its trajectory
    '''
    distance_to_ball = abs(paddle_frect.pos[1] + paddle_frect.size[1] * 0.5 - trajectory['position'])
    if me:
        return (distance_to_ball - trajectory['time']) > paddle_frect.size[1] * 0.5 + 45 * trajectory['walls'] + 8
    else:
        return (distance_to_ball - trajectory['time']) > paddle_frect.size[1] * 0.5 + 20 * trajectory['walls'] + 8


def get_vel(previous_pos, current_pos):
    """
    Return the change in position of the ball per tick as a 2-tuple.

    previous_pos - x, y tuple
    current_pos - x, y tuple
    """
    return (current_pos[0] - previous_pos[0],
            current_pos[1] - previous_pos[1])


def get_angle(paddle_y, paddle_height, ball_y, is_left_paddle):
    '''
    Given the position of the paddle and the ball, gets the angle that
    the ball will rebound off of the paddle at.
    Copied from Guerzhoy
    '''
    center = paddle_y + paddle_height / 2  # centre of paddle with respect to y
    rel_dist_from_c = ((ball_y - center) / paddle_height)  # distance from ball to centre
    rel_dist_from_c = min(0.5, rel_dist_from_c)
    rel_dist_from_c = max(-0.5, rel_dist_from_c)
    sign = 1 - 2 * is_left_paddle

    return sign * rel_dist_from_c * MAX_ANGLE * math.pi / 180


def get_ball_trajectory(ball_vel, ball_pos, paddle_edge, table_height, time=0, walls=0):
    """
    Return the y coordinate that the ball will hit when it reaches the edge
    that it's moving towards
    """
    # THIS IS A PROBLEM
    # TODO - fix
    time_to_edge = math.ceil((paddle_edge - ball_pos[0]) / ball_vel[0])
    time_to_top = -ball_pos[1] / ball_vel[1]
    time_to_bottom = (table_height - ball_pos[1]) / ball_vel[1]
    time_to_wall = math.ceil(max(time_to_top, time_to_bottom))
    if (time_to_wall < time_to_edge):
        # Headed for a wall
        projected_ball_vel = (ball_vel[0], -ball_vel[1])
        if time_to_top > time_to_bottom:
            projected_ball_pos = (ball_pos[0] + time_to_top * ball_vel[0], 0)
        else:
            projected_ball_pos = (ball_pos[0] + time_to_bottom * ball_vel[0], table_height)
        return get_ball_trajectory(projected_ball_vel, projected_ball_pos, \
                                   paddle_edge, table_height, time + time_to_wall, walls + 1)
    else:
        # Headed for a paddle (or edge)
        projected_y = ball_pos[1] + time_to_edge * ball_vel[1]
        return {'position': projected_y, 'time': time_to_edge + time, 'walls': walls}


def get_possible_positions(trajectory, paddle_frect):
    '''
    Return the possible y positions along the paddle that could potentially hit the ball
    '''
    possibilities = []
    if trajectory['position'] < paddle_frect.pos[1]:
        # ball going above paddle
        for i in range(paddle_frect.size[1]):
            if paddle_frect.pos[1] + i - trajectory['position'] < trajectory['time']:
                possibilities.append(i)
    else:
        for i in range(paddle_frect.size[1]):
            if trajectory['position'] - (paddle_frect.pos[1] + i) < trajectory['time']:
                possibilities.append(i)
    return possibilities


def get_optimal_target(possible_collision_positions, trajectory_position, paddle_frect, other_paddle_frect, ball_vel,
                       ball_frect, paddle_edge, other_paddle_edge):
    """
    Return the best point along the paddle with which to hit the ball
    """
    best_position = paddle_frect.size[1] / 2
    best_score = 0
    for possibility in possible_collision_positions:
        projected_vel = get_projected_vel(possibility, paddle_frect, trajectory_position, ball_frect)
        predicted_trajectory = get_ball_trajectory(projected_vel, (paddle_edge, trajectory_position), other_paddle_edge,
                                                   table_height)
        score = abs(predicted_trajectory['position'] - (other_paddle_frect.pos[1] + other_paddle_frect.size[1] / 2)) - \
                predicted_trajectory['time']
        if score > best_score:
            best_position = possibility
            best_score = score
    return paddle_frect.pos[1] + best_position


def most_likely_return_position():
    """
    Returns where the ball is most likely to be returned to
    Currently returns the average position of the opponent's return hits weighted by the number of turns since then.
    """
    return (sum(i * j for i, j in zip(move_getter.previous_opponent_target, history_weights)) /
            sum(history_weights[:len(move_getter.previous_opponent_target)]))  # normalize sum to 1.


def initialize(paddle_frect, their_paddle_frect, table_size):
    """
    Initialize the game set up by doing the following:
    - Initialize the size of the table
    - determine whether we are on the left or right and assign this to move_getter.is_left_paddle
    - assign the variables "my_edge" and "their_edge" to be the x coordinates of the edges.
    """

    global table_width, table_height
    table_width = table_size[0]
    table_height = table_size[1]
    move_getter.is_left_paddle = paddle_frect.pos[0] < table_width / 2
    if move_getter.is_left_paddle:
        move_getter.my_edge = paddle_frect.size[0]
        move_getter.their_edge = their_paddle_frect.pos[0]
    else:
        move_getter.my_edge = paddle_frect.pos[0]
        move_getter.their_edge = their_paddle_frect.size[0]


move_getter.previous_ball_pos = None
move_getter.ball_vel = [1, 1]
move_getter.opponent_vel = 0
move_getter.previous_opponent_vel = [0]
move_getter.previous_opponent_target = [0]
move_getter.moving_away = None
