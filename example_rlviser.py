import time

import rlgym_sim

# Rocket League runs at 120 ticks per second
# 1 / 240 will make the game run at 2x speed
DT = 1 / 120

env = rlgym_sim.make(spawn_opponents=True)

while True:
    obs = env.reset()

    done = False
    steps = 0
    ep_reward = 0
    t0 = time.time()
    starttime = time.time()
    while not done:
        actions_1 = env.action_space.sample()
        actions_2 = env.action_space.sample()
        actions = [actions_1, actions_2]
        new_obs, reward, done, state = env.step(actions, dt=DT)
        ep_reward += reward[0]
        steps += 1

    length = time.time() - t0
    print("Step time: {:1.5f} | Episode time: {:.2f} | Episode Reward: {:.2f}".format(length / steps, length, ep_reward))
