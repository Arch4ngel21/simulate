import itertools
from dataclasses import dataclass
from typing import List, Optional, Union

import numpy as np

from ..asset import Asset
from ..camera import Camera
from .reward_function import RewardFunction
from .mapping import GenericActionMapping, Discrete, Continuous

try:
    from gym import spaces
except ImportError:
    raise


def map_observation_devices_to_spaces(asset: Asset) -> spaces:
    if isinstance(asset, Camera):
        return spaces.Box(low=0, high=255, shape=[3, asset.height, asset.width], dtype=np.uint8)
    raise NotImplementedError(f"This Asset ({type(Asset)})is not yet implemented as an RlAgent type of observation.")


class RlAgent:
    """A reinforcement learning agent component for an Asset.

    Provide (all is optional at the moment):
    - action space as List of gym.space
    - action mapping to the physics engine variables
    - observation devices as assets (currently only Camera)
    - reward functions

    Automatically infered:
    - observation space from the devices

    """

    def __init__(
        self,
        action_space: spaces.Space = None,
        action_mappings: Optional[List[GenericActionMapping]] = None,
        observation_devices: Optional[Union[Asset, List[Asset]]] = None,
        reward_functions: Optional[Union[RewardFunction, List[RewardFunction]]] = None,
    ):
        if reward_functions is None:
            reward_functions = []

        self.action_space = action_space
        self.action_mappings = action_mappings
        self.observation_devices = observation_devices
        self.reward_functions = reward_functions

        self.observation_space = [map_observation_devices_to_spaces(device) for device in observation_devices]

    def copy(self):
        instance_copy = type(self)(action_space=self.action_space, action_mappings=self.action_mappings, observation_devices=self.observation_devices, reward_functions=self.reward_functions)
        return instance_copy

    def _post_copy(self):
        self.reward_functions = [rf._post_copy(self) for rf in self.reward_functions]
        # TODO handle observation devices as well


class RlAgentGrid(RlAgent):
    """ An RL agent moving with discret actions:
        - turn left
        - turn right
        - move forward
    """
    def __init__(
        self,
        observation_devices: Optional[List[Asset]] = None,
        reward_functions: Optional[List[RewardFunction]] = None,
    ):
        action_space = spaces.Discrete(3)
        action_mappings = [Discrete("rotation_y", value=-np.pi/2),
                           Discrete("rotation_y", value=np.pi/2),
                           Discrete("position_x", value=1.0)]
        super().__init__(action_space, action_mappings, observation_devices, reward_functions)


class RlAgentGrid(RlAgent):
    """ An RL agent moving with discret actions:
        - turn left
        - turn right
        - move forward
    """
    def __init__(
        self,
        observation_devices: Optional[List[Asset]] = None,
        reward_functions: Optional[List[RewardFunction]] = None,
    ):
        action_space = spaces.Discrete(3)
        action_mappings = [Discrete("rotation_y", value=-np.pi/2),
                           Discrete("rotation_y", value=np.pi/2),
                           Discrete("position_x", value=1.0)]
        super().__init__(action_space, action_mappings, observation_devices, reward_functions)
