turn_number = 1

def move_getter(paddle_frect, other_paddle_frect, ball_frect, table_size):
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

     0             x
     |------------->
     |
     |             
     |
 y   v
    '''          
    global turn_number

    if turn_number == 1:
        initialize(paddle_frect, table_size[0])
    turn_number += 1
    if move_getter.previous_ball_pos != None:
        move_getter.ball_vel = get_vel(move_getter.previous_ball_pos, ball_frect.pos)
    move_getter.previous_ball_pos = ball_frect.pos
    moving_left = move_getter.ball_vel[0] < 0
    moving_away = moving_left != move_getter.left_paddle
    if moving_left:
        paddle_edge = paddle_frect.size[0]
    else:
        paddle_edge = paddle_frect.pos[0]
    if not moving_away:
         move_getter.target_y = get_ball_trajectory(move_getter.ball_vel, ball_frect.pos, paddle_edge, table_size[1], 0)[0] + ball_frect.size[1]/2
    else:
        move_getter.target_y = table_size[1]/2
    if paddle_frect.pos[1]+paddle_frect.size[1]/2 < move_getter.target_y:
        return "down"
    else:
        return "up"

def get_vel(previous_pos, current_pos):
    return (current_pos[0] - previous_pos[0],\
            current_pos[1] - move_getter.previous_ball_pos[1])

def get_ball_trajectory(ball_vel, ball_pos, paddle_edge, table_height, time):
    '''
    Return the y coordinate that the ball will hit when it reaches the edge
    that it's moving towards
    '''
    time_to_edge = (paddle_edge - ball_pos[0])/ball_vel[0]
    time_to_top = -ball_pos[1]/ball_vel[1]
    time_to_bottom = (table_height - ball_pos[1])/ball_vel[1]
    time_to_wall = max(time_to_top, time_to_bottom)
    if (time_to_wall < time_to_edge):
        projected_ball_vel = (ball_vel[0], -ball_vel[1])
        if time_to_top > time_to_bottom:
            projected_ball_pos = (ball_pos[0] + time_to_top*ball_vel[0], 0)
        else:
            projected_ball_pos = (ball_pos[0] + time_to_bottom*ball_vel[0], table_height)
        return get_ball_trajectory(projected_ball_vel, projected_ball_pos,\
                    paddle_edge, table_height, time + time_to_wall) 
    else:
        projected_y = ball_pos[1] + time_to_edge*ball_vel[1]
        return projected_y, time_to_edge + time

def initialize(paddle_frect, table_width):
    move_getter.left_paddle = paddle_frect.pos[0] < table_width/2

move_getter.previous_ball_pos = None
move_getter.ball_vel = [0, 0]
move_getter.moving_away = None
