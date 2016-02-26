"""
Name of AI: Inigo Montoya
Author: Andrew Ilersich
"""
import math, pygame

def mmod(a, b):
    return abs(a - b * (round(a/b)))

def mmod_count(a, b):
    return abs(a//b)

def dot_product(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))

def find_angle(v1, v2):
    return math.acos(dot_product(v1, v2) / (math.sqrt(dot_product(v1, v1)) * math.sqrt(dot_product(v2, v2))))

def get_angle(paddle_frect, y):
    center = paddle_frect.pos[1]+paddle_frect.size[1]/2
    rel_dist_from_c = ((y-center)/paddle_frect.size[1])
    rel_dist_from_c = min(.5, rel_dist_from_c)
    rel_dist_from_c = max(-.5, rel_dist_from_c)
    
    return rel_dist_from_c*math.pi/4

def all_poss_angles():
    angles = []
    steps = 20
    
    for i in range(int(-0.5*steps), int(0.5*steps)):
        angles.append((i/steps) * (math.pi/4))
    
    return angles    

def aim_left(paddle_frect, other_paddle_frect, table_size, direction, move_to_pos, ball_frect, bounce_count):
    global last_aim
    
    tried_angles = [False, False]
    
    while not (tried_angles[0] or tried_angles[1]):
        if ball_frect.pos[0] > table_size[0] / 4:
            if other_paddle_frect.pos[1] > table_size[1] / 2:
                aim = 0
            else:
                aim = table_size[1]
            last_aim = aim
        else:
            aim = last_aim
        
        if aim == 0:
            sign = 1
        else:
            sign = -1
        
        if bounce_count % 2 == 1:
            direction = -direction
        
        aim_direction = (aim - move_to_pos)/(table_size[0] - (paddle_frect.pos[0] + paddle_frect.size[0] + 7.5))
        
        v = [-1, direction]
        nat_v = [1, -direction]
        aim_v = [1, aim_direction]
        
        angle = find_angle(nat_v, aim_v)
        
        rel_dist_from_c = angle / (0.5 * math.pi)
        
        if (rel_dist_from_c > 0.5 or rel_dist_from_c < -0.5):
            if aim == 0:
                aim = table_size[1]
                tried_angles[0] = True
            else:
                aim = 0
                tried_angles[1] = True
        else:
            tried_angles = [True, True]
    
    if abs(aim_direction) > abs(direction) and direction > 0:
        rel_dist_from_c = abs(rel_dist_from_c) * -aim_direction * abs(1/aim_direction)
    elif abs(aim_direction) > abs(direction) and direction < 0:
        rel_dist_from_c = abs(rel_dist_from_c) * -aim_direction * abs(1/aim_direction)
    elif abs(aim_direction) < abs(direction) and direction > 0:
        rel_dist_from_c = sign * abs(rel_dist_from_c) * aim_direction * abs(1/aim_direction)
    elif abs(aim_direction) < abs(direction) and direction < 0:
        rel_dist_from_c = sign * abs(rel_dist_from_c) * -aim_direction * abs(1/aim_direction)
    else:
        rel_dist_from_c = abs(rel_dist_from_c) * -aim_direction * abs(1/aim_direction)
    
    rel_dist_from_c = min(.5, rel_dist_from_c)
    rel_dist_from_c = max(-.5, rel_dist_from_c)
    
    move_to_pos = rel_dist_from_c*paddle_frect.size[1]
    
    return move_to_pos

def aim_right(paddle_frect, other_paddle_frect, table_size, direction, move_to_pos, ball_frect, bounce_count):
    global last_aim
    
    tried_angles = [False, False]
    
    while not (tried_angles[0] or tried_angles[1]):
        if ball_frect.pos[0] < 3 * table_size[0] / 4:
            if other_paddle_frect.pos[1] > table_size[1] / 2:
                aim = 0
            else:
                aim = table_size[1]
            last_aim = aim
        else:
            aim = last_aim
        
        if aim == 0:
            sign = 1
        else:
            sign = -1
        
        if bounce_count % 2 == 1:
            direction = -direction
        
        aim_direction = (aim - move_to_pos)/(paddle_frect.pos[0] - 7.5)
        
        v = [1, -direction]
        nat_v = [-1, direction]
        aim_v = [-1, aim_direction]
        
        angle = find_angle(nat_v, aim_v)
        
        rel_dist_from_c = angle / (0.5 * math.pi)
        
        if (rel_dist_from_c > 0.5 or rel_dist_from_c < -0.5):
            if aim == 0:
                aim = table_size[1]
                tried_angles[0] = True
            else:
                aim = 0
                tried_angles[1] = True
        else:
            tried_angles = [True, True]
    
    if abs(aim_direction) > abs(direction) and direction > 0:
        rel_dist_from_c = abs(rel_dist_from_c) * -aim_direction * abs(1/aim_direction)
    elif abs(aim_direction) > abs(direction) and direction < 0:
        rel_dist_from_c = abs(rel_dist_from_c) * -aim_direction * abs(1/aim_direction)
    elif abs(aim_direction) < abs(direction) and direction > 0:
        rel_dist_from_c = sign * abs(rel_dist_from_c) * -aim_direction * abs(1/aim_direction)
    elif abs(aim_direction) < abs(direction) and direction < 0:
        rel_dist_from_c = sign * abs(rel_dist_from_c) * aim_direction * abs(1/aim_direction)
    else:
        rel_dist_from_c = abs(rel_dist_from_c) * -aim_direction * abs(1/aim_direction)
    
    if move_to_pos < 35 or move_to_pos > table_size[1] - 35:
        rel_dist_from_ce = -rel_dist_from_c    
    
    rel_dist_from_c = min(.5, rel_dist_from_c)
    rel_dist_from_c = max(-.5, rel_dist_from_c)
    
    move_to_pos = rel_dist_from_c*paddle_frect.size[1]
    
    return move_to_pos

