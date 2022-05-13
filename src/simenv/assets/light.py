import itertools
from typing import List, Optional, Union

import numpy as np

from .asset import Asset


class Light(Asset):
    """A Scene Light.

    Three type of punctual lights are implemented:
    - directional (default): an infinitely distant point source
    - positional: point sources located in the real-world. A cone angle can be defined to limit the spatial distribution of a positional light beam in which case these are often known as spot light. a Value of None or above 90 degree means no spatial limitation.

    Punctual lights are defined as infinitely small points that emit light in well-defined directions and intensities.

    Angles are in degrees.

    """

    dimensionality = 3
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        *,
        intensity: Optional[float] = 1.0,
        color: Optional[List[float]] = [1.0, 1.0, 1.0],
        range: Optional[float] = None,
        inner_cone_angle: Optional[float] = 0.0,
        outer_cone_angle: Optional[float] = 45.0,
        light_type: Optional[str] = "directional",
        name: Optional[str] = None,
        center: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        scale: Optional[Union[float, List[float]]] = None,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        super().__init__(name=name, center=center, direction=direction, scale=scale, parent=parent, children=children)
        self.intensity = intensity
        self.color = color
        self.range = range

        if light_type not in ["directional", "positional"]:
            raise ValueError("Light type should be selected in ['directional', 'positional']")
        self.light_type = light_type
        self.inner_cone_angle = inner_cone_angle
        self.outer_cone_angle = outer_cone_angle
