import os
from typing import List
from warnings import warn

from rlgym_sim.envs import Match
from rlgym_sim.utils.terminal_conditions import common_conditions
from rlgym_sim.utils.reward_functions import DefaultReward
from rlgym_sim.utils.obs_builders import DefaultObs
from rlgym_sim.utils.action_parsers import DefaultAction
from rlgym_sim.utils.state_setters import DefaultState


def make(game_speed: int = 100,
         tick_skip: int = 8,
         spawn_opponents: bool = False,
         self_play = None,
         team_size: int = 1,
         gravity: float = 1,
         boost_consumption: float = 1,
         terminal_conditions: List[object] = (common_conditions.TimeoutCondition(225), common_conditions.GoalScoredCondition()),
         reward_fn: object = DefaultReward(),
         obs_builder: object = DefaultObs(),
         action_parser: object = DefaultAction(),
         state_setter: object = DefaultState()):
    """
    :param game_speed: The speed the physics will run at, leave it at 100 unless your game can't run at over 240fps
    :param tick_skip: The amount of physics ticks your action will be repeated for
    :param spawn_opponents: Whether you want opponents or not
    :param team_size: Cars per team
    :param gravity: Game gravity, 1 is normal gravity
    :param boost_consumption: Car boost consumption rate, 1 is normal consumption
    :param terminal_conditions: List of terminal condition objects (rlgym_sim.utils.TerminalCondition)
    :param reward_fn: Reward function object (rlgym_sim.utils.RewardFunction)
    :param obs_builder: Observation builder object (rlgym_sim.utils.ObsBuilder)
    :param action_parser: Action parser object (rlgym_sim.utils.ActionParser)
    :param state_setter: State Setter object (rlgym_sim.utils.StateSetter)
    :return: Gym object
    [1]: https://www.tomshardware.com/news/how-to-manage-virtual-memory-pagefile-windows-10,36929.html
    """

    # TODO: Remove in v1.3
    if self_play is not None:
        warn('self_play argument is deprecated and will be removed in future rlgym versions.\nPlease use spawn_opponents instead', DeprecationWarning, stacklevel=2)
        spawn_opponents = self_play

    # Imports are inside the function because setup fails otherwise (Missing win32file)
    from rlgym_sim.gym import Gym
    from rlgym_sim.version import print_current_release_notes

    print_current_release_notes()

    match = Match(reward_function=reward_fn,
                  terminal_conditions=terminal_conditions,
                  obs_builder=obs_builder,
                  action_parser=action_parser,
                  state_setter=state_setter,
                  team_size=team_size,
                  tick_skip=tick_skip,
                  game_speed=game_speed,
                  gravity=gravity,
                  boost_consumption=boost_consumption,
                  spawn_opponents=spawn_opponents)

    return Gym(match)
