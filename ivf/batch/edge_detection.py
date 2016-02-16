# -*- coding: utf-8 -*-
## @package ivf.batch.edge_detection
#
#  ivf.batch.edge_detection utility package.
#  @author      tody
#  @date        2016/02/15

import numpy as np
import cv2
import matplotlib.pyplot as plt

from ivf.batch.batch import DatasetBatch, CharacterBatch
from ivf.io_util.image import loadRGBA
from ivf.cv.image import alpha, to32F, rgb, luminance, setAlpha, rgb2Lab
from ivf.core.edge_detection.dog import DoG
from ivf.plot.window import SubplotGrid, showMaximize
from ivf.core.edge_detection.dom import DoM


class EdgeDetectionBatch(DatasetBatch, CharacterBatch):
    def __init__(self, name="EdgeDetection", dataset_name="3dmodel"):
        super(EdgeDetectionBatch, self).__init__(name, dataset_name)

    def _runCharacterImp(self):
        self._runLayer(self.fullLayerFile())

    def _runLayer(self, layer_file):
        C0_8U = loadRGBA(layer_file)

        if C0_8U is None:
            return

        A_8U = alpha(C0_8U)

#         if A_8U is None:
#             return

        C0_32F = to32F(rgb(C0_8U))
        I_32F = luminance(C0_32F)

        Lab_32F = rgb2Lab(C0_32F)

        th_specular = 0.2
        th_contour = 0.02
        th_material = 0.1
        E_32F = DoG(I_32F, sigma=2.0)

        contour = th_contour * np.min(E_32F) - E_32F
        contour *= 1.0 / np.max(contour)
        contour = np.clip(contour, 0.0, 1.0)
        specular = E_32F - th_specular * np.max(E_32F)
        specular *= 1.0 / np.max(specular)
        specular = np.clip(specular, 0.0, 1.0)

        material = rgb(C0_8U)
#         edge_mask = np.zeros(I_32F.shape, dtype=np.uint8)
#         edge_mask[contour > 0.0] = 1.0
#         material = cv2.inpaint(material, edge_mask, 3, cv2.INPAINT_TELEA)

        for i in xrange(1):
            material = cv2.medianBlur(material, ksize=7)
#         material = th_material * np.max(np.abs(E_32F)) - np.abs(E_32F)
#         material *= 1.0 / np.max(material)
#         material = np.clip(material, 0.0, 1.0)
#         material[material > 0.0] = 1.0
        E_32F[E_32F < 0.0] = 0.0

        fig, axes = plt.subplots(figsize=(11, 5))
        font_size = 15
        fig.subplots_adjust(left=0.05, right=0.95, top=0.9, hspace=0.12, wspace=0.05)
        fig.suptitle(self.name(), fontsize=font_size)

        num_rows = 1
        num_cols = 4
        plot_grid = SubplotGrid(num_rows, num_cols)

        plot_grid.showImage(C0_8U, r'$C$')
        #plot_grid.showImage(setAlpha(C0_32F, material), r'$Material$')
        plot_grid.showImage(setAlpha(material, A_8U), r'$Material$')
        plot_grid.showImage(setAlpha(C0_32F, contour), r'$Contour$')
        plot_grid.showImage(setAlpha(C0_32F, specular), r'$Specular$')

        showMaximize()

if __name__ == '__main__':
    EdgeDetectionBatch().runCharacters()