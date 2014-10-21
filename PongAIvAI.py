#   PongAIvAI
#   Author: Michael Guerzhoy, 2014. 
#   http://www.cs.toronto.edu/~guerzhoy/
#   Email: guerzhoy at cs.toronto.edu
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version. You must credit Michael Guerzhoy
#   for the original parts of this code.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   Parts of the code are based on T. S. Hayden Dennison's PongClone (2011)
#   http://www.pygame.org/project-PongClone-1740-3032.html

#This code runs with Python 2


import pygame, sys, time, random, os
from pygame.locals import *

import math



white = [255, 255, 255]
black = [0, 0, 0]    
clock = pygame.time.Clock()

class fRect:
    def __init__(self, pos, size):
        self.pos = (pos[0], pos[1])
        self.size = (size[0], size[1])
    def move(self, x, y):
        return fRect((self.pos[0]+x, self.pos[1]+y), self.size)

    def move_ip(self, x, y):
        self.pos = (self.pos[0] + x, self.pos[1] + y)

    def get_rect(self):
        return Rect(self.pos, self.size)

    def copy(self):
        return fRect(self.pos, self.size)


class Paddle:
    def __init__(self, pos, size, speed, max_angle,  facing, timeout):
        self.frect = fRect((pos[0]-size[0]/2, pos[1]-size[1]/2), size)
        self.speed = speed        
        self.size = size
        self.facing = facing
        self.max_angle = max_angle
        self.timeout = timeout

    def factor_accelerate(self, factor):
        self.speed = factor*self.speed


    def move(self, enemy_frect, ball_frect, table_size):
        #direction = self.move_getter(self.frect.copy(), enemy_frect.copy(), ball_frect.copy(), tuple(table_size))
        direction = timeout(self.move_getter, (self.frect.copy(), enemy_frect.copy(), ball_frect.copy(), tuple(table_size)), {}, 0.001)
        if direction == "up":
            self.frect.move_ip(0, -self.speed)
        elif direction == "down":
            self.frect.move_ip(0, self.speed)

        to_bottom = (self.frect.pos[1]+self.frect.size[1])-table_size[1]

        if to_bottom > 0:
            self.frect.move_ip(0, -to_bottom)
        to_top = self.frect.pos[1]
        if to_top < 0:
            self.frect.move_ip(0, -to_top)


    def get_face_pts(self):
        return ((self.frect.pos[0] + self.frect.size[0]*self.facing, self.frect.pos[1]),
                (self.frect.pos[0] + self.frect.size[0]*self.facing, self.frect.pos[1] + self.frect.size[1]-1)
                )

    def get_angle(self, y):
        center = self.frect.pos[1]+self.size[1]/2
        rel_dist_from_c = ((y-center)/self.size[1])
        rel_dist_from_c = min(.5, rel_dist_from_c)
        rel_dist_from_c = max(-.5, rel_dist_from_c)
        sign = 1-2*self.facing

        return sign*rel_dist_from_c*self.max_angle*math.pi/180



class Ball:
    def __init__(self, table_size, size, paddle_bounce, wall_bounce, dust_error, init_speed_mag):
        rand_ang = (.2+.6*random.random())*math.pi*(1-2*(random.random()>.5))+.5*math.pi
        speed = (init_speed_mag*math.cos(rand_ang), init_speed_mag*math.sin(rand_ang))
        pos = (table_size[0]/2, table_size[1]/2)
        self.frect = fRect((pos[0]-size[0]/2, pos[1]-size[1]/2), size)
        self.speed = speed        
        self.size = size        
        self.paddle_bounce = paddle_bounce
        self.wall_bounce = wall_bounce
        self.dust_error = dust_error
        self.init_speed_mag = init_speed_mag
        self.prev_bounce = None

    def get_center(self):
        return (self.frect.pos[0] + .5*self.frect.size[0], self.frect.pos[1] + .5*self.frect.size[1])


    def get_speed_mag(self):
        return math.sqrt(self.speed[0]**2+self.speed[1]**2)

    def factor_accelerate(self, factor):
        self.speed = (factor*self.speed[0], factor*self.speed[1])




    def move(self, paddles, table_size):
        for paddle in paddles:
            if self.frect.get_rect().colliderect(paddle.frect.get_rect()):

                theta = paddle.get_angle(self.frect.pos[1]+.5*self.frect.size[1])

                v = self.speed

                v = [math.cos(theta)*v[0]-math.sin(theta)*v[1], 
                        math.sin(theta)*v[0]+math.cos(theta)*v[1]]

                v[0] = -v[0]

                v = [math.cos(-theta)*v[0]-math.sin(-theta)*v[1], 
                        math.sin(-theta)*v[0]+math.cos(-theta)*v[1]]                


                if(abs(v[0]) < 1):
                    v[0] = .95*(2*paddle.facing-1)


                #a bit hacky, prevent multiple bounces from accelerating
                #the ball too much
                if not paddle is self.prev_bounce:
                    self.speed = (v[0]*self.paddle_bounce, v[1]*self.paddle_bounce)

                self.prev_bounce = paddle

                while self.frect.get_rect().colliderect(paddle.frect.get_rect()):
                    self.frect.move_ip(.1*self.speed[0], .1*self.speed[1])



                return


        walls_Rects = [Rect((-100, -100), (table_size[0]+100, 100)),
                Rect((-100, table_size[1]), (table_size[0]+100, 100))]

        for wall_rect in walls_Rects:
            if self.frect.get_rect().colliderect(wall_rect):

                r1 = 1+2*(random.random()-.5)*self.dust_error
                r2 = 1+2*(random.random()-.5)*self.dust_error
                self.speed = (self.wall_bounce*self.speed[0]*r1, -self.wall_bounce*self.speed[1]*r2)

                while self.frect.get_rect().colliderect(wall_rect):
                    self.frect.move_ip(.1*self.speed[0], .1*self.speed[1])
                return

        self.frect.move_ip(self.speed[0], self.speed[1])        


