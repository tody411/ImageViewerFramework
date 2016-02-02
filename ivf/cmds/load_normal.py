
# -*- coding: utf-8 -*-
## @package ivf.cmds.load_normal
#
#  ivf.cmds.load_normal utility package.
#  @author      tody
#  @date        2016/02/02

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import os

from ivf.cmds.base_cmds import BaseCommand
from ivf.io_util.image import loadRGBA, saveRGBA
from ivf.cv.normal import colorToNormal


class LoadNormalCommand(BaseCommand):
    def __init__(self, scene, image_file="", parent=None):
        super(LoadNormalCommand, self).__init__(scene, "Load Normal", parent)
        self._image_file = image_file
        self._show_ui = image_file is ""
        self._root_dir = os.path.expanduser('~')

    def _runImp(self):
        if self._show_ui:
            self._image_file = str(QFileDialog.getOpenFileName (None, "Open Normal Image File", self._root_dir, "Image File (*.png *.jpg *.bmp)" ))

        if self._image_file is "":
            return

        self._scene.setImageFile(self._image_file)
        N_32F = colorToNormal(self._scene.image())
        self._scene.setNormal(N_32F)
        self._input_info = self._image_file
        self._root_dir = os.path.dirname(self._image_file)