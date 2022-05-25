import simenv as sm
import simenv.assets.utils as utils
import os, time
from simenv.rl_env import RLEnv
import matplotlib.pyplot as plt
import numpy as np


def create_tmaze():
    scene = sm.Scene(engine="Unity")


    scene += sm.Light(
        name="sun", position=[0, 20, 0], rotation=utils.quat_from_degrees(60, -30, 0), intensity=3.5
    )
    scene += sm.Cube(name="floor", position=[0, -0.05, 0], scaling=[100, 0.1, 100])
    scene += sm.Cube(name="wall1", position=[-1, 0.5, 0], scaling=[0.1, 1, 5.1])
    scene += sm.Cube(name="wall2", position=[1, 0.5, 0], scaling=[0.1, 1, 5.1])
    scene += sm.Cube(name="wall3", position=[0, 0.5, 4.5], scaling=[5.9, 1, 0.1])
    scene += sm.Cube(name="wall4", position=[-2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
    scene += sm.Cube(name="wall5", position=[2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
    scene += sm.Cube(name="wall6", position=[-3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
    scene += sm.Cube(name="wall7", position=[3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
    scene += sm.Cube(name="wall8", position=[0, 0.5, -2.5], scaling=[1.9, 1, 0.1])


    agent = sm.RLAgent(name="agent", turn_speed=5.0,  position=[0, 0, 0.0], rotation=utils.quat_from_degrees(0, -180, 0))
    scene += sm.Sphere(name="collectable", position=[2, 0.5, 3.4], radius=0.3)

    reward_function = reward_function = sm.RLAgentRewardFunction(
        function="dense",
        entity1="agent",
        entity2="collectable",
        distance_metric="euclidean"
    )

    reward_function2 = sm.RLAgentRewardFunction(
        function="sparse",
        entity1="agent",
        entity2="collectable",
        distance_metric="euclidean",
        threshold=3.0,
        is_terminal=True
    )
    agent.add_reward_function(reward_function)
    agent.add_reward_function(reward_function2)
    scene += agent

    return scene


scene = create_tmaze()

PLOT=True

scene.show()
env = RLEnv(scene)


if PLOT:
    plt.ion()
    fig1, ax1 = plt.subplots()
    dummy_obs = np.zeros(shape=(scene.agent.camera_height, scene.agent.camera_width, 3), dtype=np.uint8)
    axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)


for episode in range(5):
    obs = env.reset()

    done = False
    i=0
    while not done:
        print(i)
        i += 1
        action = env.action_space.sample()
        if type(action) == int: # discrete are ints, continuous are numpy arrays
            action = [action]
        else:
            action = action.tolist()

        obs, reward, done, info = env.step(action)
        print(reward, done, info)

        if PLOT:
            axim1.set_data(obs)
            fig1.canvas.flush_events()
        
        #time.sleep(0.1)

    


env.close()