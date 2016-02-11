# -*- coding: utf-8 -*-
## @package ivf.batch.base_detail_separation
#
#  ivf.batch.base_detail_separation utility package.
#  @author      tody
#  @date        2016/02/10

import numpy as np
import cv2
import matplotlib.pyplot as plt

from ivf.batch.batch import DatasetBatch, CharacterBatch
from ivf.io_util.image import loadNormal, loadRGBA, loadRGB, saveNormal
from ivf.cv.image import to32F, setAlpha, luminance, alpha, rgb
from ivf.np.norm import normalizeVector
from ivf.core.shader.toon import ToonShader
from ivf.core.sfs.detail_layer import baseDetailSeparationGaussian, baseDetailSeparationBilateral,\
    baseDetailSeprationDOG, baseDetailSeparationMedian
from ivf.plot.window import SubplotGrid, showMaximize
from ivf.core.sfs.bump_mapping import bumpNormal
from ivf.cv.normal import normalToColor, normalizeImage
from ivf.core.sfs.amg_constraints import normalConstraints
from ivf.core.solver import amg_solver
from ivf.core.sfs import amg_constraints
from ivf.core.sfs.lumo import computeNz


class BaseDetailSeprationBatch(DatasetBatch, CharacterBatch):
    def __init__(self, name="BaseDetailSepration", dataset_name="3dmodel"):
        super(BaseDetailSeprationBatch, self).__init__(name, dataset_name)
        self._N_32F = None

    def _runImp(self):
        normal_data = loadNormal(self._data_file)

        if normal_data is None:
            return

        N0_32F, A_8U = normal_data

        A_32F = to32F(A_8U)

        L = normalizeVector(np.array([-0.2, 0.3, 0.7]))

        C0_32F = ToonShader().diffuseShading(L, N0_32F)
        # C0_32F = LambertShader().diffuseShading(L, N0_32F)

        self._runSepration(C0_32F)

    def _runSepration(self, C0_32F):

        I_32F = luminance(C0_32F)

        B_g, D_g = baseDetailSeparationGaussian(I_32F, sigma=10.0)
        B_b, D_b = baseDetailSeparationBilateral(I_32F, sigma_space=5.0, sigma_range=0.3)
        B_dog, D_dog = baseDetailSeprationDOG(I_32F, sigma=2.0)
        B_med, D_med = baseDetailSeparationMedian(I_32F, ksize=21)

        separations = [#["Gaussian", B_g, D_g],
                       #["DOG", B_dog, D_dog],
                    #["Median", B_med, D_med],
                       ["Bilateral", B_b, D_b]
                       ]

        for separation in separations:
            N0_32F = bumpNormal(separation[-1], scale=50.0, sigma=3.0)
            separation.append(normalToColor(N0_32F))

            th = 0.1
            h, w = N0_32F.shape[:2]
            W_32F = np.zeros((h, w))

            W_32F = 1.0 - N0_32F[:, :, 2]
            W_32F *= 1.0 / np.max(W_32F)

            W_32F = W_32F ** 1.5
            #W_32F[W_32F < th] = 0.0
            #W_32F[W_32F > th] = 1.0

            A_c, b_c = amg_constraints.normalConstraints(W_32F, N0_32F)

            A_L = amg_constraints.laplacianMatrix((h, w))
            A = 3.0 * A_c + A_L
            b = 3.0 * b_c

            N_32F = amg_solver.solve(A, b).reshape(h, w, 3)
            N_32F = computeNz(N_32F.reshape(-1, 3)).reshape(h, w, 3)
            N_32F = normalizeImage(N_32F)
            separation.append(normalToColor(N_32F))

            self._N_32F = N_32F

        # C0_32F = LambertShader().diffuseShading(L, N0_32F)

        fig, axes = plt.subplots(figsize=(12, 8))
        font_size = 15
        fig.subplots_adjust(left=0.05, right=0.95, top=0.9, hspace=0.12, wspace=0.05)
        fig.suptitle(self.name(), fontsize=font_size)

        num_rows = 1
        num_cols = len(separations) + 1
        plot_grid = SubplotGrid(num_rows, num_cols)

        for separation in separations:
            plot_grid.showImage(separation[-2], separation[0])
            plot_grid.showImage(separation[-1], separation[0])

        #showMaximize()

    def _runCharacterImp(self):
#         if self._character_name != "XMen":
#             return

        self._runLayer(self.fullLayerFile())

#         for layer_file in self.layerFiles():
#             self._runLayer(layer_file)

    def _runLayer(self, layer_file):
        if layer_file is None:
            return
        C0_8U = loadRGBA(layer_file)

        if C0_8U is None:
            C0_8U = loadRGB(layer_file)

        if C0_8U is None:
            return

        h, w = C0_8U.shape[:2]
        w_low = 256
        h_low = w_low * h / w

        #C0_8U = cv2.resize(C0_8U, (w_low, h_low))

        A_8U = alpha(C0_8U)

        C0_32F = to32F(rgb(C0_8U))

        if A_8U is not None:
            C0_32F[A_8U < 0.9 * np.max(A_8U), :] = np.array([0, 0, 0])

        self._runSepration(C0_32F)

        plt.savefig(self.characterResultFile("BumpNormal.png"))

        if self._N_32F is not None:
            saveNormal(self.characterResultFile("DetailNormal.png"), self._N_32F, A_8U)


if __name__ == '__main__':
    BaseDetailSeprationBatch().runCharacters()