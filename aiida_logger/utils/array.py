"""Contains auxiliary utilities to convert strings to arrays."""
from __future__ import absolute_import
import numpy as np


def string_to_float(list_of_strings, separator):
    """Convert a list of strings to NumPy float arrays."""
    array = []
    for item in list_of_strings:
        array.append(np.fromstring(item, sep=separator))

    return np.asarray(array)
