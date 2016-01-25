
# -*- coding: utf-8 -*-
## @package ivf.cmds.image
#
#  ivf.cmds.image utility package.
#  @author      tody
#  @date        2016/01/25

from ivf.cmds.base_cmds import BaseCommand
from ivf.io_util.image import loadRGBA, saveRGBA


class LoadImageCommand(BaseCommand):
    def __init__(self, scene, image_file=""):
        super(LoadImageCommand, self).__init__(scene, "Load Image")
        self._image_file = image_file

    def _runImp(self):
        image = loadRGBA(self._image_file)
        self._scene.setImage(image)
        self._input_info = self._image_file


class SaveImageCommand(BaseCommand):
    def __init__(self, scene, image_file=""):
        super(SaveImageCommand, self).__init__(scene, "Save Image")
        self._image_file = image_file

    def _runImp(self):
        image = self._scene.image()
        saveRGBA(self._image_file, image)
        self._input_info = self._image_file
