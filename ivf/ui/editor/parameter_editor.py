
# -*- coding: utf-8 -*-
## @package ivf.ui.editor.parameter_editor
#
#  ivf.ui.editor.parameter_editor utility package.
#  @author      tody
#  @date        2016/01/29

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ivf.ui.editor.numeric_editor import IntSliderGroup, FloatSliderGroup, BoolEditor, EnumEditor


class Parameter(QObject):
    valueChanged = pyqtSignal(object)

    ## Constructor
    def __init__(self, name, val, dtype=None):
        super(Parameter, self).__init__()
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
        self.valueChanged.emit(self._val)


def _nullFunc():
    pass


# Numeric slider group.
class ParameterEditor(QWidget):
    valueChanged = pyqtSignal()
    finished = pyqtSignal()

    ui_maximumHeight = 50
    valueEditMaximumWidth = 100
    epsilon = 1e-6

    ## Constructor
    def __init__(self, title="ParameterEditor"):
        super(ParameterEditor, self).__init__()

        self._parameters = {}
        self._layout = None
        self._createUI()
        self.setWindowTitle(title)

    def parameters(self):
        return self._parameters

    def parameter(self, name):
        return self._parameters[name]

    def parameterData(self):
        data = {}

        for parameter in self._parameters:
            data[parameter.name()] = parameter.value()
        return data

    def setParameterData(self, data):
        for name in data.keys():
            if self._parameters.has_key(name):
                self._parameters[name].setValue(data[name])

    def addIntParameter(self, name="", min_val=0, max_val=100, default_val=0):
        ui = IntSliderGroup(name, min_val, max_val, default_val)
        self._addParameterUI(ui, name, default_val)

    def addFloatParameter(self, name="",
                           min_val=0.0, max_val=1.0, default_val=0.0):
        ui = FloatSliderGroup(name, min_val, max_val, default_val)
        self._addParameterUI(ui, name, default_val)

    def addBoolParameter(self, name="", default_val=False):
        ui = BoolEditor(name, default_val)
        self._addParameterUI(ui, name, default_val)

    def addEnumParameter(self, name="", items=["v1", "v2", "v3"], default_val="v1"):
        ui = EnumEditor(name, items, default_val)
        self._addParameterUI(ui, name, default_val)

    def addButton(self, name="", cmd_func=_nullFunc):
        ui = QPushButton(name)
        ui.pressed.connect(cmd_func)
        self._layout.addWidget(ui)

    def addOKButton(self, cmd_func=_nullFunc):
        parent_widget = QWidget()
        layout = QHBoxLayout()
        parent_widget.setLayout(layout)
        ok_button = QPushButton("OK")
        ok_button.pressed.connect(cmd_func)
        ok_button.pressed.connect(self.close)

        cancel_button = QPushButton("Cancel")
        cancel_button.pressed.connect(self.close)

        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)
        self._layout.addWidget(parent_widget)

    def _addParameterUI(self, ui, name, default_val):
        self._layout.addWidget(ui)
        self._parameters[name] = Parameter(name, default_val)
        ui.valueChanged.connect(self._parameters[name].setValue)
        ui.valueChanged.connect(self.valueChanged)

    def _createUI(self):
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

    def _nullFunc(self):
        pass


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    editor = ParameterEditor()
    editor.addIntParameter("IntParam")
    editor.addFloatParameter("FloatParam")
    editor.addBoolParameter("BoolParam")
    editor.addEnumParameter("EnumParam")
    editor.addOKButton()
    editor.show()
    end = app.exec_()