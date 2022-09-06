# Copyright 2022 The HuggingFace Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import defaultdict

import numpy as np
from gym import spaces

import simenv as sm

# Lint as: python3
from simenv.scene import Scene


try:
    from stable_baselines3.common.vec_env.base_vec_env import VecEnv
except ImportError:

    class VecEnv:
        pass  # Dummy class if SB3 is not installed


class ParallelRLEnvironment(VecEnv):
    """
    Parallel RL environment wrapper for SimEnv scene. Uses functionality from the VecEnv in stable baselines 3
    For more information on VecEnv, see the source
    https://stable-baselines3.readthedocs.io/en/master/guide/vec_envs.html

    Args:
        scene_or_map_fn: a generator function for generating instances of the desired environment
        n_maps: TODO
        n_show: TODO
        frame_rate: TODO
        frame_skip: TODO
    """

    def __init__(self, scene_or_map_fn, n_maps=1, n_show=1, frame_rate=30, frame_skip=4, **engine_kwargs):

        if hasattr(scene_or_map_fn, "__call__"):
            self.scene = Scene(engine="Unity", **engine_kwargs)
            self.scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)
            self.map_roots = []
            for i in range(n_maps):
                map_root = scene_or_map_fn(i)
                self.scene += map_root
                self.map_roots.append(map_root)
        else:
            self.scene = scene_or_map_fn
            self.map_roots = [self.scene]

        # TODO --> add warning if scene has no actor or reward functions
        self.actors = {actor.name: actor for actor in self.scene.actors}
        self.n_actors = len(self.actors)
        self.n_maps = n_maps
        self.n_show = n_show
        self.n_actors_per_map = self.n_actors // self.n_maps

        self.actor = next(iter(self.actors.values()))

        self.action_space = self.scene.action_space  # quick workaround while Thom refactors this
        self.observation_space = {
            "CameraSensor": self.scene.observation_space
        }  # quick workaround while Thom refactors this
        self.observation_space = spaces.Dict(self.observation_space)

        super().__init__(n_show, self.observation_space, self.action_space)

        # Don't return simulation data, since minimal/faster data will be returned by agent sensors
        # Pass maps kwarg to enable map pooling
        maps = [root.name for root in self.map_roots]
        self.scene.show(
            frame_rate=frame_rate,
            frame_skip=frame_skip,
            return_frames=False,
            return_nodes=False,
            maps=maps,
            n_show=n_show,
        )

    def step(self, action=None):
        action_dict = {}
        # TODO: adapt this to multiagent setting
        if action is None:
            for i in range(self.n_show):
                action_dict[str(i)] = int(self.action_space.sample())
        elif isinstance(action, np.int64):
            action_dict["0"] = int(action)
        else:
            for i in range(self.n_show):
                action_dict[str(i)] = int(action[i])

        event = self.scene.step(action=action_dict)

        # Extract observations, reward, and done from event data
        # TODO nathan thinks we should make this for 1 agent, have a separate one for multiple agents.
        if self.n_actors == 1:
            actor_data = event["actors"][self.actor.name]
            obs = self._extract_sensor_obs(actor_data["observations"])
            reward = actor_data["reward"]
            done = actor_data["done"]
            info = {}

        else:
            reward = []
            done = []
            info = []
            obs = []
            for actor_name in event["actors"].keys():
                actor_data = event["actors"][actor_name]
                actor_obs = self._extract_sensor_obs(actor_data["observations"])
                obs.append(actor_obs)
                reward.append(actor_data["reward"])
                done.append(actor_data["done"])
                info.append({})

            obs = self._obs_dict_to_tensor2(obs)
            reward = np.array(reward)
            done = np.array(done)

        return obs, reward, done, info

    def reset(self):
        self.scene.reset()

        # To extract observations, we do a "fake" step (no actual simulation with frame_skip=0)
        event = self.scene.step(return_frames=True, frame_skip=0)
        obs = {}
        if self.n_actors == 1:
            actor_data = event["actors"][self.actor.name]
            obs = self._extract_sensor_obs(actor_data["observations"])
        else:
            obs = []
            for actor_name in event["actors"].keys():
                actor_data = event["actors"][actor_name]
                actor_obs = self._extract_sensor_obs(actor_data["observations"])
                obs.append(actor_obs)

            obs = self._obs_dict_to_tensor2(obs)

        return obs

    def _obs_dict_to_tensor2(self, obs):
        out = defaultdict(list)

        for o in obs:
            for key, value in o.items():
                out[key].append(value)

        for k in out.keys():
            out[key] = np.stack(out[key])

        return out

    def _extract_sensor_obs(self, sim_data):
        sensor_obs = {}
        for sensor_name, sensor_data in sim_data.items():
            if sensor_data["type"] == "uint8":
                shape = sensor_data["shape"]
                measurement = np.array(sensor_data["uintBuffer"], dtype=np.uint8).reshape(shape)
                sensor_obs[sensor_name] = measurement
                pass
            elif sensor_data["type"] == "float":
                shape = sensor_data["shape"]
                measurement = np.array(sensor_data["floatBuffer"], dtype=np.float32).reshape(shape)
                sensor_obs[sensor_name] = measurement
            else:
                raise TypeError

        return sensor_obs

    # def _obs_dict_to_tensor(self, obs_dict):
    #     out = []
    #     for val in obs_dict.values():
    #         out.append(val)

    #     if self.n_agents == 1:
    #         return {"CameraSensor": np.stack(out)[0]}  # quick workaround while Thom refactors this
    #     else:
    #         return {"CameraSensor": np.stack(out)}  # quick workaround while Thom refactors this

    def close(self):
        self.scene.close()

    def env_is_wrapped(self):
        return [False] * self.n_agents * self.n_parallel

    # required abstract methods

    def step_async(self, actions: np.ndarray) -> None:
        raise NotImplementedError()

    def env_method(self):
        raise NotImplementedError()

    def get_attr(self):
        raise NotImplementedError()

    def seed(self, value):
        # this should be done when the env is initialized
        return
        # raise NotImplementedError()

    def set_attr(self):
        raise NotImplementedError()

    def step_send(self):
        raise NotImplementedError()

    def step_wait(self):
        raise NotImplementedError()