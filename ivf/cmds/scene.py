
# -*- coding: utf-8 -*-
## @package ivf.cmds.scene
#
#  ivf.cmds.scene utility package.
#  @author      tody
#  @date        2016/01/26


from PyQt4.QtGui import *
from PyQt4.QtCore import *

import os

from ivf.cmds.base_cmds import BaseCommand


class LoadSceneCommand(BaseCommand):
    def __init__(self, scene, scene_file="", parent=None):
        super(LoadSceneCommand, self).__init__(scene, "Load Scene", parent)
        self._scene_file = scene_file
        self._show_ui = scene_file is ""
        self._root_dir = os.path.expanduser('~')
        action = self.action()
        action.setShortcut("Ctrl+O")

    def _runImp(self):
        if self._show_ui:
            self._scene_file = str(QFileDialog.getOpenFileName (None, "Open Scene File", self._root_dir, "Scene File (*.json)" ))

        if self._scene_file is "":
            return

        self._scene.load(self._scene_file)
        self._input_info = self._scene_file
        self._root_dir = os.path.dirname(self._scene_file)


class SaveSceneCommand(BaseCommand):
    def __init__(self, scene, scene_file="", parent=None):
        super(SaveSceneCommand, self).__init__(scene, "Save Scene", parent)
        self._scene_file = scene_file
        self._show_ui = scene_file is ""
        self._root_dir = os.path.expanduser('~')
        action = self.action()
        action.setShortcut("Ctrl+S")

    def _runImp(self):
        if self._show_ui:
            self._scene_file = str(QFileDialog.getSaveFileName(None, "Save Scene File", self._root_dir, "Scene File (*.json)" ))

        self._scene.save(self._scene_file)
        self._input_info = self._scene_file