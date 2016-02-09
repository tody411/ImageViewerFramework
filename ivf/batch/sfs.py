# -*- coding: utf-8 -*-
## @package ivf.batch.sfs
#
#  ivf.batch.sfs utility package.
#  @author      tody
#  @date        2016/02/05

import numpy as np
import cv2
import matplotlib.pyplot as plt

from ivf.batch.batch import DatasetBatch
from ivf.io_util.image import loadNormal
from ivf.cv.image import to32F, setAlpha, trim, gray2rgb
from ivf.np.norm import normalizeVector
from ivf.core.sfs.pr_sfs import Wu08SFS
from ivf.core.shader.lambert import lambertShading, diffuse, LambertShader
from ivf.cv.normal import normalToColor
from ivf.plot.window import showMaximize, SubplotGrid
from ivf.core.sfs.angle_error import angleErros
from ivf.core.shader.toon import ToonShader


class NormalInfoBatch(DatasetBatch):
    def __init__(self, name="Normal Information", dataset_name="3dmodel"):
        super(NormalInfoBatch, self).__init__(name, dataset_name)

    def _runImp(self):
        normal_data = loadNormal(self._data_file)

        if normal_data is None:
            return

        N0_32F, A_8U = normal_data
        A_32F = to32F(A_8U)
        N0_32F = trim(N0_32F, A_8U)
        A_32F = trim(A_32F, A_8U)
        A_8U = trim(A_8U, A_8U)

        L = normalizeVector(np.array([0.5, -0.2, 0.7]))
        I0_32F = diffuse(N0_32F, L)

        Ix = cv2.Sobel(I0_32F, cv2.CV_64F, 1, 0, ksize=1)
        Ix = cv2.GaussianBlur(Ix, (0, 0), 3.0)
        Ixx = cv2.Sobel(Ix, cv2.CV_64F, 1, 0, ksize=1)
        Ixx = cv2.GaussianBlur(Ixx, (0, 0), 5.0)
        Iy = -cv2.Sobel(I0_32F, cv2.CV_64F, 0, 1, ksize=1)
        Iy = cv2.GaussianBlur(Iy, (0, 0), 3.0)
        Iyy = -cv2.Sobel(Iy, cv2.CV_64F, 0, 1, ksize=1)
        Iyy = cv2.GaussianBlur(Iyy, (0, 0), 5.0)

        fig, axes = plt.subplots(figsize=(11, 5))
        font_size = 15
        fig.subplots_adjust(left=0.05, right=0.95, top=0.9, hspace=0.12, wspace=0.05)
        fig.suptitle(self.name(), fontsize=font_size)

        num_rows = 2
        num_cols = 4
        plot_grid = SubplotGrid(num_rows, num_cols)

        Nx = cv2.Sobel(N0_32F[:, :, 0], cv2.CV_64F, 1, 0, ksize=1)
        Nx = cv2.GaussianBlur(Nx, (0, 0), 3.0)
        Nxx = cv2.Sobel(Nx, cv2.CV_64F, 1, 0, ksize=1)
        Nxx = cv2.GaussianBlur(Nxx, (0, 0), 5.0)
        Ny = -cv2.Sobel(N0_32F[:, :, 1], cv2.CV_64F, 0, 1, ksize=1)
        Ny = cv2.GaussianBlur(Ny, (0, 0), 3.0)
        Nyy = -cv2.Sobel(Ny, cv2.CV_64F, 0, 1, ksize=1)
        Nyy = cv2.GaussianBlur(Nyy, (0, 0), 5.0)

        plot_grid.showColorMap(N0_32F[:, :, 0], r'$N_{x}$', v_min=-0.01, v_max=0.01)
        plot_grid.showColorMap(N0_32F[:, :, 1], r'$N_{y}$', v_min=-0.01, v_max=0.01)
        plot_grid.showColorMap(Nx, r'$N_{xx}$', v_min=-0.01, v_max=0.01)
        plot_grid.showColorMap(Ny, r'$N_{yy}$', v_min=-0.01, v_max=0.01)
        #plot_grid.showColorMap(Nx + Ny, r'$N_{xx} + N_{yy}$', v_min=-0.01, v_max=0.01)

