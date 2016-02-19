# -*- coding: utf-8 -*-
## @package ivf.batch.colormap_figure
#
#  ivf.batch.colormap_figure utility package.
#  @author      tody
#  @date        2016/02/18

import numpy as np
import cv2
import matplotlib.pyplot as plt

import os

from ivf.datasets.colormap import colorMapFiles, colorMapFile, loadColorMap, colorMapResultsDir
from ivf.io_util.image import loadRGB
from ivf.np.norm import normalizeVector
from ivf.core.shader.light_sphere import normalSphere
from ivf.core.shader.toon import ColorMapShader
from ivf.cv.image import setAlpha, to8U
from ivf.plot.window import SubplotGrid, showMaximize


def colorMapRename():
    cmap_id = 0

    for colormap_file in colorMapFiles():
        if os.path.exists(colorMapFile(cmap_id)):
            cmap_id += 1
            continue

        os.rename(colormap_file, colorMapFile(cmap_id))
        cmap_id += 1


def colorMapFigure():
    L = normalizeVector(np.array([-0.2, 0.3, 0.7]))
    N_32F, A_32F = normalSphere(h=512, w=512)

    fig, axes = plt.subplots(figsize=(6, 4))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, hspace=0.1, wspace=0.1)
    fig.suptitle("", fontsize=font_size)

    num_rows = 4
    num_cols = 6
    plot_grid = SubplotGrid(num_rows, num_cols)

    for colormap_file in colorMapFiles():
        M_32F = loadColorMap(colormap_file)
        C_32F = ColorMapShader(M_32F).diffuseShading(L, N_32F)
        plot_grid.showImage(setAlpha(C_32F, A_32F), "")

    file_path = os.path.join(colorMapResultsDir(), "ColorMapMaterials.png")
    fig.savefig(file_path, transparent=True)


if __name__ == '__main__':
    colorMapRename()
    colorMapFigure()