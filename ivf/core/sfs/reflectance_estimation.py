# -*- coding: utf-8 -*-
## @package ivf.core.sfs.reflectance_estimation
#
#  ivf.core.sfs.reflectance_estimation utility package.
#  @author      tody
#  @date        2016/02/05

import numpy as np

from ivf.cv.image import luminance


class LambertReflectanceEstimation:
    def __init__(self, C_32F, I_32F=None):
        self._C_32F = C_32F

        I0_32F = luminance(C_32F)
        self._I0_32F = I0_32F
        if I_32F is None:
            I_32F = np.array(I0_32F)

        self._I_32F = I_32F

        self._compute()

    def setBrightness(self, I_32F, update=True):
        self._I_32F = I_32F

        if update:
            self._compute()

    def setImage(self, C_32F, update=True):
        self._C_32F = C_32F

        if update:
            self._compute()

    def shading(self, I_32F):
        ka = self._ka
        kd = self._kd

        h, w = I_32F.shape[:2]
        C_32F = np.zeros((h, w, 3), dtype=np.float32)

        for ci in xrange(3):
            C_32F[:, :, ci] = ka[ci] + kd[ci] * self._I_32F

        C_32F = np.clip(C_32F, 0.0, 1.0)

        return C_32F

    def _compute(self):
        self._computeByFitting()

    def _computeByFitting(self):
        I_32F = self._I_32F
        C_32F = self._C_32F

        h, w = I_32F.shape[:2]
        C_flat = C_32F.reshape(-1, 3)
        I_flat = I_32F.reshape(h * w)

        I_avg = np.average(I_flat)
        C_avg = np.average(C_flat, axis=0)

        I_kd = I_flat - I_avg
        I_neg = I_kd < 0
        I_kd[I_neg] = - I_kd[I_neg]
        C_kd = C_flat - C_avg
        C_kd[I_neg] = - C_kd[I_neg]

        I_kd_sum = np.sum(I_kd)
        C_kd_sum = np.sum(C_kd, axis=0)

        kd = C_kd_sum / I_kd_sum
        self._kd = kd

        C_sum = np.sum(C_flat, axis=0)
        I_sum = np.sum(I_flat)

        ka = (C_sum - kd * I_sum) / (h * w)
        self._ka = ka

    def _computeByMinMax(self):
        I_32F = self._I_32F
        C_32F = self._C_32F
        C_flat = C_32F.reshape(-1, 3)

        I_min, I_max = np.min(I_32F), np.max(I_32F)
        C_min, C_max = np.min(C_flat, axis=0), np.max(C_flat, axis=0)

        self._kd = (C_max - C_min) / (I_max - I_min)
        self._ka = 0.5 * (C_min + C_max) - 0.5 * (I_min + I_max) * self._kd

