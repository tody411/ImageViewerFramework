# -*- coding: utf-8 -*-
## @package ivf.ui.matplot_frame
#
#  ivf.ui.matplot_frame utility package.
#  @author      tody
#  @date        2016/02/11


from PyQt4.QtGui import *
from PyQt4.QtCore import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar


## Matplot Frame for pyqt.
class MatplotFrame(QWidget):

    ## Constructor
    def __init__(self):
        super(MatplotFrame, self).__init__()
        self._figure = plt.figure()
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1,
                            wspace=0.01, hspace=0.15)
        self._canvas = FigureCanvas(self._figure)
        self._toolbar = NavigationToolbar(self._canvas, self)
        self._updateFunc = None

        layout = QVBoxLayout()
        layout.addWidget(self._toolbar)
        layout.addWidget(self._canvas)
        self.setLayout(layout)
        self._canvas.setFocusPolicy(Qt.StrongFocus)
        self._canvas.setFocus()

    @property
    def figure(self):
        return self._figure

    @property
    def canvas(self):
        return self._canvas

    def initPlot(self, plotFunc):
        plotFunc(self._figure)

    def setUpdateFunc(self, updateFunc):
        self._updateFunc = updateFunc
        self.update()

    def updatePlot(self):
        self._canvas.draw()

    def drawPlots(self, plotFunc):
        self.biginPlot()
        plotFunc()
        self.endPlot()

    def biginPlot(self):
        self._figure.clear()

    def endPlot(self):
        self.updatePlot()
