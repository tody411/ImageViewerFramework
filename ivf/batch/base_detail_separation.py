# -*- coding: utf-8 -*-
## @package ivf.batch.base_detail_separation
#
#  ivf.batch.base_detail_separation utility package.
#  @author      tody
#  @date        2016/02/10

import numpy as np
import cv2
import matplotlib.pyplot as plt

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import sys

from ivf.batch.batch import DatasetBatch, CharacterBatch
from ivf.io_util.image import loadNormal, loadRGBA, loadRGB, saveNormal
from ivf.cv.image import to32F, setAlpha, luminance, alpha, rgb
from ivf.np.norm import normalizeVector
from ivf.core.shader.toon import ToonShader
from ivf.core.sfs.detail_layer import baseDetailSeparationGaussian, baseDetailSeparationBilateral,\
    baseDetailSeprationDOG, baseDetailSeparationMedian
from ivf.plot.window import SubplotGrid, showMaximize
from ivf.core.sfs.bump_mapping import bumpNormal, bumpMapping
from ivf.cv.normal import normalToColor, normalizeImage
from ivf.core.sfs.amg_constraints import normalConstraints
from ivf.core.solver import amg_solver
from ivf.core.sfs import amg_constraints
from ivf.core.sfs.lumo import computeNz
from ivf.core.shader.lambert import LambertShader
from ivf.ui.image_view import ImageView
from ivf.ui.editor.parameter_editor import ParameterEditor


class BaseDetailSeprationBatch(DatasetBatch, CharacterBatch):
    def __init__(self, parameters, view, name="BaseDetailSepration", dataset_name="3dmodel"):
        super(BaseDetailSeprationBatch, self).__init__(name, dataset_name)
        self._parameters = parameters
        self._parameters["sigmaSpace"].valueChanged.connect(self._computeBaseDetalSeparation)
        self._parameters["sigmaRange"].valueChanged.connect(self._computeBaseDetalSeparation)
        self._parameters["bumpScale"].valueChanged.connect(self._computeInitialDetailNormal)
        self._view = view

        self._N_32F = None
        self._A_8U = None
        self._N0_b_32F = None
        self._N0_d_32F = None
        self._N_lumo = None
        self._C0_32F = None
        self._D = None
        self._N_b = None
        self._N_b_smooth = None

        self._N_d = None
        self._N_d_smooth = None

    def _runImp(self):
        normal_data = loadNormal(self._data_file)

        if normal_data is None:
            return

        N0_32F, A_8U = normal_data

        A_32F = to32F(A_8U)

        L = normalizeVector(np.array([-0.2, 0.3, 0.7]))

        # C0_32F = ToonShader().diffuseShading(L, N0_32F)
        C0_32F = LambertShader().diffuseShading(L, N0_32F)
        self._C0_32F = C0_32F

        self._loadImage()

    def _computeBaseDetalSeparation(self):
        sigma_space, sigma_range = self._parameters["sigmaSpace"], self._parameters["sigmaRange"]
        C0_32F = self._C0_32F
        I_32F = luminance(C0_32F)
        B_b, D_b = baseDetailSeparationBilateral(I_32F, sigma_space=sigma_space.value(), sigma_range=sigma_range.value())
        self._D = D_b
        self._N_b = bumpNormal(B_b, scale=1.0, sigma=1.0)
        self._N_d = bumpNormal(D_b, scale=1.0, sigma=1.0)
        self._view.render(D_b)

    def _computeInitialDetailNormal(self):
        bump_scale = self._parameters["bumpScale"].value()

        self._N_b[:, :, :2] *= bump_scale
        self._N_b = normalizeImage(self._N_b, th=1.0)

        self._N_d[:, :, :2] *= bump_scale
        self._N_d = normalizeImage(self._N_d, th=1.0)

        self._view.render(normalToColor(self._N_b))

    def _computeDetailNormal(self, N0_32F):
        h, w = N0_32F.shape[:2]
        W_32F = np.zeros((h, w))

#         sigma_d = 2.0 * np.max(N0_32F[:, :, 2])
#         W_32F = 1.0 - np.exp( - (N0_32F[:, :, 2] ** 2) / (sigma_d ** 2))

        W_32F = 1.0 - N0_32F[:, :, 2]
        W_32F *= 1.0 / np.max(W_32F)
        W_32F = W_32F ** 1.5

        A_c, b_c = amg_constraints.normalConstraints(W_32F, N0_32F)

        A_L = amg_constraints.laplacianMatrix((h, w))

        lambda_d = 2.0
        A = A_c + lambda_d * A_L
        b = b_c

        N_32F = amg_solver.solve(A, b).reshape(h, w, 3)
        N_32F = computeNz(N_32F.reshape(-1, 3)).reshape(h, w, 3)
        N_32F = normalizeImage(N_32F)
        return N_32F

    def computeDetailNormal(self):
        self._N_b_smooth = self._computeDetailNormal(self._N_b)
        self._N_d_smooth = self._computeDetailNormal(self._N_d)

    def _computeLumoNormal(self):
        A_8U = self._A_8U

        if A_8U is None:
            return

        h, w = A_8U.shape[:2]
        A_c, b_c = amg_constraints.silhouetteConstraints(A_8U)

        A_L = amg_constraints.laplacianMatrix((h, w))
        A = 3.0 * A_c + A_L
        b = 3.0 * b_c

        N_32F = amg_solver.solve(A, b).reshape(h, w, 3)
        N_32F = computeNz(N_32F.reshape(-1, 3)).reshape(h, w, 3)
        N_32F = normalizeImage(N_32F)
        self._N_lumo = np.array(N_32F)

    def computeInitialNormal(self):
        if self._N_lumo.shape != self._N_b_smooth.shape:
            return
        self._N0_b_32F = normalizeImage(bumpMapping(np.array(self._N_lumo), self._N_b_smooth))
        self._N0_d_32F = normalizeImage(bumpMapping(np.array(self._N_lumo), self._N_d_smooth))


    def _loadImage(self):
        C0_32F = self._C0_32F
        I_32F = luminance(C0_32F)

        self._view.render(I_32F)
        return

