# rocket-league-gym-sim
A version of [RLGym](https://www.rlgym.org) for use with the [RocketSim](https://github.com/ZealanL/RocketSim) simulator.

## FOREWORD
This project is a TEMPORARY STOP-GAP to use RocketSim while RLGym 2.0 is in development. I provide no guarantees that it is bug-free or that I will not make breaking changes to this project in the future.

This project attempts to build [python bindings](https://github.com/uservar/pyrocketsim/tree/dev) for RocketSim from a separate project, which will require c++20 build tools and cmake > 3.13. Further, you will need to acquire assets from a copy of Rocket League that you own with an asset dumper. I will not walk you through this process. The necessary links and basic instructions are listed below. If you cannot follow those, don't bother me.

## INSTALLATION
1. You will need c++20 build tools and cmake > 3.13
2. Install this project with pip via `pip install git+https://github.com/AechPro/rocket-league-gym-sim@main`
3. Build and run the [asset dumper](https://github.com/ZealanL/RLArenaCollisionDumper)
4. Move the dumped assets to the top level of your project directory

## USAGE
This project acts as a drop-in replacement for RLGym and can be used in exactly the same way. Barring the changed hyper-parameters listed below, you can replace every instance of `rlgym` with `rlgym_sim` (or simply `import rlgym_sim as rlgym`) and your existing RLGym code should work. 

All variables having to do with the game client have been removed from the `make` function. For example, `rlgym_sim.make(use_injector=True)` will fail because there is no injector. The following is a list of all removed `make` variables:
- `use_injector`
- `auto_minimize`
- `force_paging`
- `launch_preference`
- `raise_on_crash`
- `self_play`

Additionally, there is a new hyper-parameter that can be passed to `rlgym_sim.make` called `copy_gamestate_every_step`. Leave this alone for the default behavior, but if you are careful to copy all relevant `GameState`, `PlayerData`, and `PhysicsObject` information between calls to `env.step` in your configuration objects when you need to track things over time, setting `copy_gamestate_every_step` to `True` will significantly speed up the environment.

## KNOWN ISSUES
- Setting the game speed, gravity, and boost consumption values through `rlgym.update_settings()` does not work and is not supported.
- A variety of classes in `rlgym_utils` such as `SB3MultipleInstanceEnv` imports the `rlgym` library to build environments, so you will need to replace those imports yourself and remove the misc launch options listed above if you want to use SB3 with `rlgym_sim`. Note also that `SB3MultipleInstanceEnv` waits 60 seconds between launching clients by default because multiple Rocket League clients will break each other if launched simultaneously. This is not the case with RocketSim, so you can remove that delay.
- the `PlayerData` objects do not track `match_goals`, `match_saves`, `match_shots`, `match_demolishes`, or `boost_pickups` yet. 
- Maybe some kind of scoring callback issue?
- "things aren't right"