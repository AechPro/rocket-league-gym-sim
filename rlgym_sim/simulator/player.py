from rlgym_sim.utils.gamestates import PlayerData, PhysicsObject
from rlgym_sim.utils import common_values
from rlgym_sim.utils import math
import RocketSim as rsim
import numpy as np


class Player(object):
    JUMP_TIMER_SECONDS = 1.25
    def __init__(self, car, spectator_id):
        self.id = car.id
        self.car = car
        self.car_vec_mem = np.zeros((6,3))
        self.rot_mat_mem = np.zeros((3,3))
        self.inverted_quaternion = np.zeros(4)

        player_data = PlayerData()
        if car.team == rsim.Team.BLUE:
            player_data.team_num = common_values.BLUE_TEAM
        else:
            player_data.team_num = common_values.ORANGE_TEAM

        player_data.car_id = spectator_id
        self.data = player_data

    def update(self, gym_data):
        car_state = self.car.get_state()
        self.id = gym_data[0][0]
        self.data.decode(gym_data)
        self.data.has_jump = not car_state.has_jumped
        self.data.has_flip = car_state.air_time_since_jump < Player.JUMP_TIMER_SECONDS and not (car_state.has_flipped or car_state.has_double_jumped)

