import math
from visualdebugger import VisualDebugger

first_move = True
ai = None


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
    global first_move, ai

    if first_move:
        ai = SncAI(paddle_frect, other_paddle_frect, ball_frect, table_size)
        first_move = False

    return ai.get_next_move(paddle_frect, other_paddle_frect, ball_frect, table_size)


class SncAI(object):
    ### STATIC VARIABLES ###
    MAX_ANGLE = 45  # Dangerous, he might change it
    PADDLE_BOUNCE = 1.2  # Ditto
    opponent_vel_history = 20  # Number of moves to average opponent velocity over
    opponent_target_history = 20  # Number of trajectories to average opponent target over
    history_weights = [1 / i for i in range(1, 21)]

    def __init__(self, paddle_frect, their_paddle_frect, ball_frect, table_size):
        """
        Initialize the AI by telling it the following:
        - Initialize the size of the table
        - determine whether we are on the left or right and assign this to move_getter.is_left_paddle
        - assign the variables "my_edge" and "their_edge" to be the x coordinates of the edges.
        """

        self.table_width = table_size[0]
        self.table_height = table_size[1]
        self.is_left_paddle = paddle_frect.pos[0] < self.table_width / 2
        if self.is_left_paddle:
            self.my_edge = paddle_frect.pos[0] + paddle_frect.size[0]
            self.their_edge = their_paddle_frect.pos[0] - ball_frect.size[0]
            self.their_wall = self.table_width
        else:
            self.my_edge = paddle_frect.pos[0] - ball_frect.size[0]
            self.their_edge = their_paddle_frect.pos[0] + their_paddle_frect.size[0]
            self.their_wall = 0

        self.previous_ball_pos = (ball_frect.pos[0], ball_frect.pos[1])
        self.ball_vel = [1, 1]
        self.opponent_vel = 0
        self.previous_opponent_y = their_paddle_frect.pos[1]
        self.previous_opponent_vels = []
        self.previous_opponent_targets = [0]  # stores all of the opponent's past targets, used for history analysis

        self.moving_away = None  # whether the ball is moving towards or away from us

        self.visual_debugger = VisualDebugger(table_size)

    def get_next_move(self, paddle_frect, their_paddle_frect, ball_frect, table_size):
        self.paddle_frect = paddle_frect
        self.their_paddle_frect = their_paddle_frect
        self.ball_frect = ball_frect
        # Being ready for the table dimensions to change
        self.table_width = table_size[0]
        self.table_height = table_size[1]

        # Update the velocity of the opponent
        if len(self.previous_opponent_vels) > SncAI.opponent_vel_history:
            self.previous_opponent_vels.pop(0)
        actual_opponent_vel = their_paddle_frect.pos[1] - self.previous_opponent_y
        self.previous_opponent_y = their_paddle_frect.pos[1]
        self.opponent_vel = (sum(self.previous_opponent_vels) + actual_opponent_vel) / \
                            float(len(self.previous_opponent_vels) + 1)
        self.previous_opponent_vels.append(actual_opponent_vel)

        # Update the velocity of the ball and related parameters
        self.ball_vel = self.get_vel(ball_frect.pos)
        self.previous_ball_pos = (ball_frect.pos[0], ball_frect.pos[1])

        self.moving_away = (
        (self.is_left_paddle and (self.ball_vel[0] > 0)) or (not self.is_left_paddle and (self.ball_vel[0] < 0)))

        if self.moving_away:
            # Strategy when the ball is heading to the opponent - go where
            # it looks like they're aiming
            self.paddle_target = self.get_centre(paddle_frect)
            
            projected_impact = self.get_ball_trajectory(self.ball_vel, self.ball_frect.pos,
                                                        self.their_edge)
            if self.out_of_reach(projected_impact):
                self.target_y = self.table_height / 2 - self.paddle_frect.size[1] / 2
            else:
                projected_opponent_pos = their_paddle_frect.pos[1] + self.opponent_vel*projected_impact['time']
                return_vel = self.get_projected_vel(
                    projected_opponent_pos, projected_impact['position'])
                projected_return_point = self.get_ball_trajectory(return_vel,
                                                                  (self.their_edge, projected_impact['position']),
                                                                  self.my_edge)['position']
                self.target_y = projected_return_point

        else:
            # Strategy when the ball is heading towards us
            projected_trajectory = self.get_ball_trajectory(self.ball_vel, self.ball_frect.pos, self.my_edge)
            self.visual_debugger.mark(VisualDebugger.POINT, (self.my_edge, projected_trajectory['position']), 0x00FFFF)
            possibilities = self.get_possible_positions(projected_trajectory)
            for possibility in possibilities:
                self.visual_debugger.mark(VisualDebugger.POINT, (self.my_edge, possibility), 0x00FF00)
                projected_vel = self.get_projected_vel(possibility, projected_trajectory['position'])
                predicted_trajectory = self.get_ball_trajectory(projected_vel, (self.my_edge, projected_trajectory['position']),
                                                            self.their_wall)
                if 0 <= predicted_trajectory['position'] <= self.table_height:
                    self.visual_debugger.mark(VisualDebugger.POINT, (self.their_wall, predicted_trajectory['position']), 0x00FF00)
            if projected_trajectory['walls'] > 1 or projected_trajectory['time'] > 3*self.paddle_frect.size[1] / 2:
                self.target_y = projected_trajectory['position'] - self.paddle_frect.size[1] / 2
            else:
                self.target_y, aiming_for = self.get_optimal_target(projected_trajectory)


        # Return the move based on parameters set earlier
        #print self.target_y
        if self.paddle_frect.pos[1] > self.target_y:
            return "up"
        elif self.paddle_frect.pos[1] < self.target_y:
            return "down"
        else:
            return "stay still"  # not a command, but does nothing.
        #return "up" if self.paddle_target > self.target_y else "down"


    def get_centre(self, frect):
        '''
        Helper function that returns the y-coordinate of the centre of an frect.
        '''
        return frect.pos[1] + 0.5*frect.size[1]

    def get_vel(self, current_pos):
        """
        Helper function that returns the change in position of the ball per tick as a 2-tuple.

        previous_pos - x, y tuple
        current_pos - x, y tuple
        """
        return (current_pos[0] - self.previous_ball_pos[0],
                current_pos[1] - self.previous_ball_pos[1])


    def get_projected_vel(self, collision_y, trajectory_position):
        """
        Return the projected velocity (as a 2-tuple) of the ball after colliding with the paddle

        Parameters:
        collision_y - the y-coordinate of the collision

        """
        projected_theta = self.get_angle(collision_y, self.paddle_frect.size[1],
                                         trajectory_position + 0.5 * self.ball_frect.size[1])
        projected_vel = [math.cos(projected_theta) * self.ball_vel[0] -
                         math.sin(projected_theta) * self.ball_vel[1],
                         math.sin(projected_theta) * self.ball_vel[0] +
                         math.cos(projected_theta) * self.ball_vel[1]]
        projected_vel[0] = -projected_vel[0]
        projected_vel = [math.cos(-projected_theta) * projected_vel[0] -
                         math.sin(-projected_theta) * projected_vel[1],
                         math.sin(-projected_theta) * projected_vel[0] +
                         math.cos(-projected_theta) * projected_vel[1]]
        if abs(projected_vel[0]) < 1:
            projected_vel[0] = 0.95 * ((2 * (not self.is_left_paddle)) - 1)
        projected_vel = (projected_vel[0] * SncAI.PADDLE_BOUNCE, projected_vel[1] * SncAI.PADDLE_BOUNCE)
        return projected_vel


    def get_angle(self, paddle_y, paddle_height, ball_y):
        """
        Given the position of the paddle and the ball, gets the angle that
        the ball will rebound off of the paddle at.
        Copied from Guerzhoy
        """
        center = paddle_y + paddle_height / 2  # centre of paddle with respect to y
        rel_dist_from_c = ((ball_y - center) / paddle_height)  # distance from ball to centre
        rel_dist_from_c = min(0.5, rel_dist_from_c)
        rel_dist_from_c = max(-0.5, rel_dist_from_c)
        sign = 1 - 2 * self.is_left_paddle

        return sign * rel_dist_from_c * SncAI.MAX_ANGLE * math.pi / 180

    def out_of_reach(self, trajectory):
        """
        Return whether or not the paddle can potentially reach the ball on its trajectory
        (whose?)

        Parameters:
        trajectory - a dictionary with keys 'position', 'walls' and 'time', typically a result of get_ball_trajectory
        is_me - a boolean indicating whether we are considering our paddle.
        """
        distance_to_ball = abs(self.their_paddle_frect.pos[1] + self.their_paddle_frect.size[1] * 0.5 - trajectory['position'])
        return (distance_to_ball - trajectory['time']) > self.their_paddle_frect.size[1] * 0.5 + 20 * trajectory[
                'walls'] + 8


    def most_likely_return_position(self):
        """
        Returns where the ball is most likely to be returned to
        Currently returns the average position of the opponent's return hits weighted by the number of turns since then.
        """
        return (sum(i * j for i, j in zip(self.previous_opponent_target, SncAI.history_weights)) /
                sum(SncAI.history_weights[:len(self.previous_opponent_target)]))  # normalize sum to 1.


    def get_ball_trajectory(self, ball_vel, ball_pos, paddle_edge, time=0, walls=0):
        """
        Return the y coordinate that the ball will hit when it reaches the edge
        that it's moving towards

        :return: a dictionary with keys position, time and walls. Position is the y position along the edge, time is
        the number of ticks until you hit the edge and walls is the number of walls you've hit.
        """
        ball_vel = list(ball_vel)  # Copying ball_vel deliberately so I don't mess stuff up.
        if ball_vel[0] == 0:
            ball_vel[0] = 1
        if ball_vel[1] == 0:
            ball_vel[1] = 1

        time_to_edge = math.ceil((paddle_edge - ball_pos[0]) / ball_vel[0])
        time_to_top = -ball_pos[1] / ball_vel[1]
        time_to_bottom = (self.table_height - ball_pos[1]) / ball_vel[1]

        time_to_wall = math.ceil(max(time_to_top, time_to_bottom))
        if time_to_wall < time_to_edge:
            # Headed for a wall
            projected_ball_vel = (ball_vel[0], -ball_vel[1])
            if time_to_top > time_to_bottom:
                projected_ball_pos = (ball_pos[0] + time_to_top * ball_vel[0], 0)
            else:
                projected_ball_pos = (ball_pos[0] + time_to_bottom * ball_vel[0], self.table_height)
            return self.get_ball_trajectory(projected_ball_vel, projected_ball_pos, paddle_edge,
                                            time + time_to_wall, walls + 1)
        else:
            # Headed for a paddle (or edge)
            projected_y = ball_pos[1] + time_to_edge * ball_vel[1]
            if not 0 < projected_y < self.table_height:
                projected_y = self.table_height / 2
            return {'position': projected_y, 'time': time_to_edge + time, 'walls': walls}

    def get_possible_positions(self, trajectory):
        """
        Return the possible y positions that could potentially hit the ball
        """
        possibilities = []
        min_possibility = max(0, int(trajectory['position'] - self.paddle_frect.size[1]))
        max_possibility = int(min(self.table_height - self.paddle_frect.size[1], trajectory['position']))
        for i in range(min_possibility, max_possibility):
            if abs(i - self.paddle_frect.pos[1]) < trajectory['time'] + 1:
                possibilities.append(i)
        return possibilities

    def get_optimal_target(self, projected_trajectory):
        """
        Return the best point along the paddle with which to hit the ball
        """
        best_position = self.paddle_frect.pos[1] + self.paddle_frect.size[1] / 2
        best_score = -10000
        for possibility in self.get_possible_positions(projected_trajectory):
            projected_vel = self.get_projected_vel(possibility, projected_trajectory['position'])
            predicted_trajectory = self.get_ball_trajectory(projected_vel, (self.my_edge, projected_trajectory['position']),
                                                            self.their_wall)
            if 0 <= predicted_trajectory['position'] <= self.table_height \
                    and predicted_trajectory['time'] > 0:
                score = abs(predicted_trajectory['position'] - (self.their_paddle_frect.pos[1] + self.their_paddle_frect.size[1] / 2)) - \
                        predicted_trajectory['time'] - 10*predicted_trajectory['walls']**2
                if score > best_score:
                    best_position = possibility
                    best_score = score

        if best_score == -10000:
            if (self.ball_frect.pos[0] < self.table_width/2) == self.is_left_paddle:
                best_position = projected_trajectory['position']
            else:
                best_position = self.table_height / 2 - self.paddle_frect.size[1] / 2
        try:
            return best_position, predicted_trajectory['position']
        except:
            return best_position, 0


move_getter.name = "class based chaser AI with aggression"  # yes, I'm giving the function a property, but this is the best way to do it.
