# -*- coding: utf-8 -*-
## @package ivf.cmds.base_cmds
#
#  ivf.cmds.base_cmds utility package.
#  @author      tody
#  @date        2016/01/25

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from ivf.util.timer import Timer


class BaseCommand(QObject):
    def __init__(self, scene, name="", parent=None):
        super(BaseCommand, self).__init__()
        self._name = name
        self._scene = scene
        self._input_info = ""
        self._output_info = ""
        self._action = None
        self._parent = parent

    def name(self):
        return self._name

    def action(self):
        if self._action is not None:
            return self._action

        def cmdFunc():
            self.run()

        self._action = QAction(self._name, self._parent)
        self._action.triggered.connect(cmdFunc)
        return self._action

    def run(self):
        timer = Timer(self._name)
        self._runImp()
        timer.stop()
        message = self._name + "(" + self._input_info + ")"
        if self._output_info is not "":
            message += "=> " + self._output_info
        message += ": " + str(timer.secs())
        self._scene.setMessage(message)

    def _runImp(self):
        pass