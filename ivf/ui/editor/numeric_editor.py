
# PyQt modules
from PyQt4.QtCore import *
from PyQt4.QtGui import *

_attrLabelPreferredWidth = 80


class AttributeLabel(QLabel):
    def __init__(self, name = ""):
        super(AttributeLabel, self).__init__("&%s:" %name)
        self.setMaximumWidth(_attrLabelPreferredWidth)
        self.setMinimumWidth(_attrLabelPreferredWidth)


# Numeric slider group.
class NumericSliderGroup(QWidget):
    valueChanged = pyqtSignal(float)

    ui_maximumHeight = 50
    valueEditMaximumWidth = 100
    epsilon = 1e-6

    ## Constructor
    def __init__(self, name = "", min_val = 0, max_val = 100, default_val = 0, dataType = int):
        super(NumericSliderGroup, self).__init__()

        self._name = name
        self._min_val = min_val
        self._max_val = max_val
        self._dataType = dataType
        self.createUI()
        self.setValue(default_val, False)
        self.setWindowTitle(name)
        self.setMaximumHeight(self.ui_maximumHeight)

    def createUI(self):
        nameLabel = AttributeLabel(self._name)
        self._valueEdit = QLineEdit()
        self._valueEdit.editingFinished.connect( self.valueEditChanged )
        self._valueEdit.setMaximumWidth(self.valueEditMaximumWidth)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setFocusPolicy(Qt.StrongFocus)
        self._slider.setSingleStep(1)
        self._slider.sliderMoved.connect(self.sliderChanged)

        self.setMinMax(self._min_val, self._max_val)

        nameLabel.setBuddy(self._valueEdit)

        layout = QGridLayout()
        layout.addWidget(nameLabel, 0, 0)
        layout.addWidget(self._valueEdit, 0, 1)
        layout.addWidget(self._slider, 0, 2)
        self.setLayout(layout)

    def setMinMax(self, min_val = 0, max_val = 100):
        self._min_val = min_val
        self._max_val = max_val
        self._setSliderMinMax(min_val, max_val)
        self._setValidator(min_val, max_val)

    def setValue(self, val, isEmit = True):
        isModified = self._isModified(val)

        self._setSliderValue(val)
        self._setValueEditValue(val)
        if isEmit and isModified:
            self.valueChanged.emit(val)

    @property
    def value(self):
        return self._sliderValue()

    def sliderChanged(self, val, isEmit = True):
        isModified = self._isModified(val)

        val = self._sliderValue()
        self._setValueEditValue(val)
        if isEmit and isModified:
            self.valueChanged.emit(val)

    def valueEditChanged(self, isEmit = True):
        val = self._valueEditValue()
        isModified = self._isModified(val)

        self._setSliderValue(val)
        if isEmit and isModified:
            self.valueChanged.emit(val)

    def _sliderValue(self):
        return self._slider.value()

    def _valueEditValue(self):
        return self._dataType ( self._valueEdit.text() )

    def _isModified(self, val):
        val_old = self.value
        return abs( val - val_old) > self.epsilon

    def _setSliderMinMax(self, min_val, max_val):
        self._slider.setMinimum(self._min_val)
        self._slider.setMaximum(self._max_val)

    def _setValidator(self, min_val, max_val):
        self._valueEdit.setValidator(QIntValidator(self._min_val, self._max_val, self._valueEdit))

    def _setSliderValue(self, val):
        self._slider.setValue( val )

    def _setValueEditValue(self, val):
        self._valueEdit.setText('%s' %val)


## Int slider group.
class IntSliderGroup(NumericSliderGroup):

    ## Constructor
    def __init__(self, name = "", min_val = 0, max_val = 100, default_val = 0):
        super(IntSliderGroup, self).__init__(name, min_val, max_val, default_val, int)


## Float slider group.
class FloatSliderGroup(NumericSliderGroup):
    sliderMaximum = 1000

    ## Constructor
    def __init__(self, name = "", min_val = 0.0, max_val = 1.0, default_val = 0.0):
        super(FloatSliderGroup, self).__init__(name, min_val, max_val, default_val, float)
        self._slider.setMinimum(0)
        self._slider.setMaximum(self.sliderMaximum)

    def _sliderValue(self):
        return self._min_val + (self._max_val - self._min_val) * self._slider.value() / float( self.sliderMaximum)

    def _setSliderValue(self, val):
        t = (val - self._min_val) / ( self._max_val - self._min_val )
        sliderVal = self.sliderMaximum * t
        self._slider.setValue(sliderVal)

    def _setSliderMinMax(self, min_val, max_val):
        pass

    def _setValidator(self, min_val, max_val):
        self._valueEdit.setValidator(QDoubleValidator(self._min_val, self._max_val, 6, self._valueEdit))


class BoolEditor(QWidget):
    valueChanged = pyqtSignal(bool)

    ## Constructor
    def __init__(self, name="", default_val=False):
        super(BoolEditor, self).__init__()
        self._name = name
        self._val = default_val
        self.createUI()

    def setValue(self, val, isEmit=True):
        self._val = val
        if isEmit:
            self.valueChanged.emit(val)

    @property
    def value(self):
        return self._val

    def createUI(self):
        nameLabel = AttributeLabel(self._name)
        self._check_box = QCheckBox()
        self._check_box.stateChanged.connect(self.stateChanged)
        nameLabel.setBuddy(self._check_box)

        layout = QGridLayout()
        layout.addWidget(nameLabel, 0, 0)
        layout.addWidget(self._check_box, 0, 1)
        self.setLayout(layout)

    def stateChanged(self, state):
        self.setValue(state != 0)


class EnumEditor(QWidget):
    valueChanged = pyqtSignal(str)

    ## Constructor
    def __init__(self, name="", items=["v1", "v2", "v3"], default_val=""):
        super(EnumEditor, self).__init__()
        self._name = name
        self._val = default_val
        self._items = items
        self.createUI()

    def setValue(self, val, isEmit=True):
        print val
        self._val = val
        if isEmit:
            self.valueChanged.emit(val)

    @property
    def value(self):
        return self._val

    def createUI(self):
        nameLabel = AttributeLabel(self._name)
        self._combo_box = QComboBox()

        self._combo_box.addItems(self._items)
        self._combo_box.currentIndexChanged.connect(self.currentIndexChanged)
        nameLabel.setBuddy(self._combo_box)

        layout = QGridLayout()
        layout.addWidget(nameLabel, 0, 0)
        layout.addWidget(self._combo_box, 0, 1)
        self.setLayout(layout)

    def currentIndexChanged(self, text):
        print text, self._combo_box.currentText()
        self.setValue(str(self._combo_box.currentText()))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    editor = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(IntSliderGroup("IntSlider"))
    layout.addWidget(FloatSliderGroup("FloatSlider"))
    layout.addWidget(BoolEditor("BoolEditor"))
    layout.addWidget(EnumEditor("EnumEditor"))
    editor.setLayout(layout)
    editor.show()
    end = app.exec_()