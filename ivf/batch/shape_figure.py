# -*- coding: utf-8 -*-
## @package ivf.batch.shape_figure
#
#  ivf.batch.shape_figure utility package.
#  @author      tody
#  @date        2016/02/18

import numpy as np
import cv2
import matplotlib.pyplot as plt
import os

from ivf.datasets.shape import shapeFiles, shapeResultsDir, shapeFile
from ivf.io_util.image import loadRGBA, loadNormal
from ivf.plot.window import SubplotGrid
from ivf.datasets.colormap import colorMapFile, loadColorMap
from ivf.core.shader.toon import ColorMapShader
from ivf.np.norm import normalizeVector
from ivf.cv.image import setAlpha, trim, to32F


def stylizedShadingFigure():
    target_shapes = ["Man", "Ogre", "Grog", "Vase"]
    target_shapes = [shapeFile(shape_name) for shape_name in target_shapes]

    target_colormaps = [1, 5, 10, 3]
    target_colormaps = [colorMapFile(cmap_id) for cmap_id in target_colormaps]

    fig, axes = plt.subplots(figsize=(12, 4))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, hspace=0.1, wspace=0.1)
    fig.suptitle("", fontsize=font_size)

    num_rows = 1
    num_cols = 4
    plot_grid = SubplotGrid(num_rows, num_cols)

    Ls = []
    Ls.append(normalizeVector(np.array([-0.5, 0.3, 0.7])))
    Ls.append(normalizeVector(np.array([0.2, -0.35, 0.4])))
    Ls.append(normalizeVector(np.array([-0.2, 0.6, 0.3])))
    Ls.append(normalizeVector(np.array([-0.2, 0.6, 0.3])))


    for shape_file, colormap_file, L in zip(target_shapes, target_colormaps, Ls):
        N_32F, A_8U = loadNormal(shape_file)
        M_32F = loadColorMap(colormap_file)
        C_32F = ColorMapShader(M_32F).diffuseShading(L, N_32F)
#         C_32F = trim(C_32F, A_8U)
#         A_8U = trim(A_8U, A_8U)
        C_32F = setAlpha(C_32F, to32F(A_8U))

#         h, w = C_32F.shape[:2]
#
#         h_t = 512
#         w_t = w * h_t / h
#         C_32F = cv2.resize(C_32F, (w_t, h_t))
        plot_grid.showImage(C_32F, "", alpha_clip=True)

    file_path = os.path.join(shapeResultsDir(), "StylizedShading.png")
    fig.savefig(file_path, transparent=True)


def shapeFigure():
    fig, axes = plt.subplots(figsize=(10, 8))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, hspace=0.1, wspace=0.1)
    fig.suptitle("", fontsize=font_size)

    num_rows = 4
    num_cols = 5
    plot_grid = SubplotGrid(num_rows, num_cols)

    for shape_file in shapeFiles():
        N_8U = loadRGBA(shape_file)
        plot_grid.showImage(N_8U, "")

    file_path = os.path.join(shapeResultsDir(), "3DModels.png")
    fig.savefig(file_path, transparent=True)

if __name__ == '__main__':
    stylizedShadingFigure()