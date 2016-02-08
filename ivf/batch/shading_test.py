
# -*- coding: utf-8 -*-
## @package ivf.batch.shading_test
#
#  ivf.batch.shading_test utility package.
#  @author      tody
#  @date        2016/02/05


import numpy as np
import matplotlib.pyplot as plt

from ivf.batch.batch import DatasetBatch
from ivf.cv.normal import normalToColor
from ivf.plot.window import showMaximize

from ivf.core.shader import half_lambert, lambert
from ivf.np.norm import normalizeVector
from ivf.cv.image import gray2rgb, setAlpha, to32F, trim
from ivf.io_util.image import loadNormal


class ShadingTestBatch(DatasetBatch):
    def __init__(self, name="ShadingTest", dataset_name="3dmodel"):
        super(ShadingTestBatch, self).__init__(name, dataset_name)

    def _runImp(self):
        normal_data = loadNormal(self._data_file)

        if normal_data is None:
            return

        N_32F, A_8U = normal_data

        N_32F = trim(N_32F, A_8U)
        A_8U = trim(A_8U, A_8U)
        A_32F = to32F(A_8U)

        L = normalizeVector(np.array([-0.2, 0.3, 0.7]))

        I_half = half_lambert.diffuse(N_32F, L)
        I_half = setAlpha(gray2rgb(I_half), A_32F)

        I_lambert = lambert.diffuse(N_32F, L)
        I_lambert = setAlpha(gray2rgb(I_lambert), A_32F)

        fig, axes = plt.subplots(figsize=(11, 5))

        font_size = 15

        fig.subplots_adjust(left=0.05, right=0.95, top=0.9, hspace=0.05, wspace=0.05)
        fig.suptitle("Depth From Normal", fontsize=font_size)

        plt.subplot(1, 4, 1)
        plt.title(r'Normal: $N$')
        plt.imshow(normalToColor(N_32F, A_8U))
        plt.axis('off')

        plt.subplot(1, 4, 2)
        plt.title(r'Half Lambert: $I_h$')
        plt.imshow(I_half)
        plt.axis('off')

        plt.subplot(1, 4, 3)
        plt.title(r'Lambert: $I_l$')
        plt.imshow(I_lambert)
        plt.axis('off')

        showMaximize()
        #plt.savefig(self.resultFile(self._data_file_name))



if __name__ == '__main__':
    ShadingTestBatch().run()