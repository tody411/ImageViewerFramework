# -*- coding: utf-8 -*-
## @package ivf.cmds.window.depth_view
#
#  ivf.cmds.window.depth_view utility package.
#  @author      tody
#  @date        2016/02/01


import cv2

from ivf.cmds.base_cmds import BaseCommand

from ivf.cv.image import alpha
from ivf.ui.glview import GLView
from ivf.ui.editor.parameter_editor import ParameterEditor


class DepthViewCommand(BaseCommand):
    def __init__(self, scene, parent=None):
        super(DepthViewCommand, self).__init__(scene, "Depth View Command", parent)
        self._view = None

    def _runImp(self):
        D_32F = self._scene.depth()

        if D_32F is None:
            return

        image = self._scene.image()
        A_8U = alpha(image)

        if A_8U is None:
            return

        self._view = GLView()
        self._view.setRGBAD(image, D_32F)
        self._view.show()
#         A_8U = cv2.resize(A_8U, None, fx=0.25, fy=0.25)
#         N0_32F, N_32F = estimateNormal(A_8U)
#
#         h, w = image.shape[:2]
#         N_32F = cv2.resize(N_32F, (w, h))
#         self._scene.setNormal(N_32F)
#         self._scene.setDisplayMode(Scene.DisplayNormal)