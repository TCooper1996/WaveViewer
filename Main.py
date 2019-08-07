import sys
import numpy as np

from PyQt5.QtCore import pyqtSignal, QSize, Qt, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QApplication, QGridLayout, QOpenGLWidget, QSlider,
                             QWidget, QPushButton, QLabel)

from OpenGL.GL import *
from Wave import *


class Window(QWidget):
    BLACK = (0, 0, 0, 1)
    WHITE = (1, 1, 1, 1)

    def __init__(self):
        super(Window, self).__init__()

        self.glWidget = GLWidget()
        phase_slider = QSlider(Qt.Horizontal)
        phase_slider.setRange(-50, 50)
        phase_slider.setTickInterval(25)
        amplitude_slider = QSlider(Qt.Horizontal)
        amplitude_slider.setRange(0, 100)
        amplitude_slider.setTickInterval(25)
        amplitude_slider.setValue(50)
        period_slider = QSlider(Qt.Horizontal)
        period_slider.setRange(0, 100)
        period_slider.setTickInterval(25)
        period_slider.setValue(50)
        self.phase_label = QLabel("Phase: {0:.2f}".format(phase_slider.value()/100*2*np.pi))
        self.amplitude_label = QLabel("Amplitude: {0:.2f}".format(amplitude_slider.value()/100*2*np.pi))
        self.period_label = QLabel("Period: {0:.2f}".format(period_slider.value()/100*2*np.pi))

        phase_slider.valueChanged.connect(self.phase_changed)
        amplitude_slider.valueChanged.connect(self.amplitude_changed)
        period_slider.valueChanged.connect(self.period_changed)

        main_layout = QGridLayout()
        main_layout.addWidget(self.glWidget, 0, 0, 1, -1)
        main_layout.addWidget(phase_slider, 1, 0)
        main_layout.addWidget(amplitude_slider, 2, 0)
        main_layout.addWidget(period_slider, 3, 0)
        main_layout.addWidget(self.phase_label, 1, 1)
        main_layout.addWidget(self.amplitude_label, 2, 1)
        main_layout.addWidget(self.period_label, 3, 1)

        self.setLayout(main_layout)
        self.setWindowTitle("Wave Viewer")

    def phase_changed(self, value):
        phase = value/100*2*np.pi
        self.phase_label.setText("Phase: {0:.2f}".format(phase))
        self.glWidget.wave.phase = phase
        self.glWidget.update_wave_buffer()

    def amplitude_changed(self, value):
        amp = value/100*2*np.pi
        self.amplitude_label.setText("Amplitude: {0:.2f}".format(amp))
        self.glWidget.wave.amplitude = amp
        self.glWidget.update_wave_buffer()

    def period_changed(self, value):
        per = value/100*2*np.pi
        self.period_label.setText("Period: {0:.2f}".format(per))
        self.glWidget.wave.period = per
        self.glWidget.update_wave_buffer()


class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vao = -1
        self.vbo = -1
        self.width = 1000
        self.height = 800
        self.wave = SinWave(0, np.pi, np.pi)


    def initializeGL(self):
        glClearColor(*Window.WHITE)
        glLineWidth(3)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenVertexArrays(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(GLfloat), None)

        self.update_wave_buffer()
        glColor4f(*Window.BLACK)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_LINE_STRIP, 0, glGetBufferParameteriv(GL_ARRAY_BUFFER, GL_BUFFER_SIZE)//8)

    def resizeGL(self, w, h):
        self.width = w
        self.height = h

        glViewport(0, w, 0, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, np.pi*4*3, 0, np.pi*4*3, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def minimumSizeHint(self):
        return QSize(self.width, self.height)

    def sizehint(self):
        return QSize(self.width, self.height)

    def update_wave_buffer(self):
        samples = 40
        periods = 6
        xs = [np.pi*2*i/samples for i in range(samples*periods)]
        ys = self.wave.get_range(samples, periods)

        array = np.array([f for vert in zip(xs, ys) for f in vert], dtype=np.float32)

        for i in range(0, len(array), 2):
            array[i] += 0
            array[i+1] += np.pi*10
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, array, GL_DYNAMIC_DRAW)
        self.update()


    # UNSAFE: This method will SIGSEGV the program if called while an empty buffer is bound
    @staticmethod
    def print_buffer_data():
        size = glGetBufferParameteriv(GL_ARRAY_BUFFER, GL_BUFFER_SIZE)
        data = np.array(glGetBufferSubData(GL_ARRAY_BUFFER, 0, size, None))
        print(data.view(np.float32))
        print("Data contains %d bytes, or %d floats" % (size, size//4))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())