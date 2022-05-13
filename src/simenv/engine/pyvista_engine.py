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

# Lint as: python3
""" A PyVista plotting rendered as engine."""
from typing import Optional

import numpy as np
import pyvista

from ..assets import Asset, Camera, Light, Object3D
from .engine import Engine


class PyVistaEngine(Engine):
    def __init__(self, scene, **pyvista_plotter_kwargs):
        self.plotter: pyvista.Plotter = pyvista.Plotter(lighting="none", **pyvista_plotter_kwargs)
        self._scene: Asset = scene

    def _update_scene(self):
        self.plotter.clear()
        has_lights = False
        for node in self._scene:
            if not isinstance(node, (Object3D, Camera, Light)):
                continue

            transforms = list(n.transform for n in node.tree_path)
            if len(transforms) > 1:
                model_transform_matrix = np.linalg.multi_dot(transforms)  # Compute transform from the tree parents
            else:
                model_transform_matrix = transforms[0]

            if isinstance(node, Object3D):
                located_mesh = node.mesh.transform(model_transform_matrix, inplace=False)
                self.plotter.add_mesh(located_mesh)
            elif isinstance(node, Camera):
                camera = pyvista.Camera()
                camera.model_transform_matrix = model_transform_matrix
                self.plotter.camera = camera
            elif isinstance(node, Light):
                light = pyvista.Light()
                light.transform_matrix = model_transform_matrix
                self.plotter.add_light(light)
                has_lights = True
        if not has_lights:
            self.plotter.enable_lightkit()  # Still add some lights

    def show(self, **pyvista_plotter_kwargs):
        self._update_scene()
        self.plotter.show(**pyvista_plotter_kwargs)

    def close(self):
        self.plotter.close()
