# -*- coding: utf-8 -*-
## @package ivf.core.sfs.colormap_estimation
#
#  ivf.core.sfs.colormap_estimation utility package.
#  @author      tody
#  @date        2016/02/09

import numpy as np
import cv2
from scipy.interpolate.interpolate import interp1d
from scipy.interpolate.fitpack2 import UnivariateSpline

from ivf.cv.image import luminance
from ivf.np.norm import normVectors
from scipy.interpolate.rbf import Rbf




class ColorMapEstimation:
    def __init__(self, Cs, Is=None, num_samples=2000):
        self._Cs = Cs
        self._I0s = np.average(Cs, axis=1)
        if Is is None:
            Is = np.array(self._I0s)
        self._Is = Is
        self._map = None
        self._map_size = 256
        self._num_samples = num_samples

        self._compute()

    def setBrightness(self, Is, update=True):
        self._Is = Is

        if update:
            self._compute()

    def setColor(self, Cs, update=True):
        self._Cs = Cs

        if update:
            self._compute()

    def shading(self, Is):
        I_ids = self._I_ids(Is, self._Iminmax)
        Cs = self._map[I_ids, :]
        return Cs

    def illumination(self, Cs):
        I0s = np.average(Cs, axis=1)
        I0_ids = self._I_ids(I0s)

        C_map = np.zeros((self._map_size, Cs.shape[1]))
        hist = np.zeros((self._map_size))
        C_map[I0_ids, :] += Cs[:, :]
        hist[I0_ids] += 1.0

        hist_positive = hist > 0

        for ci in xrange(3):
            C_map[hist_positive, ci] *= 1.0 / hist[hist_positive]

        I_map = np.zeros((self._map_size))

        I_min, I_max = self._Iminmax

        for mi in xrange(self._map_size):
            c = C_map[mi]
            dc_i = np.argmin(normVectors(self._map[:, :] - c))

            I_map[mi] = I_min + (I_max - I_min) * dc_i / float(self._map_size - 1)

        return I_map[I0_ids]

    def mapImage(self, image_size=(256, 256)):
        return cv2.resize(self._map.reshape(1, self._map_size, -1), image_size)

    def _I_ids(self, Is, I_minmax=None):
        if I_minmax is None:
            I_minmax = np.min(Is), np.max(Is)
        I_min, I_max = I_minmax
        I_ids = np.int32((self._map_size - 1) * (Is - I_min) / (I_max - I_min))
        I_ids = np.clip(I_ids, 0, self._map_size - 1)
        return I_ids

    def _compute(self):
        self.__computeByHistogram()

    def _rbf(self, Is, Cs, smooth=0.005):
        rbf_list = []
        for ci in xrange(3):
            rbf_list.append(Rbf(Is, Cs[:, ci], smooth=smooth))

        def f(Is_new):
            Cs_new = np.zeros((len(Is_new), Cs.shape[1]))
            for ci in xrange(3):
                Cs_new[:, ci] = rbf_list[ci](Is_new)
            return Cs_new
        return f

    def __computeByHistogram(self):
        sample_ids = np.random.randint(len(self._Is) - 1, size=self._num_samples)
        Is = self._Is[sample_ids]
        I0s = self._I0s[sample_ids]
        Cs = self._Cs[sample_ids]

        I_min, I_max = np.min(Is), np.max(Is)
        self._Iminmax = I_min, I_max

        C_order = np.argsort(I0s)
        Cs_sort = Cs[C_order]
        Is_sort = np.sort(Is)

        hist = np.zeros((self._map_size))
        Cs_avg = np.zeros((self._map_size, Cs.shape[1]))

        I_ids = self._I_ids(Is_sort)
        Cs_avg[I_ids, :] += Cs_sort[:, :]
        hist[I_ids] += 1.0
        hist_positive = hist > 0

        for ci in xrange(3):
            Cs_avg[hist_positive, ci] *= 1.0 / hist[hist_positive]

        self._map = np.zeros((self._map_size, Cs.shape[1]))

        hist_positive = np.where(hist > 0)[0]

        mi = 0
        for hi in hist_positive:

            while mi < hi:
                self._map[mi, :] = Cs_avg[hi, :]
                mi += 1

        while mi < self._map_size:
            self._map[mi, :] = Cs_avg[hist_positive[-1], :]
            mi += 1

        Is_new = np.arange(self._map_size)
        M = self._rbf(Is_new, self._map, smooth=0.00005)

        self._map = np.clip(M(Is_new), 0.0, 1.0)

#         Is_avg = np.where(hist > 0)[0]
#         M = []
#
#         for ci in xrange(3):
#             M.append(Rbf(Is_avg, Cs_avg[hist_positive, ci], smooth=0.005))
#
#         for ci in xrange(3):
#             self._map[:, ci] = M[ci](np.arange(self._map_size))

    def __computeByPixelList(self):
        sample_ids = np.random.randint(len(self._Is) - 1, size=self._num_samples)
        Is = self._Is[sample_ids]
        I0s = self._I0s[sample_ids]
        Cs = self._Cs[sample_ids]

        I_min, I_max = np.min(Is), np.max(Is)
        self._Iminmax = I_min, I_max

        C_order = np.argsort(I0s)
        Cs_sort = Cs[C_order]
        Is_sort = np.sort(Is)

        self._map = np.zeros((self._map_size, Cs.shape[1]))
        I_i = 0
        for mi in xrange(self._map_size):
            Im = I_min + (I_max - I_min) * mi / (self._map_size - 1)

            while I_i < len(Is_sort) - 1 and Is_sort[I_i] < Im:
                    I_i += 1

            self._map[mi, :] = Cs_sort[I_i, :]

