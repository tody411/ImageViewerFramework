

# -*- coding: utf-8 -*-
## @package ivf.batch.depth_normal
#
#  ivf.batch.depth_normal utility package.
#  @author      tody
#  @date        2016/02/05

import numpy as np
import matplotlib.pyplot as plt

from ivf.batch.batch import DatasetBatch
from ivf.io_util.image import loadNormal
from ivf.core.sfs.depth_from_normal import depthFromNormal
from ivf.cv.normal import normalToColor
from ivf.plot.window import showMaximize
from ivf.core.sfs.depth_to_normal import depthToNormal
from ivf.core.sfs.angle_error import angleErros


class DepthFromNormalBatch(DatasetBatch):
    def __init__(self, name="DepthFromNormal", dataset_name="3dmodel"):
        super(DepthFromNormalBatch, self).__init__(name, dataset_name)

    def _runImp(self):
        # file_path = self._data_file
        file_path = self.resultFile(self._data_file_name, result_name="Wu08")
        normal_data = loadNormal(file_path)

        if normal_data is None:
            return

        N0_32F, A_8U = normal_data

        D_32F = depthFromNormal(N0_32F, A_8U)

        fig, axes = plt.subplots(figsize=(11, 5))

        font_size = 15

        fig.subplots_adjust(left=0.05, right=0.95, top=0.9, hspace=0.05, wspace=0.05)
        fig.suptitle("Depth From Normal", fontsize=font_size)

        plt.subplot(1, 4, 1)
        plt.title(r'Initial Normal: $N_0$')
        plt.imshow(normalToColor(N0_32F, A_8U))
        plt.axis('off')

        plt.subplot(1, 4, 2)
        plt.title(r'Estimated Depth: $D$')
        plt.gray()
        plt.imshow(D_32F)
        plt.axis('off')

        N_32F = depthToNormal(D_32F)
        plt.subplot(1, 4, 3)
        plt.title(r'Recovered Normal: $N$')
        plt.imshow(normalToColor(N_32F, A_8U))
        plt.axis('off')

        h, w = N_32F.shape[:2]
        N_diff = angleErros(N_32F.reshape(-1, 3), N0_32F.reshape(-1, 3)).reshape(h, w)
        N_diff[A_8U < np.max(A_8U)] = 0.0
        plt.subplot(1, 4, 4)
        plt.title(r'Angle Error: $N, N_0$')
        plt.imshow(N_diff, cmap=plt.cm.jet, vmin=0, vmax=30.0)
        plt.axis('off')

        plt.colorbar()

        #out_file_path = self.resultFile(self._data_file_name)
        out_file_path = self.resultFile(self._data_file_name, result_name="Wu08Depth")
        plt.savefig(out_file_path)



if __name__ == '__main__':
    DepthFromNormalBatch().run()