def pong_ai(paddle_frect, other_paddle_frect, ball_frect, table_size):
    global ball_last_pos
    global last_aim
    global side
    
    try:
        ball_speed = (ball_frect.pos[0] - ball_last_pos[0], ball_frect.pos[1] - ball_last_pos[1])
    except NameError:
        ball_last_pos = ball_frect.pos[:]
        
        if paddle_frect.pos[0] < table_size[0] / 2:
            side = "left"
        else:
            side = "right"
        
        return
    
    ball_last_pos = ball_frect.pos[:]
    ball_mid_pos = [ball_frect.pos[0] + (ball_frect.size[0] / 2), ball_frect.pos[1] + (ball_frect.size[1] / 2)]
    
    try:
        direction = ball_speed[1] / ball_speed[0]
    except ZeroDivisionError:
        direction = 0
    
    yint = ball_mid_pos[1] - (direction * ball_mid_pos[0])
    
    if ball_speed[0] < 0 and side == "left":
        move_to_pos = direction * (paddle_frect.pos[0] + paddle_frect.size[0] + (ball_frect.size[0] / 2)) + yint
        bounce_count = mmod_count(move_to_pos, table_size[1])
        move_to_pos = mmod(move_to_pos, 2 * (table_size[1] - ball_frect.size[1]/2))
        move_to_pos += aim_left(paddle_frect, other_paddle_frect, table_size, direction, move_to_pos, ball_frect, bounce_count)
        
        move_to_pos = round(move_to_pos)
        
        if paddle_frect.pos[1] + (paddle_frect.size[1] / 2) < move_to_pos:
            return "down"
        elif paddle_frect.pos[1] + (paddle_frect.size[1] / 2) > move_to_pos:
            return "up"
        else:
            return
    
    elif ball_speed[0] > 0 and side == "right":
        move_to_pos = direction * (paddle_frect.pos[0] - (ball_frect.size[0] / 2)) + yint
        bounce_count = mmod_count(move_to_pos, table_size[1])
        move_to_pos = mmod(move_to_pos, 2 * (table_size[1] - ball_frect.size[1]/2))
        move_to_pos += aim_right(paddle_frect, other_paddle_frect, table_size, direction, move_to_pos, ball_frect, bounce_count)
        
        move_to_pos = round(move_to_pos)
        
        if paddle_frect.pos[1] + (paddle_frect.size[1] / 2) < move_to_pos:
            return "down"
        elif paddle_frect.pos[1] + (paddle_frect.size[1] / 2) > move_to_pos:
            return "up"
        else:
            return
    
    else:
        if side == "left":
            other_pos = ball_mid_pos[1]+direction*(other_paddle_frect.pos[0]-7.5-ball_mid_pos[0])
            bounce_count = mmod_count(other_pos, table_size[1])
            other_pos = mmod(other_pos, 2 * (table_size[1] - ball_frect.size[1]/2))
            
            if bounce_count % 2 == 1:
                direction = -direction
            
            v = [1, direction]
            avg = 0
            
            for theta in all_poss_angles():
                poss_dir = -(v[0]*math.sin(2*theta)+v[1]*math.cos(2*theta))/(v[1]*math.sin(2*theta)-v[0]*math.cos(2*theta))
                
                temp_fut_pos = other_pos + poss_dir * (other_paddle_frect.pos[0] - 7.5)
                temp_fut_pos = mmod(temp_fut_pos, 2 * (table_size[1] - ball_frect.size[1]/2))
                
                avg += temp_fut_pos
            avg = round(avg / 20)
            
            if paddle_frect.pos[1] + (paddle_frect.size[1] / 2) < avg:
                return "down"
            elif paddle_frect.pos[1] + (paddle_frect.size[1] / 2) > avg:
                return "up"
            else:
                return
            
        else:
            other_pos = ball_mid_pos[1]+direction*(other_paddle_frect.pos[0]+10+7.5-ball_mid_pos[0])
            bounce_count = mmod_count(other_pos, table_size[1])
            other_pos = mmod(other_pos, 2 * (table_size[1] - ball_frect.size[1]/2))
            
            if bounce_count % 2 == 1:
                direction = -direction
            
            v = [-1, direction]
            avg = 0
            
            for theta in all_poss_angles():
                poss_dir = (v[0]*math.sin(2*theta)+v[1]*math.cos(2*theta))/(v[1]*math.sin(2*theta)-v[0]*math.cos(2*theta))
                
                temp_fut_pos = other_pos + poss_dir * (paddle_frect.pos[0] - 7.5)
                temp_fut_pos = mmod(temp_fut_pos, 2 * (table_size[1] - ball_frect.size[1]/2))
                
                avg += temp_fut_pos
            avg = round(avg / 20)
            
            if paddle_frect.pos[1] + (paddle_frect.size[1] / 2) < avg:
                return "down"
            elif paddle_frect.pos[1] + (paddle_frect.size[1] / 2) > avg:
                return "up"
            else:
                return