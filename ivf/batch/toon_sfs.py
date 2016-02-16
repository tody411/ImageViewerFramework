# -*- coding: utf-8 -*-
## @package ivf.batch.toon_sfs
#
#  ivf.batch.toon_sfs utility package.
#  @author      tody
#  @date        2016/02/16

import numpy as np
import cv2
import matplotlib.pyplot as plt

import os

from ivf.batch.batch import DatasetBatch, CharacterBatch
from ivf.io_util.image import loadNormal, saveNormal, loadRGBA
from ivf.np.norm import normalizeVector
from ivf.cv.image import to32F, alpha, rgb, luminance, setAlpha
from ivf.core.shader.toon import ToonShader
from ivf.core.sfs.pr_sfs import Wu08SFS
from ivf.core.shader.light_sphere import lightSphere
from ivf.core.sfs.light_estimation import lightEstimation, lightEstimationLaplacian, lightEstimationByVoting
from ivf.plot.window import SubplotGrid, showMaximize
from ivf.cv.normal import normalToColor
from ivf.core.shader.half_lambert import HalfLambertShader
from ivf.core.sfs.colormap_estimation import ColorMapEstimation
from ivf.core.shader.shader import LdotN
from ivf.core.sfs.toon_sfs import ToonSFS


class ToonSFSBatch(DatasetBatch, CharacterBatch):
    def __init__(self, name="ToonSFS", dataset_name="3dmodel"):
        super(ToonSFSBatch, self).__init__(name, dataset_name)

    def _runImp(self):
        normal_data = loadNormal(self._data_file)

        if normal_data is None:
            return

        N0_32F, A_8U = normal_data

        #N0_32F = cv2.resize(N0_32F, (64, 64))
        #A_8U = cv2.resize(A_8U, N0_32F.shape[:2])

        A_32F = to32F(A_8U)

        L = normalizeVector(np.array([-0.2, 0.3, 0.7]))

        C0_32F = ToonShader().diffuseShading(L, N0_32F)
        # C0_32F = LambertShader().diffuseShading(L, N0_32F)

        sfs_method = Wu08SFS(L, C0_32F, A_8U)
        sfs_method.run()
        N_32F = sfs_method.normal()

        saveNormal(self.resultFile(self._data_file_name, result_name="Wu08"), N_32F, A_8U)

    def _runCharacterImp(self):
        if self._character_name != "MikuFuwatoro":
            return

        for layer_file in self.layerFiles():
            self._runLayer(layer_file)

    def _runLayer(self, layer_file):
        C0_8U = loadRGBA(layer_file)

        if C0_8U is None:
            return

        A_8U = alpha(C0_8U)

        if A_8U is None:
            return

        A_32F = to32F(A_8U)

        C0_32F = to32F(rgb(C0_8U))
        I0_32F = luminance(C0_32F)
        N0_32F, AN_8U = loadNormal(self.characterResultFile("N0_d.png", data_name="BaseDetailSepration"))

        L = lightEstimation(I0_32F, N0_32F, A_8U)
        L_img = lightSphere(L)

        LdN = LdotN(L, N0_32F)

        layer_area = A_8U > 0.5 * np.max(A_8U)
        Cs = C0_32F[layer_area].reshape(-1, 3)
        Is = LdN[layer_area].flatten()

        M = ColorMapEstimation(Cs, Is)
        M_img = M.mapImage()

        I_const = M.illumination(Cs)
        I_32F = np.array(I0_32F)
        I_32F[layer_area] = I_const
        I_32F[A_8U < 0.5 * np.max(A_8U)] = np.min(I_const)

        toon_sfs = ToonSFS(L, C0_32F, A_8U)
        toon_sfs.setInitialNormal(N0_32F)
        toon_sfs.run()

        N_32F = toon_sfs.normal()
        LdN_recovered = LdotN(L, N_32F)
        LdN_recovered[A_8U < 0.5 * np.max(A_8U)] = np.min(LdN_recovered)

        Is = LdN_recovered[layer_area].flatten()

        Cs_recovered = M.shading(Is)

        C_32F = np.array(C0_32F)
        C_32F[layer_area, :] = Cs_recovered

        fig, axes = plt.subplots(figsize=(11, 5))
        font_size = 15
        fig.subplots_adjust(left=0.02, right=0.98, top=0.9, hspace=0.12, wspace=0.02)
        fig.suptitle(self.name(), fontsize=font_size)

        num_rows = 1
        num_cols = 4
        plot_grid = SubplotGrid(num_rows, num_cols)

#         plot_grid.showImage(L_img, r'Light: $L$')
#
#         plot_grid.showImage(I_32F, r'Luminance: $I$')
#         plot_grid.showImage(M_img, r'Color Map: $M$')
        plot_grid.showImage(normalToColor(N0_32F, A_8U), r'Initial Normal: $N_0$')
        plot_grid.showImage(normalToColor(N_32F, A_8U), r'Estimated Normal: $N$')
        plot_grid.showImage(C0_8U, r'Shading: $C_0$')
        plot_grid.showImage(setAlpha(C_32F, A_32F), r'Recovered Shading: $C$')

        out_file_path = self.characterResultFile(os.path.basename(layer_file))
        plt.savefig(out_file_path)

if __name__ == '__main__':
    ToonSFSBatch().runCharacters()
