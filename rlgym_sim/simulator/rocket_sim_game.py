import RocketSim as rsim
from rlgym_sim.utils.gamestates import GameState, PhysicsObject
from rlgym_sim.utils import common_values, math
from rlgym_sim.simulator import Player
import numpy as np


class RocketSimGame(object):
    DEFAULT_BALL_STATE = rsim.BallState()

    def __init__(self, match, copy_gamestate=True, dodge_deadzone=0.5):
        self.copy_gamestate = copy_gamestate
        self.arena = rsim.Arena(rsim.GameMode.SOCCAR)
        self.team_size = match._team_size
        self.tick_skip = match._tick_skip
        self.spawn_opponents = match._spawn_opponents
        self.n_agents = self.team_size*2 if self.spawn_opponents else self.team_size
        self.dodge_deadzone = dodge_deadzone

        self.players = {}
        self.boost_index_map = {}
        self.car_index_map = {}
        self.spectator_to_car_id_map = {}
        self.car_id_to_spectator_map = {}
        self.cars = []

        self.blue_score = 0
        self.orange_score = 0

        self.gamestate = GameState()
        self.new_game(self.tick_skip, self.team_size, self.spawn_opponents)

    def new_game(self, tick_skip, team_size, spawn_opponents):
        for car in self.arena.get_cars():
            self.arena.remove_car(car)

        self.spectator_to_car_id_map.clear()
        self.car_id_to_spectator_map.clear()

        self.team_size = team_size
        self.tick_skip = tick_skip
        self.spawn_opponents = spawn_opponents
        self.n_agents = team_size*2 if spawn_opponents else team_size

        # Two loops here so blue team is always the first half of the list
        blue_spectator_ids = [i+1 for i in range(team_size)]
        blue_idx = 0
        for i in range(team_size):
            cfg = rsim.CarConfig(rsim.CarConfig.OCTANE)
            cfg.dodge_deadzone = self.dodge_deadzone
            car = self.arena.add_car(rsim.Team.BLUE, cfg)
            car_id = car.id
            self.car_id_to_spectator_map[car_id] = blue_spectator_ids[blue_idx]
            self.spectator_to_car_id_map[blue_spectator_ids[blue_idx]] = car_id
            blue_idx += 1

        if spawn_opponents:
            orange_spectator_ids = [5 + i for i in range(team_size)]
            orange_idx = 0
            for i in range(team_size):
                cfg = rsim.CarConfig(rsim.CarConfig.OCTANE)
                cfg.dodge_deadzone = self.dodge_deadzone
                car = self.arena.add_car(rsim.Team.ORANGE,  cfg)
                car_id = car.id
                self.car_id_to_spectator_map[car_id] = orange_spectator_ids[orange_idx]
                self.spectator_to_car_id_map[orange_spectator_ids[orange_idx]] = car_id
                orange_idx += 1

        self.players.clear()
        cars = self.arena.get_cars()
        for car in cars:
            self.players[car.id] = Player(car, self.car_id_to_spectator_map[car.id])

        self.cars = cars
        self._build_index_maps()

    def reset(self, state_vals):
        player_len = 14
        state_vals = np.asarray(state_vals)
        ball_state = rsim.BallState()
        ball_state.pos = rsim.Vec(state_vals[0], state_vals[1], state_vals[2])
        ball_state.vel = rsim.Vec(state_vals[3], state_vals[4], state_vals[5])
        ball_state.ang_vel = rsim.Vec(state_vals[6], state_vals[7], state_vals[8])
        self.arena.ball.set_state(ball_state)

        idx = 9
        n_players = (len(state_vals) - idx) // player_len

        if n_players != self.n_agents:
            self.new_game(self.tick_skip, n_players//2 if self.spawn_opponents else n_players, self.spawn_opponents)

        self.cars = self.arena.get_cars()
        cars = self.cars

        if n_players > 0:
            for i in range(n_players):
                start = idx + i*player_len
                stop = start + player_len
                player_state_vals = state_vals[start:stop] #id, pos, lv, av, euler, boost

                spectator_id = int(player_state_vals[0])
                car_id = self.spectator_to_car_id_map[spectator_id]
                car = cars[self.car_index_map[car_id]]
                car_state = rsim.CarState()
                car_state.pos = rsim.Vec(player_state_vals[1], player_state_vals[2], player_state_vals[3])
                car_state.vel = rsim.Vec(player_state_vals[4], player_state_vals[5], player_state_vals[6])
                car_state.ang_vel = rsim.Vec(player_state_vals[7], player_state_vals[8], player_state_vals[9])

                mtx = math.euler_to_rotation(player_state_vals[10:13])
                rot = rsim.RotMat(*mtx.transpose().flatten()) # Bullet is row-major.

                car_state.rot_mat = rot
                car_state.boost = player_state_vals[-1]*100
                car.set_state(car_state)
                car.set_controls(rsim.CarControls())

        for pad in self.arena.get_boost_pads():
            pad.set_state(rsim.BoostPadState())

        return self._build_gamestate()

    def step(self, controls):
        self._set_controls(controls)

        gamestate = self._build_gamestate()
        self.arena.step(self.tick_skip)

        return gamestate

    def _build_gamestate(self):
        players = self.players
        if self.copy_gamestate:
            gamestate = GameState()
        else:
            gamestate = self.gamestate
        arena_state = self.arena.get_gym_state()
        gamestate.players = []

        game_data = arena_state[0]
        gamestate.game_type = game_data[0]
        gamestate.last_touch = game_data[1]

        blue_score, orange_score = game_data[2], game_data[3]
        gamestate.blue_score = blue_score
        gamestate.orange_score = orange_score

        # Reset ball to kickoff position on goal to prevent goal counter from increasing more than once.
        if blue_score != self.blue_score or orange_score != self.orange_score:
            self.blue_score = blue_score
            self.orange_score = orange_score
            self.arena.ball.set_state(RocketSimGame.DEFAULT_BALL_STATE)

        boostpad_data = arena_state[1]
        gamestate.boost_pads = boostpad_data[0]
        gamestate.inverted_boost_pads = boostpad_data[1]

        ball_data = arena_state[2][0]
        inverted_ball_data = arena_state[2][1]
        gamestate.ball.decode_data(ball_data)
        gamestate.inverted_ball.decode_data(inverted_ball_data)
        for i in range(3, len(arena_state)):
            player_data = arena_state[i]
            player = players[int(player_data[0][0])]
            player.update(player_data)
            gamestate.players.append(player.data)

        return gamestate

    def _set_controls(self, controls):
        cars = self.cars
        car_index_map = self.car_index_map
        spectator_map = self.spectator_to_car_id_map
        n = 9

        for i in range(self.n_agents):
            car_controls = rsim.CarControls()
            spectator_id = controls[i*n]
            car_id = spectator_map[spectator_id]
            cars_idx = car_index_map[car_id]

            car_controls.throttle = controls[i*n+1]
            car_controls.steer = controls[i*n+2]
            car_controls.pitch = controls[i*n+3]
            car_controls.yaw = controls[i*n+4]
            car_controls.roll = controls[i*n+5]
            car_controls.jump = controls[i*n+6] == 1
            car_controls.boost = controls[i*n+7] == 1
            car_controls.handbrake = controls[i*n+8] == 1

            cars[cars_idx].set_controls(car_controls)

    def _build_index_maps(self):
        pads = self.arena.get_boost_pads()
        self.boost_index_map.clear()
        self.car_index_map.clear()

        cars = self.arena.get_cars()
        for i in range(len(cars)):
            self.car_index_map[cars[i].id] = i

        for loc in common_values.BOOST_LOCATIONS:
            for i in range(len(pads)):
                pos = pads[i].get_pos()
                if round(pos.x) == loc[0] and round(pos.y) == loc[1]:
                    self.boost_index_map[loc] = i

                    # Uncomment to compare order of boostpad array from the simulator to the expected order in RLGym.
                    # print(loc,"->",i," | ",common_values.BOOST_LOCATIONS[i])
                    break