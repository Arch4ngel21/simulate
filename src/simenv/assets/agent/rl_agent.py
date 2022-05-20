import itertools
from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from ..asset import Asset
from .rl_agent_actions import DiscreteRLAgentActions, RLAgentActions


class RL_Agent(Asset):
    dimensionality = 3
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        color: Optional[List[float]] = None,
        height: Optional[float] = 1.5,
        move_speed: Optional[float] = 2.0,
        turn_speed: Optional[float] = 0.4,
        actions: Optional[RLAgentActions] = None,
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        super().__init__(name=name, position=position, rotation=rotation, parent=parent, children=children)

        if color is None:
            color = [1.0, 0.0, 0.0]
        if actions is None:
            actions = DiscreteRLAgentActions.default()
        self.color = color
        self.height = height
        self.move_speed = move_speed
        self.turn_speed = turn_speed
        self.actions = actions