#         Ixx[Ixx>0] = 1.0
#         Ixx[Ixx<0] = -1.0
#         Iyy[Iyy>0] = 1.0
#         Iyy[Iyy<0] = -1.0
        plot_grid.showColorMap(-Ix, r'$I_{x}$', v_min=-0.001, v_max=0.001)
        plot_grid.showColorMap(-Iy, r'$I_{y}$', v_min=-0.001, v_max=0.001)
        plot_grid.showColorMap(-Ixx, r'$I_{xx}$', v_min=-0.001, v_max=0.001)
        plot_grid.showColorMap(-Iyy, r'$I_{yy}$', v_min=-0.001, v_max=0.001)
        #plot_grid.showColorMap(-Ixx - Iyy, r'$I_{xx} + I_{yy}$', v_min=-0.01, v_max=0.01)
        #plot_grid.showColorMap(Iy, r'$I_{y}$')

        showMaximize()


class SFSBatch(DatasetBatch):
    def __init__(self, name="Shape From Shading", dataset_name="3dmodel"):
        super(SFSBatch, self).__init__(name, dataset_name)

    def _runImp(self):
        if self._data_name != "Man":
            return
        normal_data = loadNormal(self._data_file)

        if normal_data is None:
            return

        N0_32F, A_8U = normal_data

        #N0_32F = cv2.resize(N0_32F, (64, 64))
        #A_8U = cv2.resize(A_8U, N0_32F.shape[:2])

        A_32F = to32F(A_8U)

        L = normalizeVector(np.array([-0.2, 0.3, 0.7]))

        # C0_32F = ToonShader().diffuseShading(L, N0_32F)
        C0_32F = LambertShader().diffuseShading(L, N0_32F)

        sfs_method = Wu08SFS(L, C0_32F, A_8U)
        sfs_method.run()
        N_32F = sfs_method.normal()

        C_error = sfs_method.shadingError()
        I_32F = sfs_method.brightness()
        I_32F = gray2rgb(I_32F)
        C_32F = sfs_method.shading()

        N0_32F = trim(N0_32F, A_8U)
        C0_32F = trim(C0_32F, A_8U)
        C_32F = trim(C_32F, A_8U)
        N_32F = trim(N_32F, A_8U)
        C_error = trim(C_error, A_8U)
        I_32F = trim(I_32F, A_8U)
        A_32F = trim(A_32F, A_8U)
        A_8U = trim(A_8U, A_8U)

        h, w = N_32F.shape[:2]
        N_error = angleErros(N_32F.reshape(-1, 3), N0_32F.reshape(-1, 3)).reshape(h, w)
        N_error[A_8U < np.max(A_8U)] = 0.0

        fig, axes = plt.subplots(figsize=(11, 5))
        font_size = 15
        fig.subplots_adjust(left=0.05, right=0.95, top=0.9, hspace=0.12, wspace=0.05)
        fig.suptitle(self.name(), fontsize=font_size)

        num_rows = 2
        num_cols = 3
        plot_grid = SubplotGrid(num_rows, num_cols)

        plot_grid.showImage(normalToColor(N0_32F, A_8U), r'Ground Truth Normal: $N_g$')
        plot_grid.showImage(normalToColor(N_32F, A_8U), r'Estimated Normal: $N$')
        plot_grid.showColorMap(N_error, r'Angle Error: $N_g, N$', v_min=0, v_max=30.0)

        plot_grid.showImage(setAlpha(C0_32F, A_32F), r'Shading: $C$')
        plot_grid.showImage(setAlpha(C_32F, A_32F), r'Estimated Shading: $C$')
        plot_grid.showColorMap(C_error, r'Shading Error: $C_g, C$', v_min=0, v_max=0.1)

        showMaximize()

if __name__ == '__main__':
    SFSBatch().run()