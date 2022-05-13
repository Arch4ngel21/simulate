# Copyright 2022 The HuggingFace Simenv Authors.
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
"""Utilities."""
import itertools
import math
import re
from typing import List, Union

import numpy as np


_uppercase_uppercase_re = re.compile(r"([A-Z]+)([A-Z][a-z])")
_lowercase_uppercase_re = re.compile(r"([a-z\d])([A-Z])")

_single_underscore_re = re.compile(r"(?<!_)_(?!_)")
_multiple_underscores_re = re.compile(r"(_{2,})")

_split_re = r"^\w+(\.\w+)*$"


def camelcase_to_snakecase(name: str) -> str:
    """Convert camel-case string to snake-case."""
    name = _uppercase_uppercase_re.sub(r"\1_\2", name)
    name = _lowercase_uppercase_re.sub(r"\1_\2", name)
    return name.lower()


def snakecase_to_camelcase(name: str) -> str:
    """Convert snake-case string to camel-case string."""
    name = _single_underscore_re.split(name)
    name = [_multiple_underscores_re.split(n) for n in name]
    return "".join(n.capitalize() for n in itertools.chain.from_iterable(name) if n != "")


def get_transform_from_trs(
    translation: Union[np.ndarray, List[float]],
    rotation: Union[np.ndarray, List[float]],
    scale: Union[np.ndarray, List[float]],
) -> np.ndarray:
    """Create a homogenious transform matrix (4x4) from 3D vector of translation and scale, and a quaternion vector of rotation."""
    if not isinstance(translation, np.ndarray):
        translation = np.array(translation)
    if not isinstance(rotation, np.ndarray):
        rotation = np.array(rotation)
    if not isinstance(scale, np.ndarray):
        scale = np.array(scale)

    translation = np.squeeze(translation)
    rotation = np.squeeze(rotation)
    scale = np.squeeze(scale)

    if not translation.shape == (3,):
        raise ValueError("The translation vector should be of size 3")
    if not rotation.shape == (4,):
        raise ValueError("The rotation vector should be of size 4")
    if not scale.shape == (3,):
        raise ValueError("The scale vector should be of size 3")

    translation_matrix = np.eye(4)
    translation_matrix[:3, 3] = translation
    translation_matrix[3, 3] = 1

    # Rotation matrix
    q0, q1, q2, q3 = rotation[0], rotation[1], rotation[2], rotation[3]
    r00 = 2 * (q0 * q0 + q1 * q1) - 1
    r01 = 2 * (q1 * q2 - q0 * q3)
    r02 = 2 * (q1 * q3 + q0 * q2)

    r10 = 2 * (q1 * q2 + q0 * q3)
    r11 = 2 * (q0 * q0 + q2 * q2) - 1
    r12 = 2 * (q2 * q3 - q0 * q1)

    r20 = 2 * (q1 * q3 - q0 * q2)
    r21 = 2 * (q2 * q3 + q0 * q1)
    r22 = 2 * (q0 * q0 + q3 * q3) - 1
    # Gather it all
    rotation_matrix = np.zeros((4, 4))
    rotation_matrix[3, 3] = 1
    rotation_matrix[:3, :3] = np.array([[r00, r01, r02], [r10, r11, r12], [r20, r21, r22]])

    scale_matrix = np.zeros((4, 4))
    scale_matrix[0, 0] = scale[0]
    scale_matrix[1, 1] = scale[1]
    scale_matrix[2, 2] = scale[2]
    scale_matrix[3, 3] = 1

    transformation_matrix = translation_matrix @ rotation_matrix @ scale_matrix
    return transformation_matrix


# def quaternion_from_transformation_matrix(matrix, isprecise=False):
#     m00, m01, m02 = M[0, :3]
#     m10, m11, m12 = M[1, :3]
#     m20, m21, m22 = M[2, :3]
#     # Sym matrix
#     sym_matrix = np.array([[m00-m11-m22, 0.0, 0.0, 0.0],
#                     [m01+m10,     m11-m00-m22, 0.0,         0.0],
#                         [m02+m20,     m12+m21,     m22-m00-m11, 0.0],
#                         [m21-m12,     m02-m20,     m10-m01,     m00+m11+m22]])
#     sym_matrix /= 3.0
#     # We take the largest eigenvector of sym_matrix
#     eigen_w, eigen_vector = np.linalg.eigh(sym_matrix)
#     quaternion = eigen_vector[[3, 0, 1, 2], np.argmax(eigen_w)]
#     if quaternion[0] < 0.0:
#         quaternion = -quaternion
#     return quaternion


# def get_scale_from_transformation_matrix(transformation_matrix):
#     mat = np.asarray(transformation_matrix, dtype=np.float64)
#     factor = np.trace(mat) - 2.0
#     # direction: unit eigenvector corresponding to eigenvalue factor
#     l, V = np.linalg.eig(mat)
#     near_factors, = np.nonzero(abs(np.real(l.squeeze()) - factor) < 1e-8)
#     if near_factors.size == 0:
#         # uniform scaling
#         factor = (factor + 2.0) / 3.0
#         return factor, None
#     direction = np.real(V[:, near_factors[0]])


# def get_trs_from_transformation_matrix(transformation_matrix: np.ndarray):
#     translation_matrix = np.array(transformation_matrix, copy=False)[:3, 3].copy()
#     transformation_matrix[:, 3] = 0
#     rotation_matrix = quaternion_from_transformation_matrix(transformation_matrix)
#     scale_matrix


def quat_from_euler(x: float, y: float, z: float) -> List[float]:
    qx = np.sin(x / 2) * np.cos(y / 2) * np.cos(z / 2) - np.cos(x / 2) * np.sin(y / 2) * np.sin(z / 2)
    qy = np.cos(x / 2) * np.sin(y / 2) * np.cos(z / 2) + np.sin(x / 2) * np.cos(y / 2) * np.sin(z / 2)
    qz = np.cos(x / 2) * np.cos(y / 2) * np.sin(z / 2) - np.sin(x / 2) * np.sin(y / 2) * np.cos(z / 2)
    qw = np.cos(x / 2) * np.cos(y / 2) * np.cos(z / 2) + np.sin(x / 2) * np.sin(y / 2) * np.sin(z / 2)
    return [qx, qy, qz, qw]


def quat_from_degrees(x, y, z):
    return quat_from_euler(math.radians(x), math.radians(y), math.radians(z))


def degrees_to_radians(x, y, z):
    return quat_from_euler(math.radians(x), math.radians(y), math.radians(z))
