from rlgym_sim.envs import Match
from rlgym_sim.gym import Gym
from rlgym_sim.utils import terminal_conditions as terminal_conditions
from rlgym_sim.utils.action_parsers import ActionParser, DefaultAction
from rlgym_sim.utils.obs_builders import DefaultObs, ObsBuilder
from rlgym_sim.utils.reward_functions import DefaultReward, RewardFunction
from rlgym_sim.utils.state_setters import DefaultState, StateSetter
from rlgym_sim.utils.terminal_conditions import common_conditions


def make(
    tick_skip: int = 8,
    spawn_opponents: bool = False,
    team_size: int = 1,
    gravity: float = 1,
    boost_consumption: float = 1,
    copy_gamestate_every_step: bool = True,
    dodge_deadzone: float = 0.8,
    terminal_conditions: tuple[terminal_conditions.TerminalCondition, ...] = (
        common_conditions.TimeoutCondition(225),
        common_conditions.GoalScoredCondition(),
    ),
    reward_fn: RewardFunction = DefaultReward(),
    obs_builder: ObsBuilder = DefaultObs(),
    action_parser: ActionParser = DefaultAction(),
    state_setter: StateSetter = DefaultState(),
):
    """
    :param tick_skip: The amount of physics ticks your action will be repeated for
    :param spawn_opponents: Whether you want opponents or not
    :param team_size: Cars per team
    :param gravity: Game gravity, 1 is normal gravity -- CURRENTLY UNSUPPORTED
    :param boost_consumption: Car boost consumption rate, 1 is normal consumption -- CURRENTLY UNSUPPORTED
    :param dodge_deadzone: Dodge deadzone setting. Pitch must be >= this value while in the air and pressing jump to flip.

    :param copy_gamestate_every_step: Whether a new instance of a GameState object should be returned after every call
    to env.step(). Setting this to True is significantly slower but will allow users to compare GameStates between steps
    without manually copying the state inside their configuration objects. Setting this to False will make env.step()
    much faster, but users will need to carefully copy every value they want to track in the GameState, PlayerData, and
    PhysicsObject objects across steps.

    :param terminal_conditions: List of terminal condition objects (rlgym_sim.utils.TerminalCondition)
    :param reward_fn: Reward function object (rlgym_sim.utils.RewardFunction)
    :param obs_builder: Observation builder object (rlgym_sim.utils.ObsBuilder)
    :param action_parser: Action parser object (rlgym_sim.utils.ActionParser)
    :param state_setter: State Setter object (rlgym_sim.utils.StateSetter)
    :return: Gym object
    """  # noqa: E501

    match = Match(
        reward_function=reward_fn,
        terminal_conditions=terminal_conditions,
        obs_builder=obs_builder,
        action_parser=action_parser,
        state_setter=state_setter,
        team_size=team_size,
        spawn_opponents=spawn_opponents,
    )

    return Gym(
        match,
        tick_skip=tick_skip,
        gravity=gravity,
        boost_consumption=boost_consumption,
        copy_gamestate_every_step=copy_gamestate_every_step,
        dodge_deadzone=dodge_deadzone,
    )
