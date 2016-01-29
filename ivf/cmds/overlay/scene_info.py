# -*- coding: utf-8 -*-
## @package ivf.cmds.overlay.scene_info
#
#  ivf.cmds.overlay.scene_info utility package.
#  @author      tody
#  @date        2016/01/27

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from ivf.cmds.overlay.overlay_cmd import OverlayCommand


class SceneInfoOverlayCommand(OverlayCommand):
    def __init__(self, scene, view, parent=None):
        super(SceneInfoOverlayCommand, self).__init__(scene, view, "Scene Info", parent)

    def _viewOverlayImp(self, painter):
        painter.setFont(QFont("Arial", 13, QFont.Bold))
        painter.setPen(QColor(230, 230, 240))



        text = "Scene Info:\n"

        if self._scene.image() is not None:
            h, w, cs = self._scene.image().shape[:3]
            text += "  Image Size: (%s, %s, %s)" %(w, h, cs)

        x = 10
        y = 10

        painter.drawText(QRectF(x, y, 400, 400), text)
