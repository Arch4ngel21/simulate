"""
Util functions.
"""

import numpy as np

from .constants import GRANULARITY, HEIGHT_CONSTANT


def decode_rgb(img, specific_map=None, sample_from=None, max_height=8):
    """
    Decode the RGB image into a height map with tiles of 2x2.

    Might be temporary until we migrate completely to this format.
    """

    img_np = np.array(img)

    if sample_from is None and specific_map is None:
        map_2d = img_np[:, :, 0] * HEIGHT_CONSTANT
    else:
        # Create the map
        map_2d = np.zeros((2 * img_np.shape[0], 2 * img_np.shape[1]))

        # TODO: optimize this decoding
        for i in range(img_np.shape[0]):
            for j in range(img_np.shape[1]):
                if img_np[i, j, 1] == 0:
                    map_2d[2 * i : 2 * (i + 1), 2 * j : 2 * (j + 1)] = img_np[i, j, 0]
                elif img_np[i, j, 1] == 1:
                    map_2d[2 * i, 2 * j : 2 * (j + 1)] = img_np[i, j, 0]
                    map_2d[2 * i + 1, 2 * j : 2 * (j + 1)] = img_np[i, j, 0] + 1
                elif img_np[i, j, 1] == 2:
                    map_2d[2 * i : 2 * (i + 1), 2 * j] = img_np[i, j, 0]
                    map_2d[2 * i : 2 * (i + 1), 2 * j + 1] = img_np[i, j, 0] + 1
                elif img_np[i, j, 1] == 3:
                    map_2d[2 * i, 2 * j : 2 * (j + 1)] = img_np[i, j, 0] + 1
                    map_2d[2 * i + 1, 2 * j : 2 * (j + 1)] = img_np[i, j, 0]
                elif img_np[i, j, 1] == 4:
                    map_2d[2 * i : 2 * (i + 1), 2 * j] = img_np[i, j, 0] + 1
                    map_2d[2 * i : 2 * (i + 1), 2 * j + 1] = img_np[i, j, 0]

        map_2d = map_2d * (255.0 * HEIGHT_CONSTANT * 1 / max_height)

    return map_2d


def convert_to_actual_pos(obj_pos, generated_map):
    # Unpack values
    x, y, z = generated_map
    
    # Get true heights and weights
    # TODO: should we pass it in the function, or add atributes to a class?
    true_width, true_height = x.shape
    width, height = true_width / GRANULARITY, true_height / GRANULARITY

    # Get conversiona array to multiply by positions and get indexes on x, y, z
    conversion = np.array([(true_width - 1) / (width), (true_height - 1) / (height)])

    # Set object in the middle of the tile (by adding 0.5)
    converted_pos = np.expand_dims(conversion, axis=1) * [obj_pos + 0.5]

    # Transform to int
    converted_pos = converted_pos.astype(int)

    # Transform to tuple in order to pass to x, y, z
    converted_pos = tuple(*converted_pos)

    return np.array([x[converted_pos], y[converted_pos], z[converted_pos]]).transpose()


def get_bounds(object_type, object_size):
    """
    Returns bounds for certain objects construction.
    """
    if object_type == 'Cube':
        xMin, xMax, yMin, yMax, zMin, zMax = 0, object_size, 0, object_size, 0, object_size
        return xMin, xMax, yMin, yMax, zMin, zMax

    else:
        raise NotImplementedError