#         B_g, D_g = baseDetailSeparationGaussian(I_32F, sigma=10.0)
#         B_b, D_b = baseDetailSeparationBilateral(I_32F, sigma_space=5.0, sigma_range=0.3)
#         B_dog, D_dog = baseDetailSeprationDOG(I_32F, sigma=2.0)
#         B_med, D_med = baseDetailSeparationMedian(I_32F, ksize=21)
#
#         separations = [#["Gaussian", B_g, D_g],
#                        #["DOG", B_dog, D_dog],
#                     #["Median", B_med, D_med],
#                        ["Bilateral", B_b, D_b]
#                        ]

#         for separation in separations:
#             N0_32F = bumpNormal(separation[-1], scale=50.0, sigma=3.0)
#             separation.append(normalToColor(N0_32F))
#
#             th = 0.1
#             h, w = N0_32F.shape[:2]
#             W_32F = np.zeros((h, w))
#
#             W_32F = 1.0 - N0_32F[:, :, 2]
#             W_32F *= 1.0 / np.max(W_32F)
#
#             W_32F = W_32F ** 1.5
#             #W_32F[W_32F < th] = 0.0
#             #W_32F[W_32F > th] = 1.0
#
#             A_c, b_c = amg_constraints.normalConstraints(W_32F, N0_32F)
#
#             A_L = amg_constraints.laplacianMatrix((h, w))
#             A = 3.0 * A_c + A_L
#             b = 3.0 * b_c
#
#             N_32F = amg_solver.solve(A, b).reshape(h, w, 3)
#             N_32F = computeNz(N_32F.reshape(-1, 3)).reshape(h, w, 3)
#             N_32F = normalizeImage(N_32F)
#             separation.append(normalToColor(N_32F, self._A_8U))
#
#             self._N_32F = N_32F

        # C0_32F = LambertShader().diffuseShading(L, N0_32F)

#         fig, axes = plt.subplots(figsize=(12, 8))
#         font_size = 15
#         fig.subplots_adjust(left=0.05, right=0.95, top=0.9, hspace=0.12, wspace=0.05)
#         fig.suptitle(self.name(), fontsize=font_size)
#
#         num_rows = 1
#         num_cols = len(separations) + 1
#         plot_grid = SubplotGrid(num_rows, num_cols)
#
#         for separation in separations:
#             plot_grid.showImage(separation[-2], separation[0])
#             plot_grid.showImage(separation[-1], separation[0])
#
#         showMaximize()

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
        w_low = 1024
        h_low = w_low * h / w

        #  C0_8U = cv2.resize(C0_8U, (w_low, h_low))

        A_8U = alpha(C0_8U)
        self._A_8U = A_8U

        C0_32F = to32F(rgb(C0_8U))

        if A_8U is not None:
            C0_32F[A_8U < 0.9 * np.max(A_8U), :] = np.array([0, 0, 0])

        self._C0_32F = C0_32F

        self._loadImage()
        self._computeBaseDetalSeparation()
        self._computeInitialDetailNormal()
        self.computeDetailNormal()
        self._computeLumoNormal()
        self.computeInitialNormal()

        # plt.savefig(self.characterResultFile("BumpNormal.png"))

        if self._N_b_smooth is not None:
            self.cleanCharacterResultDir()
            saveNormal(self.characterResultFile("N_b.png"), self._N_b, A_8U)
            saveNormal(self.characterResultFile("N_b_smooth.png"), self._N_b_smooth, A_8U)
            saveNormal(self.characterResultFile("N_d.png"), self._N_d, A_8U)
            saveNormal(self.characterResultFile("N_d_smooth.png"), self._N_d_smooth, A_8U)
            saveNormal(self.characterResultFile("N_lumo.png"), self._N_lumo, A_8U)
            saveNormal(self.characterResultFile("N0_b.png"), self._N0_b_32F, A_8U)
            saveNormal(self.characterResultFile("N0_d.png"), self._N0_d_32F, A_8U)

    def finishCharacter(self):
        if self._character_name != "":
            pass

        self.runCharacter()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ImageView()
    view.showMaximized()
    editor = ParameterEditor()
    editor.addFloatParameter("sigmaSpace", min_val=1.0, max_val=30.0, default_val=5.0)
    editor.addFloatParameter("sigmaRange", min_val=0.0, max_val=1.0, default_val=0.3)
    editor.addFloatParameter("bumpScale", min_val=10.0, max_val=50.0, default_val=20.0)

    batch = BaseDetailSeprationBatch(editor.parameters(), view)
    editor.addButton("Compute Silhouette Normal", cmd_func=batch.computeInitialNormal)
    editor.addButton("Compute Detail Normal", cmd_func=batch.computeDetailNormal)

    editor.show()

    #view.setReturnCallback(batch.finishCharacter)
    batch.runCharacters()
    sys.exit(app.exec_())
