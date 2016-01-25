
# -*- coding: utf-8 -*-
## @package npr_sfs.shaders.shader_program
#
#  npr_sfs.shaders.shader_program utility package.
#  @author      tody
#  @date        2015/11/17

import os
from PyQt4 import *
from PyQt4.QtOpenGL import *
from PyQt4.QtGui import QMatrix4x4


def shaderDir():
    return os.path.dirname(os.path.abspath(__file__))


def shaderFile(shader_name):
    return os.path.join(shaderDir(), shader_name)


class ShaderProgram(object):
    def __init__(self, vertex_shader, fragment_shader):
        self._program = QGLShaderProgram()
        self.linkShaders(vertex_shader, fragment_shader)

    def bind(self):
        if not self.isLinked():
            return

        self._program.bind()

    def release(self):
        self._program.release()

    def isLinked(self):
        return self._program.isLinked()

    def linkShaders(self, vertex_shader, fragment_shader):
        vertex_shader_file = shaderFile(vertex_shader)
        fragment_shader_file = shaderFile(fragment_shader)

        self._program.removeAllShaders()
        self._program.addShaderFromSourceFile(QGLShader.Vertex, vertex_shader_file)
        self._program.addShaderFromSourceFile(QGLShader.Fragment, fragment_shader_file)
        self._program.link()
        self._program.bind()
        self._initAttr()

    def setUniformValue(self, attr, val):
        attr_location = self._program.uniformLocation(attr)
        self._program.setUniformValue(attr_location, val)

    def _initAttr(self):
        matrixLocation = self._program.uniformLocation("matrix")
        self._program.setUniformValue(matrixLocation, QMatrix4x4())
