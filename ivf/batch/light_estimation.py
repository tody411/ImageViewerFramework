# -*- coding: utf-8 -*-
## @package ivf.batch.light_estimation
#
#  ivf.batch.light_estimation utility package.
#  @author      tody
#  @date        2016/02/12

import numpy as np
import cv2
import matplotlib.pyplot as plt

from ivf.batch.batch import DatasetBatch, CharacterBatch
from ivf.io_util.image import loadRGBA, loadNormal
from ivf.cv.image import alpha, to32F, rgb, luminance, setAlpha
from ivf.plot.window import SubplotGrid, showMaximize
from ivf.cv.normal import normalToColor
from ivf.core.sfs.light_estimation import lightEstimation, lightEstimationLaplacian, lightEstimationByVoting
from ivf.core.shader.light_sphere import lightSphere
from ivf.datasets.colormap import colorMapFiles, loadColorMap
from ivf.core.shader.toon import ColorMapShader
from ivf.np.norm import normalizeVector
from ivf.datasets.shape import shapeResultFile


class LightEstimationBatch(DatasetBatch, CharacterBatch):
    def __init__(self, name="Shape From Shading", dataset_name="3dmodel"):
        super(LightEstimationBatch, self).__init__(name, dataset_name)

    def _runImp(self):
        N0_file = shapeResultFile(result_name="InitialNormal", data_name=self._data_name)
        N0_data = loadNormal(N0_file)

        N0_32F, A_8U = N0_data

        Ng_data = loadNormal(self._data_file)
        Ng_32F, A_8U = Ng_data

        for colormap_file in colorMapFiles():
            self._runColorMap(colormap_file, Ng_32F, N0_32F, A_8U)

    def _runColorMap(self, colormap_file, Ng_32F, N0_32F, A_8U):
        M_32F = loadColorMap(colormap_file)

        L0 = normalizeVector(np.array([-0.2, 0.3, 0.6]))
        L0_img = lightSphere(L0)
        L0_txt = 0.01 * np.int32(100 * L0)

        C0_32F = ColorMapShader(M_32F).diffuseShading(L0, Ng_32F)
        I_32F = luminance(C0_32F)

        L = lightEstimation(I_32F, N0_32F, A_8U)

        L_txt = 0.01 * np.int32(100 * L)
        L_img = lightSphere(L)

        fig, axes = plt.subplots(figsize=(11, 5))
        font_size = 15
        fig.subplots_adjust(left=0.05, right=0.95, top=0.9, hspace=0.12, wspace=0.05)
        fig.suptitle(self.name(), fontsize=font_size)

        num_rows = 1
        num_cols = 4
        plot_grid = SubplotGrid(num_rows, num_cols)

        plot_grid.showImage(setAlpha(C0_32F, A_8U), r'Input image: $\mathbf{c}$', font_size=font_size)
        plot_grid.showImage(normalToColor(N0_32F, A_8U), r'Initial normal: $\mathbf{N}_0$')
        plot_grid.showImage(L0_img, r'Ground trugh light: $L_g = (%s, %s, %s)$' %(L0_txt[0], L0_txt[1], L0_txt[2]))
        plot_grid.showImage(L_img, r'Estimated light: $L = (%s, %s, %s)$' %(L_txt[0], L_txt[1], L_txt[2]))

        showMaximize()


    def _runCharacterImp(self):
        if self._character_name != "KenjiMiku":
            return
        # self._runLayer(self.fullLayerFile())

        for layer_file in self.layerFiles():
            self._runLayer(layer_file)

    def _runLayer(self, layer_file):
        C0_8U = loadRGBA(layer_file)

        if C0_8U is None:
            return

        A_8U = alpha(C0_8U)

        if A_8U is None:
            return

        C0_32F = to32F(rgb(C0_8U))
        I_32F = luminance(C0_32F)

        N0_32F, A_8U = loadNormal(self.characterResultFile("N0_d.png", data_name="BaseDetailSepration"))
        Nd_32F, A_8U = loadNormal(self.characterResultFile("N_d_smooth.png", data_name="BaseDetailSepration"))
        Nb_32F, A_8U = loadNormal(self.characterResultFile("N_b_smooth.png", data_name="BaseDetailSepration"))

        W_32F = np.array(Nb_32F[:, :, 2])
        W_32F = W_32F
        W_32F[W_32F < 0.95] = 0.0

        L = lightEstimation(I_32F, N0_32F, A_8U)
        # L = lightEstimationByVoting(I_32F, N0_32F, A_8U)

        L_txt = 0.01 * np.int32(100 * L)

        L_img = lightSphere(L)

        fig, axes = plt.subplots(figsize=(11, 5))
        font_size = 15
        fig.subplots_adjust(left=0.05, right=0.95, top=0.9, hspace=0.12, wspace=0.05)
        fig.suptitle(self.name(), fontsize=font_size)

        num_rows = 1
        num_cols = 4
        plot_grid = SubplotGrid(num_rows, num_cols)

        plot_grid.showImage(C0_8U, r'$C$')
        plot_grid.showImage(normalToColor(N0_32F, A_8U), r'$N$')
        plot_grid.showImage(setAlpha(C0_32F, W_32F), r'$Nd_z$')
        plot_grid.showImage(L_img, r'$L: [%s, %s, %s]$' %(L_txt[0], L_txt[1], L_txt[2]))

        showMaximize()

if __name__ == '__main__':
    LightEstimationBatch().run()