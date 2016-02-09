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
from ivf.core.solver import amg_solver, image_solver
from ivf.np.norm import normalizeVectors
from ivf.core.sfs.constraints import silhouetteConstraints, laplacianMatrix, gradientConstraints, laplacianConstraints,\
    brightnessConstraints
from ivf.core.shader.lambert import diffuse
from ivf.core.sfs.reflectance_estimation import LambertReflectanceEstimation
from ivf.core.solver.amg_solver import gauss_seidel_iter, sor_iter
from ivf.util.timer import timing_func
from ivf.cv.normal import normalizeImage


class Wu08SFS(ShapeFromShading):
    def __init__(self, L=None, C_32F=None, A_8U=None):
        super(Wu08SFS, self).__init__("Wu08", L, C_32F, A_8U)
        self._N0_32F = None

    def _runImp(self):
        if self._N0_32F is None:
            self._computeInitialNormal()
        self._optimize()

        L = self._L
        self._I_32F = diffuse(self._N_32F, L)
        reflectance = LambertReflectanceEstimation(self._C0_32F, self._I_32F)
        self._C_32F = reflectance.shading(self._I_32F)

    def _computeInitialNormal(self):
        A_8U = self._A_8U
        self._N0_32F = np.float64(silhouetteNormal(A_8U))

        return

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

    def _laplacianConstraint(self, w_c=0.5):
        def func(N):
            N_smooth = image_solver.laplacian(N) + N
            N_smooth = computeNz(N_smooth.reshape(-1, 3)).reshape(N.shape)
            return w_c, N_smooth
        return func

    def _brightnessConstraint(self, L, I_32F, w_c=0.1):
        I_level = image_solver.LevelImage(I_32F)

        def func(N):
            I_32F_level = I_level.level(N)
            h, w = N.shape[:2]
            NL = np.dot(N.reshape(-1, 3), L)
            NL = np.clip(NL, 0.0, 1.0)
            dI = I_32F_level.reshape(h*w) - NL
            dI = dI.reshape(h, w)
            N_I = np.zeros_like(N)
            for i in range(3):
                N_I[:, :, i] = N[:, :, i] + dI[:, :] * L[i]
            return w_c, N_I
        return func

    def _silhouetteConstraint(self, N0_32F, A_8U, w_c=0.5):
        N0_level = image_solver.LevelImage(N0_32F)
        A0_level = image_solver.LevelImage(A_8U)

        def func(N):
            A_8U_level = A0_level.level(N)
            N0_32F_level = N0_level.level(N)

            N_sil = np.array(N)
            N_sil[A_8U_level == 0, :] = N0_32F_level[A_8U_level == 0, :]

            return w_c, N_sil
        return func

    def _postFunc(self):
        def func(N):
            N = normalizeImage(N, th=0.0)
            return N
        return func

    @timing_func
    def _optimize(self):
        I_32F = self._I0_32F
        h, w = I_32F.shape[:2]
        I = I_32F.reshape(h * w)

        L = self._L
        N0_32F = self._N0_32F
        N0 = N0_32F.reshape(-1, 3)

        NL = np.clip(np.dot(N0, L), 0.0, 1.0)

        I = self._estimateBrightness()

        I_32F = I.reshape(h, w)

        N = np.array(N0_32F)

        A_8U = self._A_8U

        solver_iter = image_solver.solveIterator([self._laplacianConstraint(),
                                                  self._brightnessConstraint(L, I_32F),
                                                  self._silhouetteConstraint(N0_32F, A_8U)],
                                                 [self._postFunc()])
        N = image_solver.solveMG(N, solver_iter, iterations=3)

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