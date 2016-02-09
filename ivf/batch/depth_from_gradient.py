# -*- coding: utf-8 -*-
## @package ivf.batch.depth_from_gradient
#
#  ivf.batch.depth_from_gradient utility package.
#  @author      tody
#  @date        2016/02/08

import numpy as np
import cv2
import matplotlib.pyplot as plt

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import sys

from ivf.batch.batch import DatasetBatch
from ivf.io_util.image import loadNormal
from ivf.cv.image import to32F, luminance, setAlpha
from ivf.np.norm import normalizeVector
from ivf.core.shader.toon import ToonShader
from ivf.core.sfs.depth_from_gradient import depthFromGradient
from ivf.core.sfs.depth_to_normal import depthToNormal
from ivf.plot.window import SubplotGrid, showMaximize
from ivf.cv.normal import normalToColor
from ivf.core.shader.lambert import LambertShader
from ivf.ui.model_view import ModelView


class DepthFromGradientBatch(DatasetBatch):
    def __init__(self, view, name="Depth From Gradient", dataset_name="3dmodel"):
        super(DepthFromGradientBatch, self).__init__(name, dataset_name)
        self._view = view

    def _runImp(self):
        normal_data = loadNormal(self._data_file)

        if normal_data is None:
            return

        N0_32F, A_8U = normal_data
        A_32F = to32F(A_8U)

        L = normalizeVector(np.array([-0.2, 0.3, 0.7]))

        #C0_32F = ToonShader().diffuseShading(L, N0_32F)
        C0_32F = LambertShader().diffuseShading(L, N0_32F)
        I0_32F = luminance(C0_32F)

        I0_low_32F = cv2.resize(I0_32F, (256, 256))
        A_low_8U = cv2.resize(A_8U, I0_low_32F.shape)

        D_32F = depthFromGradient(I0_low_32F, A_low_8U)
        D_32F = cv2.resize(D_32F, I0_32F.shape)
        N_32F = depthToNormal(D_32F)

        self._view.setRGBAD(setAlpha(C0_32F, A_32F), D_32F)

#         fig, axes = plt.subplots(figsize=(11, 5))
#         font_size = 15
#         fig.subplots_adjust(left=0.05, right=0.95, top=0.9, hspace=0.12, wspace=0.05)
#         fig.suptitle(self.name(), fontsize=font_size)
#
#         num_rows = 1
#         num_cols = 4
#         plot_grid = SubplotGrid(num_rows, num_cols)
#
#         plot_grid.showImage(setAlpha(C0_32F, A_32F), r'Input Shading: $C$')
#         plot_grid.showImage(normalToColor(N0_32F, A_8U), r'Ground Truth Normal: $N_g$')
#         plot_grid.showImage(D_32F, r'Estimated Depth: $D$')
#         plot_grid.showImage(normalToColor(N_32F, A_8U), r'Estimated Normal: $N$')
#
#         showMaximize()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ModelView()
    batch = DepthFromGradientBatch(view)

    view.setReturnCallback(batch.runNext)
    view.show()
    sys.exit(app.exec_())