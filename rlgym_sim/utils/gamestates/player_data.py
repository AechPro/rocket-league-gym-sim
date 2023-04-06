"""
A class containing all data about a player in the game.
"""

from rlgym_sim.utils.gamestates import PhysicsObject


class PlayerData(object):
    def __init__(self):
        self.car_id: int = -1
        self.team_num: int = -1
        self.match_goals: int = -1
        self.match_saves: int = -1
        self.match_shots: int = -1
        self.match_demolishes: int = -1
        self.boost_pickups: int = -1
        self.is_demoed: bool = False
        self.on_ground: bool = False
        self.ball_touched: bool = False
        self.has_jump: bool = False
        self.has_flip: bool = False
        self.boost_amount: float = -1
        self.car_data: PhysicsObject = PhysicsObject()
        self.inverted_car_data: PhysicsObject = PhysicsObject()

    def copy(self, other):
        self.car_id = other.car_id
        self.team_num = other.team_num
        self.match_goals = other.match_goals
        self.match_saves = other.match_saves
        self.match_shots = other.match_shots
        self.match_demolishes = other.match_demolishes
        self.boost_pickups = other.boost_pickups
        self.is_demoed = other.is_demoed
        self.on_ground = other.on_ground
        self.ball_touched = other.ball_touched
        self.has_jump = other.has_jump
        self.has_flip = other.has_flip
        self.boost_amount = other.boost_amount
        self.car_data.copy(other.car_data)
        self.inverted_car_data.copy(other.inverted_car_data)


    def decode(self, car_data):
        self.team_num = car_data[0][1]
        self.match_goals = car_data[0][2]
        self.match_saves = car_data[0][3]
        self.match_shots = car_data[0][4]
        self.match_demolishes = car_data[0][5]
        self.boost_pickups = car_data[0][6]
        self.is_demoed = car_data[0][7] == 1.0
        self.on_ground = car_data[0][8] == 1.0
        self.ball_touched = car_data[0][9] == 1.0
        self.boost_amount = car_data[0][10]/100

        self.car_data.decode_data(car_data[0][11:36])
        self.inverted_car_data.decode_data(car_data[1][11:36])

    def __str__(self):
        output = "****PLAYER DATA OBJECT****\n" \
                 "Match Goals: {}\n" \
                 "Match Saves: {}\n" \
                 "Match Shots: {}\n" \
                 "Match Demolishes: {}\n" \
                 "Boost Pickups: {}\n" \
                 "Is Alive: {}\n" \
                 "On Ground: {}\n" \
                 "Ball Touched: {}\n" \
                 "Has Jump: {}\n" \
                 "Has Flip: {}\n" \
                 "Boost Amount: {}\n" \
                 "Car Data: {}\n" \
                 "Inverted Car Data: {}"\
            .format(self.match_goals,
                    self.match_saves,
                    self.match_shots,
                    self.match_demolishes,
                    self.boost_pickups,
                    not self.is_demoed,
                    self.on_ground,
                    self.ball_touched,
                    self.has_jump,
                    self.has_flip,
                    self.boost_amount,
                    self.car_data,
                    self.inverted_car_data)
        return output
