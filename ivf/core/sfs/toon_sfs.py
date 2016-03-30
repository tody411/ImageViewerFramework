# -*- coding: utf-8 -*-
## @package ivf.core.sfs.toon_sfs
#
#  ivf.core.sfs.toon_sfs utility package.
#  @author      tody
#  @date        2016/02/16
import numpy as np
import cv2
import matplotlib.pyplot as plt

from ivf.core.sfs.sfs import ShapeFromShading
from ivf.util.timer import timing_func
from ivf.core.shader.shader import LdotN
from ivf.core.sfs.colormap_estimation import ColorMapEstimation
from ivf.core.solver import image_solver
from ivf.core.sfs import image_constraints
from ivf.core.edge_detection.dog import DoG


class ToonSFS(ShapeFromShading):
    def __init__(self, L=None, C_32F=None, A_8U=None):
        super(ToonSFS, self).__init__("ToonSFS", L, C_32F, A_8U)
        self._N0_32F = None
        self._iterations = 40
        self._w_lap = 5.0
        self._Cini_32F = C_32F
        self._M = None

    def setInitialNormal(self, N0_32F):
        self._N0_32F = N0_32F

    def setNumIterations(self, iterations):
        self._iterations = iterations

    def setWeights(self, w_lap=5.0):
        self._w_lap = w_lap

    def initialShading(self):
        return self._Cini_32F

    def colorMap(self):
        return self._M

    def relighting(self, L):
        N_32F = self._N_32F
        LdN = LdotN(L, N_32F)

        return self._M.shading(LdN.flatten()).reshape(self._C0_32F.shape)

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

        self._Cini_32F = M.shading(LdN.flatten()).reshape(self._C0_32F.shape)

        I_recovered = M.illumination(Cs)
        I_32F = np.zeros(LdN.shape)
        I_32F[:] = np.min(I_recovered)
        I_32F[layer_area] = I_recovered

        I_dog = DoG(I_32F, sigma=2.0)
        sigma = 2.0
        I_32F = np.float32(cv2.GaussianBlur(I_32F, (0, 0), sigma))
        I_lap = -cv2.Laplacian(np.float32(I_32F), cv2.CV_32F, ksize=1)

        I_lap = np.abs(I_lap)

        I_lap_median = np.median(I_lap[layer_area])
        print "I_lap_mean", np.mean(I_lap[layer_area])
        print "I_lap_median", np.median(I_lap[layer_area])

        sigma = 0.05
        epsilon = 0.0 * I_lap_median
        w_min = 0.05
        w_max = 1.0

        W_32F = w_min + (w_max - w_min) * (1.0 - np.exp(- (I_lap - epsilon) ** 2 / (sigma ** 2)))
        W_32F = w_min * np.ones(I_32F.shape[:2])
        W_32F[I_lap < epsilon] = w_min
        W_32F[I_lap > epsilon] = w_max

        W_32F[:, :] = 1.0

        constraints = []
        #W_32F = np.ones(N0_32F.shape[:2])
        #constraints.append(image_constraints.normalConstraints(W_32F, N0_32F, w_c=0.05))

        w_lap = self._w_lap
        constraints.append(image_constraints.laplacianConstraints(w_c=w_lap))
        constraints.append(image_constraints.brightnessConstraints(L, I_32F, w_c=1.0))
        constraints.append(image_constraints.gradientConstraints(L, I_32F, w_c=0.2))

        w_sil = 0.4 * w_lap
        constraints.append(image_constraints.silhouetteConstraints(A_8U, w_c=w_sil))

        N_32F = np.array(N0_32F, dtype=np.float64)

        solver_iter = image_solver.solveIterator(constraints,
                                                [image_constraints.postNormalize(th=0.0)])
                                                #[image_constraints.postComputeNz()])
        N_32F = image_solver.solveMG(N_32F, solver_iter, iterations=self._iterations)

        self._N_32F = N_32F

        LdN = LdotN(L, N_32F)

        I_32F[layer_area] = LdN[layer_area]

        self._C_32F = M.shading(I_32F.flatten()).reshape(self._C0_32F.shape)
        self._M = M