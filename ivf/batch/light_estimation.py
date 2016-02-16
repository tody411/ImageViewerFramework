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


class LightEstimationBatch(DatasetBatch, CharacterBatch):
    def __init__(self, name="Shape From Shading", dataset_name="3dmodel"):
        super(LightEstimationBatch, self).__init__(name, dataset_name)

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
    LightEstimationBatch().runCharacters()