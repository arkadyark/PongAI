''' The "main" block: will be runned immediately after "import pong_ai.py'''

global ball_positions
ball_positions = []   # Static global variable. Store the positions of
                      # the ball that are passed to pong_ai.py every time.
global i_am_at_left_side 
                      # Because this algorithm is dependent on which side the paddle is at,
                      # this variable is set up to judge which side it is.
   
def ball_is_away(paddle_frect, other_paddle_frect):
    '''Judge if the ball is moving away from our paddle.
    '''
    global ball_positions
    global i_am_at_left_side
    if (paddle_frect.pos[0] > other_paddle_frect.pos[0]):
	i_am_at_left_side = False
    else:
	i_am_at_left_side = True    
    n = len(ball_positions) - 1
    
    if (n == 0):
	return False   # Used to prevent list IndexOutOfRange error
    
    if (i_am_at_left_side):
	if (ball_positions[n].pos[0] > ball_positions[n-1].pos[0]):
	    return True
	else:
	    return False
    else:  # I (paddle) am at right side
	if (ball_positions[n].pos[0] > ball_positions[n-1].pos[0]):
	    return False
	else:
	    return True

def ball_should_be(paddle_frect, other_paddle_frect, ball_frect, table_size):
    '''According to the ball positions, calculate the velocity, 
    return the y value of the position of the ball when its x value is the same
    as our paddle.
    '''
    global i_am_at_left_side
  
    global ball_positions
    n = len(ball_positions) - 1
    
    if (n == 0):
	return .5 * table_size[1]
    
    tan_ball_direction = (ball_positions[n].pos[1] - ball_positions[n-1].pos[1]) / \
                         (ball_positions[n].pos[0] - ball_positions[n-1].pos[0])
    if(i_am_at_left_side):
	ball_will_be_y = ball_frect.pos[1] - ((ball_frect.pos[0] - paddle_frect.pos[0] - .5*paddle_frect.size[0] - .5*ball_frect.size[0]) * tan_ball_direction)
    else:
	ball_will_be_y = ball_frect.pos[1] + ((paddle_frect.pos[0] - ball_frect.pos[0] -.5*paddle_frect.size[0] - .5*ball_frect.size[0]) * tan_ball_direction)
    
    if (ball_will_be_y <0):
	if(int(ball_will_be_y / table_size[1]) % 2 == 0):
	    while(ball_will_be_y < 0):
		ball_will_be_y += table_size[1]
	    ball_will_be_y = table_size[1] - ball_will_be_y
	else:
	    while(ball_will_be_y < 0):
		ball_will_be_y += table_size[1]	    
    elif (ball_will_be_y >table_size[1]):
	if(int(ball_will_be_y / table_size[1]) % 2 == 0):
	    while(ball_will_be_y > table_size[1]):
		ball_will_be_y -= table_size[1]
	else:
	    while(ball_will_be_y > table_size[1]):
		ball_will_be_y -= table_size[1]
	    ball_will_be_y = table_size[1] - ball_will_be_y    
    return ball_will_be_y    
    
    


def chaser(paddle_frect, other_paddle_frect, ball_frect, table_size):
    # Algorithm: Record the ball positions. Calculate the velocity.
    # If the ball is travelling away, move to middle; Otherwise,
    # predict the position where the ball is going to hit our paddle.
    # Move the paddle to that place.
    '''return "up" or "down", depending on which way our paddle should go to
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
    #Record the positions
    ball_positions.append(ball_frect)
    
    if (ball_is_away(paddle_frect, other_paddle_frect)):
	if (paddle_frect.pos[1] < .5 * (table_size[1] - paddle_frect.size[1])):
	    return "down"
	else:
	    return "up"
    
    else: # ball is coming
	
	if (paddle_frect.pos[1] < ball_should_be(paddle_frect, other_paddle_frect, ball_frect, table_size) - \
	                         (.5 * paddle_frect.size[1])):
	    return "down"
	else:
	    return "up"
