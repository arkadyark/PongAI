import math

first_move = True


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
    global first_move

    if first_move:
        s = SncAI(paddle_frect, other_paddle_frect, ball_frect, table_size)
        first_move = False

    return s.get_next_move(paddle_frect, other_paddle_frect, ball_frect, table_size)


class SncAI():
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
            self.my_edge = paddle_frect.size[0]
            self.their_edge = their_paddle_frect.pos[0]
        else:
            self.my_edge = paddle_frect.pos[0]
            self.their_edge = their_paddle_frect.size[0]

        self.previous_ball_pos = None
        self.ball_vel = [1, 1]
        self.opponent_vel = 0
        self.previous_opponent_vel = [0]
        self.previous_opponent_target = [0]  # stores all of the opponent's past targets, used for history analysis
        self.moving_away = None  # whether the ball is moving towards or away from us

    def get_next_move(self, paddle_frect, their_paddle_frect, ball_frect, table_size):
        self.paddle_frect = paddle_frect
        self.their_paddle_frect = their_paddle_frect
        self.ball_frect = ball_frect
        self.table_width = table_size[0]
        self.table_height = table_size[1]

        #Actually return a move here.

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
                                         trajectory_position + 0.5 * self.ball_frect.size[1],
                                         not self.is_left_paddle)
        projected_vel = [math.cos(projected_theta) * self.ball_vel[0] -
                         math.sin(projected_theta) * self.ball_vel[1],
                         math.sin(projected_theta) * self.ball_vel[0] +
                         math.cos(projected_theta) * self.ball_vel[1]]
        projected_vel[0] = -projected_vel[0]
        projected_vel = [math.cos(-projected_theta) * projected_vel[0] -
                         math.sin(-projected_theta) * projected_vel[0],
                         math.sin(-projected_theta) * projected_vel[0] +
                         math.cos(-projected_theta) * projected_vel[1]]
        if abs(projected_vel[0]) < 1:
            projected_vel[0] = 0.95 * (2 * (not self.is_left_paddle - 1))
        projected_vel = (projected_vel[0] * SncAI.PADDLE_BOUNCE, projected_vel[1] * SncAI.PADDLE_BOUNCE)
        return projected_vel


    def get_angle(self, paddle_y, paddle_height, ball_y, is_left_paddle):
        """
        Given the position of the paddle and the ball, gets the angle that
        the ball will rebound off of the paddle at.
        Copied from Guerzhoy
        """
        center = paddle_y + paddle_height / 2  # centre of paddle with respect to y
        rel_dist_from_c = ((ball_y - center) / paddle_height)  # distance from ball to centre
        rel_dist_from_c = min(0.5, rel_dist_from_c)
        rel_dist_from_c = max(-0.5, rel_dist_from_c)
        sign = 1 - 2 * is_left_paddle

        return sign * rel_dist_from_c * SncAI.MAX_ANGLE * math.pi / 180

    def out_of_reach(self, trajectory, is_me):
        """
        Return whether or not the paddle can potentially reach the ball on its trajectory
        (whose?)

        Parameters:
        trajectory - a dictionary with keys 'position', 'walls' and 'time', typically a result of get_ball_trajectory
        is_me - a boolean indicating whether we are considering our paddle.
        """
        distance_to_ball = abs(self.paddle_frect.pos[1] + self.paddle_frect.size[1] * 0.5 - trajectory['position'])
        if is_me:
            return (distance_to_ball - trajectory['time']) > self.paddle_frect.size[1] * 0.5 + 45 * trajectory[
                'walls'] + 8
        else:
            return (distance_to_ball - trajectory['time']) > self.paddle_frect.size[1] * 0.5 + 20 * trajectory[
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
        """
        # THIS IS A PROBLEM
        # TODO - fix
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
            return {'position': projected_y, 'time': time_to_edge + time, 'walls': walls}

    def get_possible_positions(self, trajectory):
        """
        Return the possible y positions along the paddle that could potentially hit the ball
        """
        possibilities = []
        if trajectory['position'] < self.paddle_frect.pos[1]:
            # ball going above paddle
            for i in range(self.paddle_frect.size[1]):
                if self.paddle_frect.pos[1] + i - trajectory['position'] < trajectory['time']:
                    possibilities.append(i)
        else:
            for i in range(self.paddle_frect.size[1]):
                if trajectory['position'] - (self.paddle_frect.pos[1] + i) < trajectory['time']:
                    possibilities.append(i)
        return possibilities

    def get_optimal_target(self, possible_collision_positions, trajectory_position, paddle_frect, other_paddle_frect,
                           paddle_edge, other_paddle_edge):
        """
        Return the best point along the paddle with which to hit the ball
        """
        best_position = paddle_frect.size[1] / 2
        best_score = 0
        for possibility in possible_collision_positions:
            projected_vel = self.get_projected_vel(possibility, trajectory_position)
            predicted_trajectory = self.get_ball_trajectory(projected_vel, (paddle_edge, trajectory_position),
                                                            other_paddle_edge)
            score = abs(
                predicted_trajectory['position'] - (other_paddle_frect.pos[1] + other_paddle_frect.size[1] / 2)) - \
                    predicted_trajectory['time']
            if score > best_score:
                best_position = possibility
                best_score = score
        return paddle_frect.pos[1] + best_position