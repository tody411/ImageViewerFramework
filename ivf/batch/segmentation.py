# -*- coding: utf-8 -*-
## @package ivf.batch.segmentation
#
#  ivf.batch.segmentation utility package.
#  @author      tody
#  @date        2016/02/15

import numpy as np
import cv2
import matplotlib.pyplot as plt

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import sys
import os

from ivf.batch.batch import CharacterBatch
from ivf.io_util.image import loadRGBA
from ivf.ui.image_view import ImageView
from ivf.ui.tool.stroke_tool import StrokeTool
from ivf.cv.image import alpha, to32F, rgb
from ivf.scene.stroke import StrokeSets
from ivf.core.guided_filter.guided_filter import GuidedFilter
from ivf.np.norm import normVectors
from ivf.core.segmentation.kmeans import KMeans
from ivf.core.segmentation.edge_based_segmentation import EdgeBasedSegmentaiton


class SegmentationBatch(CharacterBatch):
    def __init__(self, view, tool, name="Segmentation", dataset_name="3dmodel"):
        super(SegmentationBatch, self).__init__(name, dataset_name)
        self._view = view
        self._tool = tool
        self._stroke_sets = StrokeSets()
        self._tool.setStrokeSets(self._stroke_sets)

    def _runCharacterImp(self):
        self._runLayer(self.fullLayerFile())

    def _runLayer(self, layer_file):
        C0_8U = loadRGBA(layer_file)

        if C0_8U is None:
            return

        if os.path.exists(self._segmentationFile()):
            self._stroke_sets.load(self._segmentationFile())
            self._tool.setStrokeSets(self._stroke_sets)
            self._view.update()
        else:
            self._tool.clearStrokeSets()

        self._computeSegmentaiton(C0_8U)
        #self._runUI(C0_8U)

    def _runUI(self, C0_8U):
        self._view.render(C0_8U)

    def _computeSegmentaiton(self, C0_8U):
        C_32F = to32F(rgb(C0_8U))

        label0 = np.zeros(C_32F.shape[:3], dtype=np.uint8)

        colors = []

        for stroke_set in self._stroke_sets.strokeSets():
            print stroke_set.color()
            color = np.array(stroke_set.color())[:3]
            colors.append(color)
            color = np.int32(255 * color)

            print type(color[0])

            for stroke in stroke_set.strokes():
                if stroke.empty():
                    continue
                points = stroke.points()
                points = np.int32(points)

                brush_size = int(stroke.brushSize())

                print color
                cv2.polylines(label0, [points], 0, (color[0], color[1], color[2]), brush_size)

        colors = np.array(colors)

#         h, w = label0.shape[:2]
#
#         w_low = 512
#         h_low = w_low * h / w
#
#         gauide_filter = GuidedFilter(cv2.resize(C_32F, (w_low, h_low)), radius=11, epsilon=0.05)
#
#         label0 = cv2.resize(label0, (w_low, h_low))
#         h, w = label0.shape[:2]
#         label = np.array(label0)
#
#         dc = np.zeros((len(colors), h * w), dtype=np.float32)
#
#         for i in xrange(5):
#             label = gauide_filter.filter(label)
#             label[label0 > 0] = label0[label0 > 0]
#
#         label_flat = label.reshape(-1, 3)
#
#         for ci, color in enumerate(colors):
#             dc[ci, :] = normVectors(label_flat - color)
#
#         centers = np.argmin(dc, axis=0)
#
#         label_flat = colors[centers]
#         label = label_flat.reshape(h, w, 3)

#         kmeans = KMeans(C0_8U, num_colors=20)
#         centerImage = kmeans.centerImage()
#         self._view.render(centerImage)
#
#         histImage = kmeans.histImage()
#
#         plt.imshow(histImage)
#         plt.show()

        edgeSeg = EdgeBasedSegmentaiton(C0_8U)
        labels = edgeSeg.labels()
        plt.imshow(labels)
        plt.show()

    def finishCharacter(self):
        if self._character_name != "":
            self._stroke_sets.save(self._segmentationFile())
        self.runCharacter()

    def _segmentationFile(self):
        return self.characterResultFile("segmentation.json")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ImageView()
    view.showMaximized()
    tool = StrokeTool()
    view.setTool(tool)
    batch = SegmentationBatch(view, tool)
    view.setReturnCallback(batch.finishCharacter)
    sys.exit(app.exec_())