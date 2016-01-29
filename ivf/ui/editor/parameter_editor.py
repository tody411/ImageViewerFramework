
# -*- coding: utf-8 -*-
## @package ivf.ui.editor.parameter_editor
#
#  ivf.ui.editor.parameter_editor utility package.
#  @author      tody
#  @date        2016/01/29

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ivf.ui.editor.numeric_editor import IntSliderGroup, FloatSliderGroup, BoolEditor, EnumEditor


class Parameter:
    ## Constructor
    def __init__(self, name, val, dtype=None):
        self._name = name
        self._val = val
        self._dtype = dtype

    def name(self):
        return self._name

    def value(self):
        return self._val

    def setValue(self, val):
        if self._dtype is not None:
            val = self._dtype(val)
        self._val = val
        print self._name, ": ", self._val


# Numeric slider group.
class ParameterEditor(QWidget):
    valueChanged = pyqtSignal(float)

    ui_maximumHeight = 50
    valueEditMaximumWidth = 100
    epsilon = 1e-6

    ## Constructor
    def __init__(self):
        super(ParameterEditor, self).__init__()

        self._parameters = {}
        self._layout = None
        self._createUI()

    def parameters(self):
        return self._parameters

    def parameter(self, name):
        return self._parameters[name]

    def addIntParameter(self, name="", min_val=0, max_val=100, default_val=0):
        ui = IntSliderGroup(name, min_val, max_val, default_val)
        self._layout.addWidget(ui)
        self._parameters[name] = Parameter(name, default_val, int)
        ui.valueChanged.connect(self._parameters[name].setValue)

    def addFloatParameter(self, name="",
                           min_val=0.0, max_val=1.0, default_val=0.0):
        ui = FloatSliderGroup(name, min_val, max_val, default_val)
        self._layout.addWidget(ui)
        self._parameters[name] = Parameter(name, default_val, float)
        ui.valueChanged.connect(self._parameters[name].setValue)

    def addBoolParameter(self, name="", default_val=False):
        ui = BoolEditor(name, default_val)
        self._layout.addWidget(ui)
        self._parameters[name] = Parameter(name, default_val)
        ui.valueChanged.connect(self._parameters[name].setValue)

    def addEnumParameter(self, name="", items=["v1", "v2", "v3"], default_val="v1"):
        ui = EnumEditor(name, items, default_val)
        self._layout.addWidget(ui)
        self._parameters[name] = Parameter(name, default_val)
        ui.valueChanged.connect(self._parameters[name].setValue)

    def _createUI(self):
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    editor = ParameterEditor()
    editor.addIntParameter("IntParam")
    editor.addFloatParameter("FloatParam")
    editor.addBoolParameter("BoolParam")
    editor.addEnumParameter("EnumParam")
    editor.show()
    end = app.exec_()