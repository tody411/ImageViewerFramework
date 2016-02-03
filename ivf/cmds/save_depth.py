
# -*- coding: utf-8 -*-
## @package ivf.cmds.save_depth
#
#  ivf.cmds.save_depth utility package.
#  @author      tody
#  @date        2016/02/02


from PyQt4.QtGui import *
from PyQt4.QtCore import *

import os

from ivf.cmds.base_cmds import BaseCommand
from ivf.scene.gl3d.image_plane import ImagePlane
from ivf.io_util.obj_model import saveOBJ


class SaveDepthCommand(BaseCommand):
    def __init__(self, scene, file_path="", parent=None):
        super(SaveDepthCommand, self).__init__(scene, "Save Depth Mesh", parent)
        self._file_path = file_path
        self._show_ui = file_path is ""
        self._root_dir = os.path.expanduser('~')

    def _runImp(self):
        if self._show_ui:
            self._file_path = str(QFileDialog.getSaveFileName(None, "Save Depth Mesh", self._root_dir, "Obj File (*.obj)" ))

        if self._file_path is "":
            return

        RGBA_8U = self._scene.image()
        D_32F = self._scene.depth()

        if D_32F is None:
            return

        model = ImagePlane(RGBA_8U)
        model.setDepth(D_32F)
        vertices = model.mesh().positions()
        index_array = model.mesh().indexArray()
        vertex_colors = model.mesh().vertexColors()

        saveOBJ(self._file_path, vertices, index_array, vertex_colors)