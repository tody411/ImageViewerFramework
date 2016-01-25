# -*- coding: utf-8 -*-
## @package ivf.cmds.base_cmds
#
#  ivf.cmds.base_cmds utility package.
#  @author      tody
#  @date        2016/01/25

from ivf.util.timer import Timer


class BaseCommand(object):
    def __init__(self, scene, name=""):
        self._name = name
        self._scene = scene
        self._input_info = ""
        self._output_info = ""

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