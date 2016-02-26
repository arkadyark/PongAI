"""
Team name: BallNet
Team members: Sooham Rafiz, Juan Camilo Osorio
Student Numbers: 1001250683, 
Credits to Michael Guzerhoy work in PongAIvAI.py for lines 43 - 59 of
the code below.
"""
import math

ai_set_up = False
ai = None


def wrap(a, b):
    """ Wraps the distance a around the distance b and returns the recess."""
    quo, rem = divmod(abs(a), b)
    return rem if (quo % 2 == 0) else (b - rem)


def pong_ai(paddle, enemy, ball, table_size):
    global ai, ai_set_up

    # setup ai one time
    if not ai_set_up:
        ai = AI(paddle, table_size)
        ai_set_up = True

    v = ai.velocity(ball)
    # if ball not moving horizontally
    if v[0] == 0:
        return 'nothing'

    # if ball coming towards
    if ai.ball_towards:
        y_dist = (ball.pos[1] + v[1] * ((paddle.pos[0] - ball.pos[0]) / v[0]))
        landing_prediction = wrap(y_dist, table_size[1])

        if ai.ball_old_dist < 3 * paddle.size[0] and ai.mean_change:
            if not ai.mean_landing_pos:
                ai.mean_landing_pos = y_dist
            else:
                ai.mean_landing_pos = (y_dist + ai.n * ai.mean_landing_pos) / (ai.n + 1)
            ai.n += 1
            ai.mean_change = False

    else:  # ball moving away defensive
        if not ai.mean_change:
            ai.mean_change = True
        if ai.n > 5:
            landing_prediction = ai.mean_landing_pos
        else:
            landing_prediction = ai.TABLE_CENTER

    ai.update(paddle, ball)

    if ai.ball_towards:
        killit = (enemy.pos[1] + enemy.size[1] / 2 > ai.TABLE_CENTER)
        beta = math.atan(1 - ((v[1] / v[0]) * (abs(paddle.pos[0] - enemy.pos[0]) / ((-table_size[1] * killit) - landing_prediction))))
        beta = min(-.5, beta)
        beta = max(.5, beta)

        paddle_hit_point = (paddle.size[1] * beta / 2) - (paddle.size[1] / 2) + landing_prediction + (ball.size[1] / 2)
        quo, rem = divmod(paddle_hit_point, paddle.size[1])
        paddle_hit_point = rem if (quo % 2 == 0) else (paddle.size[1] - rem)
    else:
        paddle_hit_point = paddle.size[1] / 2

    if not ((8 * paddle_hit_point > paddle.size[1]) and (8 * paddle_hit_point < 7 * paddle.size[1])):
        if landing_prediction < ai.TABLE_CENTER:
            paddle_hit_point = paddle.size[1] / 8
        elif landing_prediction > ai.TABLE_CENTER:
            paddle_hit_point = 7 * paddle.size[1] / 8
        else:
            paddle_hit_point = paddle.size[1] / 2

    if paddle_hit_point + paddle.pos[1] < landing_prediction:
        return 'down'
    elif paddle_hit_point + paddle.pos[1] > landing_prediction:
        return 'up'
    else:
        return 'nothing'


class AI(object):
    """ Represents the artifically intelligent pong player"""

    def __init__(self, paddle, table_size):
        self.ball_old_pos = (table_size[0] / 2, table_size[1] / 2)
        self.ball_old_v = (0, 0)
        self.ball_old_dist = abs(paddle.pos[0] - self.ball_old_pos[0])
        self.ball_towards = None
        self.TABLE_CENTER = table_size[1] / 2
        self.mean_landing_pos = None
        self.n = 0
        self.mean_change = True

    def velocity(self, ball):
        return ball.pos[0] - self.ball_old_pos[0], ball.pos[1] - self.ball_old_pos[1]

    def towards(self, paddle, ball):
        current_dist = abs(paddle.pos[0] - ball.pos[0])
        if current_dist < self.ball_old_dist:
            self.ball_towards = True
        elif current_dist > self.ball_old_dist:
            self.ball_towards = False

    def update(self, paddle, ball):
        self.ball_old_v = self.velocity(ball)
        self.ball_old_pos = ball.pos
        self.towards(paddle, ball)
        self.ball_old_dist = abs(paddle.pos[0] - ball.pos[0])
