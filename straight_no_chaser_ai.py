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

    if move_getter.previous_ball_pos != None:
	move_getter.ball_vel = get_vel(move_getter.previous_ball_pos, ball_frect.pos)
    move_getter.previous_ball_pos = ball_frect.pos
    move_getter.moving_away = move_getter.ball_vel[0] > 0

    if paddle_frect.pos[1]+paddle_frect.size[1]/2 < ball_frect.pos[1]+ball_frect.size[1]/2:
	return "down"
    else:
	return "up"

def get_vel(previous_pos, current_pos):
    return (current_pos[0] - previous_pos[0],\
	    current_pos[1] - move_getter.previous_ball_pos[1])

    move_getter.previous_ball_pos = None
move_getter.ball_vel = [0, 0]
move_getter.moving_away = None
