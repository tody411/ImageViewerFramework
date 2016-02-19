# -*- coding: utf-8 -*-
## @package ivf.core.sfs.toon_sfs
#
#  ivf.core.sfs.toon_sfs utility package.
#  @author      tody
#  @date        2016/02/16
import numpy as np
import cv2

from ivf.core.sfs.sfs import ShapeFromShading
from ivf.util.timer import timing_func
from ivf.core.shader.shader import LdotN
from ivf.core.sfs.colormap_estimation import ColorMapEstimation
from ivf.core.solver import image_solver
from ivf.core.sfs import image_constraints


class ToonSFS(ShapeFromShading):
    def __init__(self, L=None, C_32F=None, A_8U=None):
        super(ToonSFS, self).__init__("ToonSFS", L, C_32F, A_8U)
        self._N0_32F = None
        self._iterations = 20

    def setInitialNormal(self, N0_32F):
        self._N0_32F = N0_32F

    def setNumIterations(self, iterations):
        self._iterations = iterations

    def _runImp(self):
        self._optimize()



    @timing_func
    def _optimize(self):
        L = self._L
        N0_32F = self._N0_32F
        C0_32F = self._C0_32F

        LdN = LdotN(L, N0_32F)

        A_8U = self._A_8U
        layer_area = A_8U > 0.5 * np.max(A_8U)
        Cs = C0_32F[layer_area].reshape(-1, 3)
        Is = LdN[layer_area].flatten()

        M = ColorMapEstimation(Cs, Is)

        I_recovered = M.illumination(Cs)
        I_32F = np.zeros(LdN.shape)
        I_32F[:] = np.min(I_recovered)
        I_32F[layer_area] = I_recovered

        sigma = 1.0
        I_32F = cv2.GaussianBlur(I_32F, (0, 0), sigma)
        I_lap = cv2.Laplacian(np.float32(I_32F), cv2.CV_32F, ksize=1)
        I_lap = np.abs(I_lap)
        W_32F = I_lap
        W_32F *= 1.0 / np.max(W_32F)
        W_32F = W_32F ** 1.5 + 0.01
        W_32F *= 1.0 / np.max(W_32F)
        #W_32F = np.zeros(I_32F.shape)

        constraints = []
        #W_32F = np.ones(N0_32F.shape[:2])
        # constraints.append(image_constraints.normalConstraints(W_32F, N0_32F, w_c=0.01))
        constraints.append(image_constraints.laplacianConstraints(w_c=0.05))
        constraints.append(image_constraints.brightnessConstraintsWithWeight(W_32F, L, I_32F, w_c=1.0))
        constraints.append(image_constraints.silhouetteConstraints(A_8U, w_c=0.05))

        N_32F = np.array(N0_32F, dtype=np.float64)

        solver_iter = image_solver.solveIterator(constraints,
                                                 [image_constraints.postNormalize(th=0.0)])
        N_32F = image_solver.solveMG(N_32F, solver_iter, iterations=self._iterations)

        self._N_32F = N_32F

        LdN = LdotN(L, N_32F)

        I_32F[layer_area] = LdN[layer_area]

        self._C_32F = M.shading(I_32F.flatten()).reshape(self._C0_32F.shape)