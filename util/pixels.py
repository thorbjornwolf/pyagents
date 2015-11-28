"""This module contains methods that can aid in preprocessing a pixel stream
"""
import numpy as np
from scipy.misc import imresize

# from util.listops import product

# _module_mem = dict()


def pixel_max(*frames):
    """Takes any number of frames as separate arguments and
    returns a pixel buffer with the maximum value per pixel across
    the frames given.
    """
    return np.max(np.stack(frames), axis=0)


def pixel_avg(*frames):
    """Takes any number of frames as separate arguments and
    returns a pixel buffer with the average value per pixel across
    the frames given.
    """
    return np.average(np.stack(frames), axis=0)


def scale(array, wanted_shape=(64,64)):
    """Scales an array down to the wanted shape.
    """
    return imresize(array.squeeze(), wanted_shape, 'bilinear'))



class Preprocessor(object):
    """This class encapsulates preprocessing settings
    and actions for the following operations:
    - Take max for each color channel over this and 
        previous n_frame_max frames
    - Convert to luminance (using luma constants)
    - Scale down to SCALE_SHAPE pixels
    - Concatenate with the last n_frame_concat preprocessed inputs
    """

    def __init__(self, scale_shape, n_frame_concat, n_frame_max):
        """scale_shape is the wanted shape of the output's first two 
            dimensions
        n_frame_concat is the number of preprocessed frames that are
            to be concatenated with the current frame.
        n_frame_max is the number of previous frames over which we
            take the max value for each channel.
        """
        self.scale_shape = scale_shape
        # Holds the last n_frame_max unprocessed frames
        self._unprocessed = CircularList(n_frame_max)
        # Holds the last n_frame_concat processed frames
        self._processed = CircularList(n_frame_concat)

    def process(self, gm_callbacks):
        """gm_callbacks is the namedtuple from a GameManager
        containing methods that can be used to get different
        state representations.

        Returns a numpy array of 3 dimensions, where the last 
        dimension is time.
        """

        frame = self.get_basis_frame(gm_callbacks)
        state = self.time_concatenate(frame)
        return state

    def trace(self, gm_callbacks):
        """Returns an np.array of shape scale_shape
        which is a weighted average over the last n_frame_concat
        frames, plus the current frame
        """
        state = self.process(gm_callbacks)
        weights = [x+1 for x in reversed(range(state.shape[0]))]
        return np.average(state, axis=0, weights=weights)

    def time_max(self, frame):
        lastframes = self._unprocessed[:]
        self._unprocessed.append(frame)

        return np.max(np.stack([frame] + lastframes), axis=0)

    def luminance(self, frame):
        # Use luma constants
        # https://en.wikipedia.org/wiki/HSL_and_HSV#Lightness
        weights = np.array([0.3, 0.59, 0.11])
        weighted = np.multiply(frame, weights)
        return np.sum(weighted, axis=2)

    def resize(self, frame):
        return imresize(frame, self.scale_shape, 'bilinear')

    def get_basis_frame(self, gm_callbacks):
        """Take max for each channel over this and last frames
        Convert to luminance
        Scale down
        """
        frame = gm_callbacks.rgb()
        frame = self.time_max(frame)
        frame = self.luminance(frame)
        frame = self.resize(frame)

        return frame

    def time_concatenate(self, frame):
        frames = [frame] + self._processed[:]
        frames = np.stack(frames, axis=0)
        self._processed.append(frame)
        return frames

    def get_settings(self):
        """Called by the GameManager when it is
        time to store this object's settings

        Returns a dict representing the settings needed to 
        reproduce this object.
        """
        return dict([
            ('scale_shape', self.scale_shape),
            ('n_frame_concat', self._processed.capacity()),
            ('n_frame_max', self._unprocessed.capacity()),
        ])