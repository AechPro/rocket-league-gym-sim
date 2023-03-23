import pyrocketsim as rsim
from rlgym_sim.utils.gamestates import GameState, PhysicsObject
from rlgym_sim.utils import common_values, math
from rlgym_sim.simulator import Player
import numpy as np


class RocketSimGame(object):
    GOAL_THRESHOLD_Y = 5121.75 + 91.25
    DEFAULT_BALL_STATE = rsim.BallState()
    INVERT_VEC = np.array([-1, -1, 1])

    def __init__(self, match, copy_gamestate=True):
        self.copy_gamestate = copy_gamestate
        self.arena = rsim.Arena(rsim.SOCCAR)
        self.blue_score = 0
        self.orange_score = 0
        self.team_size = match._team_size
        self.tick_skip = match._tick_skip
        self.spawn_opponents = match._spawn_opponents
        self.n_agents = self.team_size*2 if self.spawn_opponents else self.team_size

        self.players = {}
        self.boost_index_map = {}
        self.car_index_map = {}
        self.cars = []
        self.ball_vec_mem = np.zeros((6,3))

        self.gamestate = GameState()

        self.ball = PhysicsObject()
        self.inverted_ball = PhysicsObject()

        self.gamestate.ball = self.ball
        self.gamestate.inverted_ball = self.inverted_ball
        self.gamestate.boost_pads = np.asarray([1 for _ in range(34)])
        self.gamestate.inverted_boost_pads = np.asarray([1 for _ in range(34)])
        self.new_game(self.tick_skip, self.team_size, self.spawn_opponents)
        self.arena.set_goal_score_call_back(self._goal_callback)

    def new_game(self, tick_skip, team_size, spawn_opponents):
        for car in self.arena.get_cars():
            self.arena.remove_car(car)

        self.blue_score = 0
        self.orange_score = 0
        self.team_size = team_size
        self.tick_skip = tick_skip
        self.spawn_opponents = spawn_opponents
        self.n_agents = team_size*2 if spawn_opponents else team_size

        # Two loops here so blue team is always the first half of the list
        for i in range(team_size):
            self.arena.add_car(rsim.BLUE, rsim.OCTANE)

        if spawn_opponents:
            for i in range(team_size):
                self.arena.add_car(rsim.ORANGE, rsim.OCTANE)

        self.players.clear()
        for car in self.arena.get_cars():
            self.players[car.id] = Player(car)

        self._build_index_maps()

    def reset(self, state_vals):
        player_len = 14
        state_vals = np.asarray(state_vals)
        ball_state = rsim.BallState()
        ball_state.pos = rsim.Vec(state_vals[0], state_vals[1], state_vals[2])
        ball_state.vel = rsim.Vec(state_vals[3], state_vals[4], state_vals[5])
        ball_state.ang_vel = rsim.Vec(state_vals[6], state_vals[7], state_vals[8])
        self.arena.ball.set_state(ball_state)
        rsim.Vec()

        idx = 9
        n_players = (len(state_vals) - idx) // player_len
        if n_players != self.n_agents:
            self.new_game(self.tick_skip, n_players//2, self.spawn_opponents)

        cars = self.arena.get_cars()
        offset = min(self.car_index_map.keys()) - 1
        for i in range(n_players):
            start = idx + i*player_len
            stop = start + player_len
            player_state_vals = state_vals[start:stop] #id, pos, lv, av, euler, boost

            spectator_id = int(player_state_vals[0])
            if spectator_id >= 5:
                converted_player_id = spectator_id - 4 + self.team_size
            else:
                converted_player_id = spectator_id
            converted_player_id = offset + converted_player_id

            car = cars[self.car_index_map[converted_player_id]]
            car_state = rsim.CarState()
            car_state.pos = rsim.Vec(player_state_vals[1], player_state_vals[2], player_state_vals[3])
            car_state.vel = rsim.Vec(player_state_vals[4], player_state_vals[5], player_state_vals[6])
            car_state.ang_vel = rsim.Vec(player_state_vals[7], player_state_vals[8], player_state_vals[9])

            mtx = math.euler_to_rotation(player_state_vals[10:13])
            rot = rsim.RotMat(forward=rsim.Vec(*mtx[:, 0]),
                              right=rsim.Vec(*mtx[:, 1]),
                              up=rsim.Vec(*mtx[:, 2]))

            car_state.rot_mat = rot
            car_state.boost = player_state_vals[-1]
            car.set_state(car_state)
            car.set_controls(rsim.CarControls())

        for pad in self.arena.get_boost_pads():
            pad.set_state(rsim.BoostPadState())

        self.cars = cars

        return self._build_gamestate()

    def step(self, controls):
        self._set_controls(controls)

        gamestate = self._build_gamestate()
        self.arena.step(self.tick_skip)

        self.cars = self.arena.get_cars()
        return gamestate

    def _build_gamestate(self):
        gamestate = self.gamestate
        gamestate.players = []
        gamestate.blue_score = self.blue_score
        gamestate.orange_score = self.orange_score

        boostpads = gamestate.boost_pads
        inverted_boostpads = gamestate.inverted_boost_pads

        ball = self.ball
        inverted_ball = self.inverted_ball
        ball_vec_mem = self.ball_vec_mem

        for car in self.cars:
            player = self.players[car.id]
            player.update(car)
            gamestate.players.append(player.data)

        ball_state = self.arena.ball.get_state()
        ball_pos = ball_state.pos
        ball_vel = ball_state.vel
        ball_ang_vel = ball_state.ang_vel
        ball_vec_mem[0, 0] = ball_pos.x
        ball_vec_mem[0, 1] = ball_pos.y
        ball_vec_mem[0, 2] = ball_pos.z

        ball_vec_mem[1, 0] = ball_vel.x
        ball_vec_mem[1, 1] = ball_vel.y
        ball_vec_mem[1, 2] = ball_vel.z

        ball_vec_mem[2, 0] = ball_ang_vel.x
        ball_vec_mem[2, 1] = ball_ang_vel.y
        ball_vec_mem[2, 2] = ball_ang_vel.z

        ball_vec_mem[3, 0] = -ball_vec_mem[0, 0]
        ball_vec_mem[3, 1] = -ball_vec_mem[0, 1]
        ball_vec_mem[3, 2] = ball_vec_mem[0, 2]

        ball_vec_mem[4, 0] = -ball_vec_mem[1, 0]
        ball_vec_mem[4, 1] = -ball_vec_mem[1, 1]
        ball_vec_mem[4, 2] =  ball_vec_mem[1, 2]

        ball_vec_mem[5, 0] = -ball_vec_mem[2, 0]
        ball_vec_mem[5, 1] = -ball_vec_mem[2, 1]
        ball_vec_mem[5, 2] = ball_vec_mem[2, 2]

        ball.position = ball_vec_mem[0]
        ball.linear_velocity = ball_vec_mem[1]
        ball.angular_velocity = ball_vec_mem[2]
        inverted_ball.position = ball_vec_mem[3]
        inverted_ball.linear_velocity = ball_vec_mem[4]
        inverted_ball.angular_velocity = ball_vec_mem[5]

        pads = self.arena.get_boost_pads()
        locs = common_values.BOOST_LOCATIONS
        boost_index_map = self.boost_index_map
        for i in range(34):
            pad_active = pads[boost_index_map[locs[i]]].get_state().is_active
            inverted_boostpads[-(i+1)] = pad_active
            boostpads[i] = pad_active

        if self.copy_gamestate:
            return GameState(other=gamestate)

        return gamestate

    def _set_controls(self, controls):
        players = self.players
        cars = self.cars
        car_index_map = self.car_index_map
        n = 9

        for i in range(self.n_agents):
            car_controls = rsim.CarControls()
            car_id = players[controls[i*n]].id
            cars_idx = car_index_map[car_id]

            car_controls.throttle = controls[i*n+1]
            car_controls.steer = controls[i*n+2]
            car_controls.pitch = controls[i*n+3]
            car_controls.yaw = controls[i*n+4]
            car_controls.roll = controls[i*n+5]
            car_controls.jump = controls[i*n+6]
            car_controls.boost = controls[i*n+7]
            car_controls.handbrake = controls[i*n+8]

            cars[cars_idx].set_controls(car_controls)

    def _goal_callback(self, arena, scoring_team):
        self.arena.ball.set_state(RocketSimGame.DEFAULT_BALL_STATE)

        if scoring_team == rsim.BLUE:
            self.blue_score += 1
        else:
            self.orange_score += 1

    def _build_index_maps(self):
        pads = self.arena.get_boost_pads()
        self.boost_index_map.clear()
        self.car_index_map.clear()

        cars = self.arena.get_cars()
        for i in range(len(cars)):
            self.car_index_map[cars[i].id] = i

        for loc in common_values.BOOST_LOCATIONS:
            for i in range(len(pads)):
                pos = pads[i].pos
                if round(pos[0]) == loc[0] and round(pos[1]) == loc[1]:
                    self.boost_index_map[loc] = i
                    break
