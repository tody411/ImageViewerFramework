
# -*- coding: utf-8 -*-
## @package ivf.cmds.quit
#
#  ivf.cmds.quit utility package.
#  @author      tody
#  @date        2016/01/25

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from ivf.cmds.base_cmds import BaseCommand


class QuitCommand(BaseCommand):
    def __init__(self, scene, parent=None):
        super(QuitCommand, self).__init__(scene, "&Close", parent)
        action = self.action()
        action.setShortcut("Ctrl+W")

    def _runImp(self):
        QApplication.closeAllWindows()
