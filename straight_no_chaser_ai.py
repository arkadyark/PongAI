import math

turn_number = 1
MAX_ANGLE = 45 # Dangerous, he might change it
PADDLE_BOUNCE = 1.2 # Ditto
opponent_vel_history = 20 # Number of moves to average opponent velocity over

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
<<<<<<< HEAD
	initialize(paddle_frect, other_paddle_frect, table_size[0])
    turn_number += 1
    if move_getter.previous_ball_pos != None:
	move_getter.ball_vel = get_vel(move_getter.previous_ball_pos, ball_frect.pos)
	move_getter.opponent_vel = other_paddle_frect.pos[1] - move_getter.previous_opponent_pos
=======
        initialize(paddle_frect, table_size[0])
    turn_number += 1
    if move_getter.previous_ball_pos != None:
        move_getter.ball_vel = get_vel(move_getter.previous_ball_pos, ball_frect.pos)
>>>>>>> c4d45b6f6489b820236a99ff2fade393251c9def
    move_getter.previous_ball_pos = ball_frect.pos
    move_getter.previous_opponent_pos = other_paddle_frect.pos[1]
    if len(move_getter.previous_opponent_vel) >= opponent_vel_history:
	move_getter.previous_opponent_vel.pop(0)
    move_getter.previous_opponent_vel.append(move_getter.opponent_vel)
    move_getter.opponent_vel = sum(move_getter.previous_opponent_vel)/float(len(move_getter.previous_opponent_vel))
    moving_left = move_getter.ball_vel[0] < 0
    moving_away = moving_left != move_getter.left_paddle
    if moving_left:
<<<<<<< HEAD
	paddle_edge = paddle_frect.size[0]
	other_paddle_edge = paddle_frect.pos[0]
    else:
	paddle_edge = paddle_frect.pos[0]
	other_paddle_edge = paddle_frect.size[0]
    if not moving_away:
	trajectory = get_ball_trajectory(move_getter.ball_vel, ball_frect.pos, paddle_edge, table_size[1])
	estimated_ball_pos = trajectory['position'] + ball_frect.size[1]/2
	if out_of_reach(paddle_frect, trajectory):
	    # TODO - dangerous with walls
	    print "I can't reach the ball, moving to centre"
	    move_getter.target_y = table_size[1]*0.5
	else:
	    print "The ball is actually coming to:", estimated_ball_pos
	    move_getter.target_y = estimated_ball_pos
    else:
	trajectory = get_ball_trajectory(move_getter.ball_vel, ball_frect.pos, paddle_edge, table_size[1], 0)
	if out_of_reach(other_paddle_frect, trajectory):
	    # Move to middle if point is over
	    print "The opponent can't reach the ball, moving to centre"
	    move_getter.target_y = table_size[1]/2
	else:
	    # Assuming opponent continues their trajectory
	    collision_opponent_y = other_paddle_frect.pos[1] + move_getter.opponent_vel*trajectory['time']
	    if collision_opponent_y < 0:
		collision_opponent_y = 0
	    elif collision_opponent_y > table_size[1]:
		collision_opponent_y = table_size[1]
	    projected_theta = get_angle(collision_opponent_y, other_paddle_frect.size[1], trajectory['position'] + 0.5*ball_frect.size[1], not move_getter.left_paddle)
	    projected_vel = [math.cos(projected_theta)*move_getter.ball_vel[0] - \
		    math.sin(projected_theta)*move_getter.ball_vel[1],
		    math.sin(projected_theta)*move_getter.ball_vel[0] + \
			    math.cos(projected_theta)*move_getter.ball_vel[1]]
	    projected_vel[0] = -projected_vel[0]
	    projected_vel = [math.cos(-projected_theta)*projected_vel[0] - \
		    math.sin(-projected_theta)*projected_vel[0],
		    math.sin(-projected_theta)*projected_vel[0] + \
			    math.cos(-projected_theta)*projected_vel[1]]
	    if abs(projected_vel[0]) < 1:
		projected_vel[0] = 0.95*(2*(not move_getter.left_paddle - 1))
	    projected_vel = (projected_vel[0]*PADDLE_BOUNCE, projected_vel[1]*PADDLE_BOUNCE)
	    return_trajectory = get_ball_trajectory(projected_vel, (paddle_edge, trajectory['position']), other_paddle_edge, table_size[1])
	    print "I think the opponent will hit it to:", return_trajectory['position'] 
	    move_getter.target_y = return_trajectory['position'] 
