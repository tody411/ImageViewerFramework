# -*- coding: utf-8 -*-
## @package ivf.cmds.sfs.pr_sfs
#
#  ivf.cmds.sfs.pr_sfs utility package.
#  @author      tody
#  @date        2016/02/05

import numpy as np
import cv2

from ivf.core.sfs.sfs import ShapeFromShading

from ivf.core.sfs.silhouette_normal import silhouetteNormal
from ivf.core.sfs.lumo import normalConstraints, computeNz
from ivf.core.solver import amg_solver
from ivf.np.norm import normalizeVectors
from ivf.core.sfs.constraints import silhouetteConstraints, laplacianMatrix, gradientConstraints, laplacianConstraints,\
    brightnessConstraints
from ivf.core.shader.lambert import diffuse
from ivf.core.sfs.reflectance_estimation import LambertReflectanceEstimation
from ivf.core.solver.amg_solver import gauss_seidel_iter, sor_iter
from ivf.util.timer import timing_func


class Wu08SFS(ShapeFromShading):
    def __init__(self, L=None, C_32F=None, A_8U=None):
        super(Wu08SFS, self).__init__("Wu08", L, C_32F, A_8U)
        self._N0_32F = None

    def _runImp(self):
        A, b = self._computeInitialNormal()
        self._projectBrightness(A, b)

        L = self._L
        self._I_32F = diffuse(self._N_32F, L)
        reflectance = LambertReflectanceEstimation(self._C0_32F, self._I_32F)
        self._C_32F = reflectance.shading(self._I_32F)

    def _computeInitialNormal(self):
        #print self._A_8U
        A_8U = self._A_8U
        h, w = A_8U.shape
        A_L = laplacianMatrix((h, w), num_elements=3)
        A_sil, b_sil = silhouetteConstraints(A_8U, is_flat=True)

        A = A_L + A_sil
        b = b_sil

        N = amg_solver.solve(A, b).reshape(-1, 3)
        computeNz(N)
        N = normalizeVectors(N)
        N_32F = N.reshape(h, w, 3)
        self._N0_32F = N_32F
        return A, b

    @timing_func
    def _projectBrightness(self, A, b):
        I_32F = self._I0_32F
        h, w = I_32F.shape[:2]
        I = I_32F.reshape(h * w)

        L = self._L
        N0_32F = self._N0_32F
        N0 = N0_32F.reshape(-1, 3)

        NL = np.clip(np.dot(N0, L), 0.0, 1.0)

        I = self._estimateBrightness()

        dI = I - NL

        N = np.array(N0)

        w_I = 1.0
        w_smooth = 1.0
        for k in xrange(10):
            x = N.flatten()
            sor_iter(A, x, b, 1.3, iterations=10)
            N_smooth = x.reshape(-1, 3)
            for i in range(3):
                N[:, i] = w_I * (N[:, i] + L[i] * dI) + w_smooth * N_smooth[:, i]

            N = normalizeVectors(N)

            NL = np.clip(np.dot(N, L), 0.0, 1.0)
            dI = I - NL

        self._N_32F = N.reshape(h, w, 3)

    def _NzToNxy(self, N):
        gx = - cv2.Sobel(N[:, :, 2], cv2.CV_64F, 1, 0, ksize=1)
        gy = cv2.Sobel(N[:, :, 2], cv2.CV_64F, 0, 1, ksize=1)

        epsilon = 0.0001
        gxy_norm = np.clip(np.sqrt(gx * gx + gy * gy), epsilon, 1.0)
        Nxy_norm = np.sqrt(np.clip(1.0 - N[:, :, 2] * N[:, :, 2], 0.0, 1.0))

        gx = gx * Nxy_norm / gxy_norm
        gy = gy * Nxy_norm / gxy_norm

        N[:, :, 0] = gx
        N[:, :, 1] = gy

        return N

    def _estimateBrightness(self):
        I_32F = self._I0_32F
        h, w = I_32F.shape[:2]
        I = I_32F.reshape(h * w)

        NL_min, NL_max = 0.0, 1.0

        I_min, I_max = np.min(I), np.max(I)

        I = NL_min + (NL_max - NL_min) * (I - I_min) / (I_max - I_min)
        return I


    def _estimateShading(self):
        pass


class LaplacianSFS(ShapeFromShading):
    def __init__(self, L=None, C_32F=None, A_8U=None):
        super(Wu08SFS, self).__init__("LaplacianSFS", L, C_32F, A_8U)
        self._N0_32F = None

    def _runImp(self):
        self._computeInitialNormal()
        self._projectBrightness()

    def _computeInitialNormal(self):
        A_8U = self._A_8U
        h, w = A_8U.shape
        N0_32F = silhouetteNormal(A_8U)
        A, b = normalConstraints(A_8U, N0_32F)

        N_flat = amg_solver.solve(A, b)
        N_flat = normalizeVectors(N_flat)
        N_32F = N_flat.reshape(h, w, 3)
        self._N0_32F = N_32F

    def _projectBrightness(self):
        I_32F = self._I_32F
        h, w = I_32F.shape[:2]
        I = I_32F.reshape(h * w)

        L = self._L
        N0_32F = self._N0_32F
        N0 = N0_32F.reshape(-1, 3)

        NL = np.dot(N0, L)
        NL_min, NL_max = np.min(NL), np.max(NL)

        I_min, I_max = np.min(I), np.max(I)

        I = NL_min + (NL_max - NL_min) * (I - I_min) / (I_max - I_min)

        dI = I - NL

        N = np.zeros(N0.shape)
        for i in range(3):
            N[:, i] = N0[:, i] + L[i] * dI

        N = normalizeVectors(N)
        self._N_32F = N.reshape(h, w, 3)