def directions_from_input(paddle_rect, other_paddle_rect, ball_rect, table_size):
    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        return "up"    
    elif keys[pygame.K_DOWN]:
        return "down"
    else:
        return None




def timeout(func, args=(), kwargs={}, timeout_duration=1, default=None):
    '''From:
    http://code.activestate.com/recipes/473878-timeout-function-using-threading/'''
    import threading
    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None

        def run(self):
            try:
                self.result = func(*args, **kwargs)
            except:
                self.result = default

    it = InterruptableThread()
    it.start()
    it.join(timeout_duration)
    if it.isAlive():
        return default
    else:
        return it.result

def render(screen, paddles, ball, score, table_size):
    screen.fill(black)    

    pygame.draw.rect(screen, white, paddles[0].frect.get_rect())
    pygame.draw.rect(screen, white, paddles[1].frect.get_rect())

    pygame.draw.circle(screen, white, (int(ball.get_center()[0]), int(ball.get_center()[1])),  int(ball.frect.size[0]/2), 0)


    pygame.draw.line(screen, white, [screen.get_width()/2, 0], [screen.get_width()/2, screen.get_height()])

    score_font = pygame.font.Font(None, 32)
    screen.blit(score_font.render(str(score[0]), True, white), [int(0.4*table_size[0])-8, 0])
    screen.blit(score_font.render(str(score[1]), True, white), [int(0.6*table_size[0])-8, 0])

    pygame.display.flip()



def check_point(score, ball, table_size):
    if ball.frect.pos[0]+ball.size[0]/2 < 0:
        score[1] += 1
        ball = Ball(table_size, ball.size, ball.paddle_bounce, ball.wall_bounce, ball.dust_error, ball.init_speed_mag)
        return (ball, score)
    elif ball.frect.pos[0]+ball.size[0]/2 >= table_size[0]:
        ball = Ball(table_size, ball.size, ball.paddle_bounce, ball.wall_bounce, ball.dust_error, ball.init_speed_mag)        
        score[0] += 1
        return (ball, score)

    return (ball, score)


def game_loop(screen, paddles, ball, table_size, clock_rate, turn_wait_rate, score_to_win):
    score = [0, 0]





    while max(score) < score_to_win:
        old_score = score[:]
        ball, score = check_point(score, ball, table_size)        
        if score != old_score:
            font = pygame.font.Font(None, 32)            
            if score[0] != old_score[0]:
                screen.blit(font.render("Left scores!", True, white, black), [0, 32])
            else:
                screen.blit(font.render("Right scores!", True, white, black), [int(table_size[0]/2+20), 32])


            pygame.display.flip()
            clock.tick(turn_wait_rate)



        render(screen, paddles, ball, score, table_size)
        paddles[0].move(paddles[1].frect, ball.frect, table_size)
        paddles[1].move(paddles[0].frect, ball.frect, table_size)
        ball.move(paddles, table_size)



        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[K_q]:            
            return



        clock.tick(clock_rate)

    font = pygame.font.Font(None, 64)                
    if score[0] > score[1]:
        screen.blit(font.render("Left wins!", True, white, black), [24, 32])
    else:
        screen.blit(font.render("Right wins!", True, white, black), [24, 32])
    pygame.display.flip()
    clock.tick(2)

    pygame.event.pump()
    while any(pygame.key.get_pressed()):
        pygame.event.pump()
        clock.tick(30)

    return

def init_game(mode):
    table_size = (440, 280)
    paddle_size = (10, 70)
    ball_size = (15, 15)
    paddle_speed = 1
    max_angle = 45

    paddle_bounce = 1.2
    wall_bounce = 1.00
    dust_error = 0.1
    init_speed_mag = 2
    timeout = .200
    clock_rate = 80
    turn_wait_rate = 3
    score_to_win = 5


    screen = pygame.display.set_mode(table_size)    
    pygame.display.set_caption('PongAIvAI')

    paddles = [Paddle((20, table_size[1]/2), paddle_size, paddle_speed, max_angle,  1, timeout),
            Paddle((table_size[0]-1-20, table_size[1]/2), paddle_size, paddle_speed, max_angle, 0, timeout)]
    ball = Ball(table_size, ball_size, paddle_bounce, wall_bounce, dust_error, init_speed_mag)

    import chaser_ai, straight_no_chaser_ai
    if mode == '1':
        paddles[0].move_getter = directions_from_input
        paddles[1].move_getter = straight_no_chaser_ai.move_getter
    if mode == '2':
        paddles[0].move_getter = chaser_ai.chaser
        paddles[1].move_getter = straight_no_chaser_ai.move_getter
    game_loop(screen, paddles, ball, table_size, clock_rate, turn_wait_rate, score_to_win)
    pygame.quit()


if __name__ == '__main__':
    try:
        mode = sys.argv[1]
        assert(mode in ('1', '2'))
    except:
        mode = '1'
    pygame.init()
    init_game(mode)