=======
        paddle_edge = paddle_frect.size[0]
    else:
        paddle_edge = paddle_frect.pos[0]
    if not moving_away:
         move_getter.target_y = get_ball_trajectory(move_getter.ball_vel, ball_frect.pos, paddle_edge, table_size[1], 0)[0] + ball_frect.size[1]/2
    else:
        move_getter.target_y = table_size[1]/2
>>>>>>> c4d45b6f6489b820236a99ff2fade393251c9def
    if paddle_frect.pos[1]+paddle_frect.size[1]/2 < move_getter.target_y:
        return "down"
    else:
        return "up"

def out_of_reach(paddle_frect, trajectory):
    distance_to_ball = abs(paddle_frect.pos[1] + paddle_frect.size[1]*0.5 - trajectory['position'])
    return distance_to_ball - trajectory['time'] > paddle_frect.size[1]*0.5 + 25*trajectory['walls']

def get_vel(previous_pos, current_pos):
    return (current_pos[0] - previous_pos[0],\
<<<<<<< HEAD
	    current_pos[1] - previous_pos[1])

def get_angle(paddle_y, paddle_height, ball_y, left_paddle):
    center = paddle_y+paddle_height/2
    rel_dist_from_c = ((ball_y - center)/paddle_height)
    rel_dist_from_c = min(0.5, rel_dist_from_c)
    rel_dist_from_c = max(-0.5, rel_dist_from_c)
    sign = 1-2*left_paddle
=======
            current_pos[1] - move_getter.previous_ball_pos[1])
>>>>>>> c4d45b6f6489b820236a99ff2fade393251c9def

    return sign*rel_dist_from_c*MAX_ANGLE*math.pi/180

def get_ball_trajectory(ball_vel, ball_pos, paddle_edge, table_height, time = 0, walls = 0):
    '''
    Return the y coordinate that the ball will hit when it reaches the edge
    that it's moving towards
    '''
    time_to_edge = (paddle_edge - ball_pos[0])/ball_vel[0]
    time_to_top = -ball_pos[1]/ball_vel[1]
    time_to_bottom = (table_height - ball_pos[1])/ball_vel[1]
    time_to_wall = max(time_to_top, time_to_bottom)
    if (time_to_wall < time_to_edge):
<<<<<<< HEAD
	# Headed for a wall
	projected_ball_vel = (ball_vel[0], -ball_vel[1])
	if time_to_top > time_to_bottom:
	    projected_ball_pos = (ball_pos[0] + time_to_top*ball_vel[0], 0)
	else:
	    projected_ball_pos = (ball_pos[0] + time_to_bottom*ball_vel[0], table_height)
	return get_ball_trajectory(projected_ball_vel, projected_ball_pos,\
		    paddle_edge, table_height, time + time_to_wall, walls + 1) 
    else:
	# Headed for a paddle (or edge)
	projected_y = ball_pos[1] + time_to_edge*ball_vel[1]
	return {'position':projected_y, 'time':time_to_edge + time, 'walls':walls}
=======
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
>>>>>>> c4d45b6f6489b820236a99ff2fade393251c9def

def initialize(paddle_frect, their_paddle_frect, table_width):
    move_getter.left_paddle = paddle_frect.pos[0] < table_width/2
    if move_getter.left_paddle:
	move_getter.my_edge = paddle_frect.size[0]
	move_getter.their_edge = their_paddle_frect.pos[0]
    else:
	move_getter.my_edge = paddle_frect.pos[0]
	move_getter.their_edge = their_paddle_frect.size[0]

move_getter.previous_ball_pos = None
move_getter.ball_vel = [1, 1]
move_getter.opponent_vel = 0
move_getter.previous_opponent_vel = [0]
move_getter.moving_away = None
