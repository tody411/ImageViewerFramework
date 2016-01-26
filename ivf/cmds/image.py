
# -*- coding: utf-8 -*-
## @package ivf.cmds.image
#
#  ivf.cmds.image utility package.
#  @author      tody
#  @date        2016/01/25

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import os

from ivf.cmds.base_cmds import BaseCommand
from ivf.io_util.image import loadRGBA, saveRGBA


class LoadImageCommand(BaseCommand):
    def __init__(self, scene, image_file="", parent=None):
        super(LoadImageCommand, self).__init__(scene, "Load Image", parent)
        self._image_file = image_file
        self._show_ui = image_file is ""
        self._root_dir = os.path.expanduser('~')
        action = self.action()
        action.setShortcut("Ctrl+I")

    def _runImp(self):
        if self._show_ui:
            self._image_file = str(QFileDialog.getOpenFileName (None, "Open Image File", self._root_dir, "Image File (*.png *.jpg *.bmp)" ))

        if self._image_file is "":
            return

        self._scene.setImageFile(self._image_file)
        self._input_info = self._image_file
        self._root_dir = os.path.dirname(self._image_file)


class SaveImageCommand(BaseCommand):
    def __init__(self, scene, image_file="", parent=None):
        super(SaveImageCommand, self).__init__(scene, "Save Image", parent)
        self._image_file = image_file
        self._show_ui = image_file is ""
        self._root_dir = os.path.expanduser('~')
        action = self.action()
        action.setShortcut("Ctrl+E")

    def _runImp(self):
        if self._show_ui:
            self._image_file = str(QFileDialog.getSaveFileName(None, "Save Image File", self._root_dir, "Image File (*.png *.jpg *.bmp)" ))

        image = self._scene.image()
        saveRGBA(self._image_file, image)
        self._input_info = self._image_file
