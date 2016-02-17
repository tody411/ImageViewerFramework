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
from ivf.cv.image import to32F, alpha, rgb, luminance, setAlpha, trim
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
from ivf.io_util.video import saveVideo


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
        targets = ["Miku", "KenjiMiku", "SozaiMiku", "MikuFuwatoro"]
        if not self._character_name in targets:
            return

        self.cleanCharacterResultDir()

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

        initial_normals = ["N_lumo.png", "N0_d.png"]

        layer_name = os.path.splitext(os.path.basename(layer_file))[0]

        for initial_normal in initial_normals:
            N0_32F, AN_8U = loadNormal(self.characterResultFile(initial_normal, data_name="BaseDetailSepration"))
            N_32F, L, C_32F, M = self._runSFS(C0_32F, A_8U, N0_32F, AN_8U)

            L_img = lightSphere(L)

            M_img = M.mapImage()

            fig, axes = plt.subplots(figsize=(11, 5))
            font_size = 15
            fig.subplots_adjust(left=0.02, right=0.98, top=0.9, hspace=0.12, wspace=0.02)
            fig.suptitle(self.name(), fontsize=font_size)

            num_rows = 1
            num_cols = 4
            plot_grid = SubplotGrid(num_rows, num_cols)

            plot_grid.showImage(normalToColor(N0_32F, A_8U), r'Initial Normal: $N_0$')
            plot_grid.showImage(normalToColor(N_32F, A_8U), r'Estimated Normal: $N$')
            plot_grid.showImage(C0_8U, r'Shading: $C_0$')
            plot_grid.showImage(setAlpha(C_32F, A_32F), r'Recovered Shading: $C$')

            out_file_path = self.characterResultFile("ToonSFS" + initial_normal, layer_name=layer_name)
            plt.savefig(out_file_path)

            N_trim = trim(N_32F, A_8U)
            N0_trim = trim(N0_32F, A_8U)
            C0_trim = trim(C0_32F, A_8U)
            A_trim = trim(A_8U, A_8U)


            out_file_path = self.characterResultFile(initial_normal, layer_name=layer_name)
            saveNormal(out_file_path, N_trim, A_trim)

            images = self._relightingImages(N_trim, A_trim, M)

            initial_normal_name = os.path.splitext(initial_normal)[0]
            video_name = "Relighting" + initial_normal_name + ".wmv"
            out_file_path = self.characterResultFile(video_name, layer_name=layer_name)
            saveVideo(out_file_path, images)

            images = self._relightingOffsetImages(L, C0_trim, N0_trim, A_trim, M)
            video_name = "RelightingOffset" + initial_normal_name + ".wmv"
            out_file_path = self.characterResultFile(video_name, layer_name=layer_name)
            saveVideo(out_file_path, images)


#         plot_grid.showImage(L_img, r'Light: $L$')
#
#         plot_grid.showImage(I_32F, r'Luminance: $I$')
#         plot_grid.showImage(M_img, r'Color Map: $M$')


    def _lightAnimation(self):
        ts = np.linspace(0.0, 1.0, 120)

        L_start = np.array([-0.6, 0.3, 0.7])
        L_end = np.array([0.6, 0.2, 0.7])

        Ls = []
        for t in ts:
            L = normalizeVector((1.0 - t) * L_start + t * L_end)
            Ls.append(L)
        return Ls

    def _relightingImages(self, N_32F, A_8U, M):
        Ls = self._lightAnimation()
        h, w = N_32F.shape[:2]
        images = []
        for L in Ls:
            LdN = LdotN(L, N_32F)

            C = M.shading(LdN.flatten()).reshape(h, w, -1)
            C[A_8U < 0.5 * np.max(A_8U), :] = 0
            images.append(C)
        return images

    def _relightingOffsetImages(self, L0, C0_32F, N_32F, A_8U, M):
        Cs = C0_32F.reshape(-1, 3)

        I0 = M.illumination(Cs)
        I0_32F = np.float32(I0.reshape(C0_32F.shape[:2]))
        I0_32F = cv2.bilateralFilter(I0_32F, 0, 0.1, 3)
        I0 = I0_32F.flatten()
        LdN0 = LdotN(L0, N_32F).flatten()

        dI = I0 - LdN0

        Ls = self._lightAnimation()
        h, w = N_32F.shape[:2]
        images = []
        for L in Ls:
            LdN = LdotN(L, N_32F).flatten()

            C = M.shading(LdN + dI).reshape(h, w, -1)
            C[A_8U < 0.5 * np.max(A_8U), :] = 0
            images.append(C)
        return images


    def _runSFS(self, C0_32F, A_8U, N0_32F, AN_8U):
        I0_32F = luminance(C0_32F)
        L = lightEstimation(I0_32F, N0_32F, A_8U)

        LdN = LdotN(L, N0_32F)

        layer_area = A_8U > 0.5 * np.max(A_8U)
        Cs = C0_32F[layer_area].reshape(-1, 3)
        Is = LdN[layer_area].flatten()

        M = ColorMapEstimation(Cs, Is)

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

        return N_32F, L, C_32F, M


if __name__ == '__main__':
    ToonSFSBatch().runCharacters()
