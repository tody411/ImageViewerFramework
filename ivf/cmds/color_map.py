# -*- coding: utf-8 -*-
## @package ivf.cmds.color_map
#
#  ivf.cmds.color_map utility package.
#  @author      tody
#  @date        2016/02/18


import numpy as np
import cv2
import matplotlib.pyplot as plt

import os

from ivf.cmds.base_cmds import BaseCommand
from ivf.ui.tool.stroke_tool import StrokeTool
from ivf.cv.image import rgb, to8U, to32F

from ivf.core.sfs.colormap_estimation import ColorMapEstimation
from ivf.ui.matplot_frame import MatplotFrame
from ivf.datasets.colormap import colorMapFile
from ivf.io_util.image import saveImage


class ColorMapCommand(BaseCommand):
    def __init__(self, scene, view, parent=None):
        super(ColorMapCommand, self).__init__(scene, "ColrMap", parent)
        self._view = view
        self._tool = StrokeTool()
        self._tool.setStrokeEditedCallBack(self._strokeEdited)

        self._matplot_view = MatplotFrame()
        self._matplot_view.show()

        self._cmap_id = 0
        self._newColorMapID()
        print self._cmap_id
        print self._currentColorMapFile()

    def _runImp(self):
        stroke_sets = self._scene.strokeSets()
        self._tool.setStrokeSets(stroke_sets)
        self._view.setTool(self._tool)

    def _strokeEdited(self, stroke_sets):

        image = self._scene.image()

        C_32F = to32F(rgb(image))

        for stroke_set in stroke_sets.strokeSets():
            for stroke in stroke_set.strokes():
                if stroke.empty():
                    continue

                mask = np.zeros(image.shape[:2], dtype=np.uint8)
                points = stroke.points()
                points = np.int32(points)

                brush_size = int(stroke.brushSize())
                cv2.polylines(mask, [points], 0, 255, brush_size)

                Cs = C_32F[mask > 0, :]
                Is = np.arange(len(Cs), dtype=np.float32)

                Is = np.array(Is)
                Cs = np.array(Cs)
                M = ColorMapEstimation(Cs, Is, num_samples=1000)

                M_img = M.mapImage(image_size=(256, 32))

                def plotFunc():
                    plt.imshow(M_img)

                self._matplot_view.drawPlots(plotFunc)

                saveImage(self._currentColorMapFile(), M_img)
                self._newColorMapID()

    def _newColorMapID(self):
        while os.path.exists(colorMapFile(self._cmap_id)):
            self._cmap_id += 1

    def _currentColorMapFile(self):
        return colorMapFile(self._cmap_id)