
# -*- coding: utf-8 -*-
## @package ivf.core.sfs.brightness_field
#
#  ivf.core.sfs.brightness_field utility package.
#  @author      tody
#  @date        2016/02/08


import numpy as np
import scipy.sparse
import cv2
from ivf.core.sfs.constraints import laplacianMatrix
from ivf.core.solver import amg_solver
from ivf.core.sfs.lumo import computeNz
from ivf.np.norm import normalizeVectors


class BrightnessField:
    def __init__(self, I_32F, sigma=1.0):
        self._I_32F = I_32F
        self._sigma = sigma

        self._computeGradients()
        A_I, b_I = self._computeConstraints()
        self._optimize(A_I, b_I)

    def gradients(self):
        return self._gxy

    def smoothBrightness(self):
        return self._I_smooth

    def brightnessDifference(self):
        return self._dI

    def field(self):
        return self._N_32F

    def _computeGradients(self):
        I_32F = self._I_32F
        I_smooth = cv2.GaussianBlur(I_32F, (0, 0), self._sigma)
        self._I_smooth = I_smooth
        self._dI = np.abs(cv2.GaussianBlur(I_32F, (0, 0), 4.0) - I_32F)

        h, w = I_32F.shape

        gx = - cv2.Sobel(I_smooth, cv2.CV_64F, 1, 0, ksize=1)
        gy = cv2.Sobel(I_smooth, cv2.CV_64F, 0, 1, ksize=1)

        epsilon = 0.0001
        gxy_norm = np.clip(np.sqrt(gx * gx + gy * gy), epsilon, 1.0)
        Nxy_norm = np.sqrt(np.clip(1.0 - self._I_smooth * self._I_smooth, 0.0, 1.0))

        gx = gx * Nxy_norm / gxy_norm
        gy = gy * Nxy_norm / gxy_norm
        self._gxy = (gx, gy)

    def _computeConstraints(self, w_cons=0.01):
        h, w = self._I_32F.shape[:2]
        num_verts = h * w
        diags = np.zeros(num_verts)

        dI = self._dI.flatten()
        cons_ids = np.where(dI > 0.05 * np.max(dI))
        diags[cons_ids] = 1.0

        A = scipy.sparse.diags(diags, 0)
        AtA = A.T * A

        b = np.zeros((num_verts, 3), dtype=np.float32)
        gx, gy = self._gxy
        gx = gx.flatten()
        gy = gy.flatten()
        I_smooth = self._I_smooth.flatten()
        b[cons_ids, 0] = gx[cons_ids]
        b[cons_ids, 1] = gy[cons_ids]
        b[cons_ids, 2] = I_smooth[cons_ids]

        Atb = A.T * b

        return w_cons * AtA, w_cons * Atb

    def _optimize(self, A_I, b_I):
        h, w = self._I_32F.shape[:2]
        A_L = laplacianMatrix((h, w), num_elements=1)
        A_L = A_L

        A = A_L + A_I
        b = b_I

        N = amg_solver.solve(A, b).reshape(-1, 3)
        computeNz(N)
        #N = normalizeVectors(N)
        N_32F = N.reshape(h, w, 3)

        self._N_32F = N_32F
