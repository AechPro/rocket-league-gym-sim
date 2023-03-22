# rocket-league-gym-sim
A version of [RLGym](https://github.com/lucas-emery/rocket-league-gym) for use with the RocketSim simulator.

## FOREWORD
This project is a TEMPORARY STOP-GAP to use [RocketSim](https://github.com/ZealanL/RocketSim) while RLGym 2.0 is in development. I provide no guarantees that it is bug-free or that I will not make breaking changes to this project in the future. 

Installing this project requires you to build Python bindings from a separate project, and acquire assets from a copy of the game you own with another project. I will not walk you through this process. The necessary links and basic instructions are listed below. If you cannot follow those, don't bother me.

## INSTALLATION
1. Clone and build the [Python bindings](https://github.com/uservar/pyrocketsim/tree/dev). You will need c++20 build tools for this.
2. Build and run the [asset dumper](https://github.com/ZealanL/RLArenaCollisionDumper)
3. Move the dumped assets to the top level of your project directory
4. Clone and install this project with pip

## USAGE
This project acts as a drop-in replacement for RLGym, and can be used in exactly the same way. However, note that all variables having to do with the game client have been removed from the `make` function. For example, `rlgym_sim.make(use_injector=True)` will fail because there is no injector. The following is a list of all removed `make` variables:
- `use_injector`
- `auto_minimize`
- `force_paging`
- `launch_preference`
- `raise_on_crash`

Otherwise you can replace every instance of `rlgym` with `rlgym_sim` (or simply `import rlgym_sim as rlgym`) and your existing RLGym code should work.

## KNOWN ISSUES
- Setting the game speed, gravity, and boost consumption values through `rlgym.update_settings()` does not work and is not supported.
- A variety of classes in `rlgym_utils` such as `SB3MultipleInstanceEnv` imports the `rlgym` library to build environments, so you will need to replace those imports yourself and remove the misc launch options listed above if you want to use SB3 with `rlgym_sim`. Note also that `SB3MultipleInstanceEnv` waits 60 seconds between launching clients by default because multiple Rocket League clients will break each other if launched simultaneously. This is not the case with RocketSim, so you can remove that delay.
- the `PlayerData` objects do not track `match_goals`, `match_saves`, `match_shots`, `match_demolishes`, or `boost_pickups` yet.
