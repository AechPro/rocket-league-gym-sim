# rocket-league-gym-sim
A version of [RLGym](https://www.rlgym.org) for use with the [RocketSim](https://github.com/ZealanL/RocketSim) simulator.

## FOREWORD
This project is a TEMPORARY STOP-GAP to use RocketSim while RLGym 2.0 is in development. I provide no guarantees that it is bug-free or that I will not make breaking changes to this project in the future.

This project requires you to install [python bindings](https://github.com/mtheall/RocketSim/tree/python-dev) for RocketSim from a separate project, which will require c++20 build tools. Further, you will need to acquire assets from a copy of Rocket League that you own with an asset dumper. I will not walk you through this process. The necessary links and basic instructions are listed below. If you cannot follow those, don't bother me.

## INSTALLATION
1. You will need c++20 build tools
2. Build RocketSim and install the Python bindings via `pip install git+https://github.com/mtheall/RocketSim@1710e5d462a33bc3be3b0c8f52f7d6132e5d5257` 
3. Install this project with pip via `pip install git+https://github.com/AechPro/rocket-league-gym-sim@main`
4. Build and run the [asset dumper](https://github.com/ZealanL/RLArenaCollisionDumper)
5. Move the dumped assets to the top level of your project directory

## USAGE
This project acts as a drop-in replacement for RLGym and can be used in exactly the same way. Barring the changed variables listed below, you can replace every instance of `rlgym` with `rlgym_sim` (or simply `import rlgym_sim as rlgym`) and your existing RLGym code should work. 

All variables having to do with the game client have been removed from the `make` function. For example, `rlgym_sim.make(use_injector=True)` will fail because there is no injector. The following is a list of all removed `make` variables:
- `use_injector`
- `game_speed`
- `auto_minimize`
- `force_paging`
- `launch_preference`
- `raise_on_crash`
- `self_play`

Thanks to the flexibility of the simulator, the following additional variables have been added as arguments to `make`:
- `copy_gamestate_every_step`: Leave this alone for the default behavior. Setting this to `True` will no longer return a new `GameState` object at every call to `step`, which is substantially faster. However, if you need to track data from the game state or its member variables over time, you will need to manually copy all relevant `GameState`, `PlayerData`, and `PhysicsObject` data at each `step`.
- `dodge_deadzone`: Sets the threshold value that `pitch` must meet in order for a dodge to occur when jumping in the air.

## KNOWN ISSUES
- Setting the gravity and boost consumption values through `rlgym.update_settings()` does not work and is not supported.
- A variety of classes in `rlgym_utils` such as `SB3MultipleInstanceEnv` imports the `rlgym` library to build environments, so you will need to replace those imports yourself and remove the misc launch options listed above if you want to use SB3 with `rlgym_sim`. Note also that `SB3MultipleInstanceEnv` waits 60 seconds between launching clients by default because multiple Rocket League clients will break each other if launched simultaneously. This is not the case with RocketSim, so you can remove that delay.
- the `PlayerData` objects do not track `match_saves` or `match_shots` yet.
