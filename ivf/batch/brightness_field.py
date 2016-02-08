
# -*- coding: utf-8 -*-
## @package ivf.batch.brightness_field
#
#  ivf.batch.brightness_field utility package.
#  @author      tody
#  @date        2016/02/08

import numpy as np
import cv2
import matplotlib.pyplot as plt

from ivf.batch.batch import DatasetBatch
from ivf.io_util.image import loadNormal
from ivf.cv.image import to32F, luminance
from ivf.np.norm import normalizeVector
from ivf.core.shader.toon import ToonShader
from ivf.core.sfs.brightness_field import BrightnessField
from ivf.plot.window import SubplotGrid, showMaximize
from ivf.cv.normal import normalToColor
from ivf.core.shader.lambert import LambertShader


class BrightnessFieldBatch(DatasetBatch):
    def __init__(self, name="Brightness Field", dataset_name="3dmodel"):
        super(BrightnessFieldBatch, self).__init__(name, dataset_name)

    def _runImp(self):
        normal_data = loadNormal(self._data_file)

        if normal_data is None:
            return

        N0_32F, A_8U = normal_data
        A_32F = to32F(A_8U)

        L = normalizeVector(np.array([-0.2, 0.4, 0.7]))

        C0_32F = LambertShader().diffuseShading(L, N0_32F)
        I_32F = luminance(C0_32F)

        br_field = BrightnessField(I_32F, sigma=5.0)
        I_smooth_32F = br_field.smoothBrightness()
        dI = br_field.brightnessDifference()
        gx, gy = br_field.gradients()

        N_32F = br_field.field()

        fig, axes = plt.subplots(figsize=(11, 5))
        font_size = 15
        fig.subplots_adjust(left=0.05, right=0.95, top=0.9, hspace=0.12, wspace=0.05)
        fig.suptitle(self.name(), fontsize=font_size)

        num_rows = 2
        num_cols = 4
        plot_grid = SubplotGrid(num_rows, num_cols)
        plot_grid.showImage(I_32F, r'$I$')
        plot_grid.showColorMap(dI, r'$dI$')
        plot_grid.showColorMap(gx, r'$gx$')
        plot_grid.showColorMap(gy, r'$gy$')

        plot_grid.showImage(normalToColor(N_32F, A_8U), r'$N$')
        plot_grid.showImage(N_32F[:, :, 2], r'$N_z$')

        showMaximize()

if __name__ == '__main__':
    BrightnessFieldBatch().run()