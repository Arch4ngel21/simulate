import argparse
import math
import random
import time
from collections import defaultdict

import numpy as np
from stable_baselines3 import PPO

import simenv as sm
from simenv.assets.object import ProcGenPrimsMaze3D
from simenv.assets.sensors import RaycastSensor, StateSensor

# Lint as: python3
from simenv.scene import Scene


def generate_map(index):
    maze_width = 3
    maze_depth = 3
    n_objects = 1
    maze = ProcGenPrimsMaze3D(maze_width, maze_depth, wall_material=sm.Material.YELLOW)
    maze += sm.Box(
        position=[0, 0, 0],
        bounds=[0.0, maze_width, 0, 0.1, 0.0, maze_depth],
        material=sm.Material.BLUE,
        with_collider=True,
    )
    actor_position = [math.floor(maze_width / 2.0) + 0.5, 0.5, math.floor(maze_depth / 2.0) + 0.5]

    actor = sm.EgocentricCameraActor(position=actor_position)
    actor += StateSensor(actor, maze)
    actor += RaycastSensor()

    maze += actor

    for r in range(n_objects):
        position = [random.randint(0, maze_width - 1) + 0.5, 0.5, random.randint(0, maze_depth - 1) + 0.5]
        while ((position[0] - actor_position[0]) ** 2 + (position[2] - actor_position[2]) ** 2) < 1.0:
            # avoid overlapping collectables
            position = [random.randint(0, maze_width - 1) + 0.5, 0.5, random.randint(0, maze_depth - 1) + 0.5]

        collectable = sm.Sphere(position=position, radius=0.2, material=sm.Material.RED, with_collider=True)
        maze += collectable
        reward_function = sm.RewardFunction(
            type="sparse",
            entity_a=actor,
            entity_b=collectable,
            distance_metric="euclidean",
            threshold=0.5,
            is_terminal=True,
            is_collectable=False,
        )
        actor += reward_function

    timeout_reward_function = sm.RewardFunction(
        type="timeout",
        entity_a=actor,
        entity_b=actor,
        distance_metric="euclidean",
        threshold=100,
        is_terminal=True,
        scalar=-1.0,
    )
    actor += timeout_reward_function

    return maze


def generate_env(port):
    env = sm.RLEnv(generate_map, args.n_maps, args.n_show, engine_exe=args.build_exe, engine_port=port)

    return env


parser = argparse.ArgumentParser()
parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv")
parser.add_argument("--n_maps", default=12, type=int, required=False, help="Number of maps to spawn")
parser.add_argument("--n_show", default=4, type=int, required=False, help="Number of maps to show")
args = parser.parse_args()
args.build_exe = "/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64"
env = sm.ParallelRLEnv(generate_env, 4)

time.sleep(2.0)
model = PPO("MultiInputPolicy", env, verbose=3, n_epochs=2)
model.learn(total_timesteps=100000)

env.close()