# -*- coding: utf-8 -*-
## @package ivf.cmds.resize
#
#  ivf.cmds.resize utility package.
#  @author      tody
#  @date        2016/01/26


from PyQt4.QtGui import *
from PyQt4.QtCore import *

import cv2

from ivf.cmds.base_cmds import BaseCommand


class ResizeImageCommand(BaseCommand):
    def __init__(self, scene, scales, name, parent=None):
        super(ResizeImageCommand, self).__init__(scene, name, parent)
        self._scales = scales

    def _runImp(self):
        image = self._scene.image()
        fx, fy = self._scales

        image_new = cv2.resize(image, None, fx=fx, fy=fy)
        self._scene.setImage(image_new)
