#!/usr/bin/python3
# -*- coding: utf8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyKDE4 import kdecore, kdeui, ktexteditor, kparts
import math
import sys
import traceback

import PyQt4.QtGui, PyQt4.QtCore

about = kdecore.KAboutData(
    "qp-experiment",
    "",
    kdecore.ki18n(b"KApplication"),
    "0.1",
    kdecore.ki18n(b"experiment"),
    kdecore.KAboutData.License_GPL,
    kdecore.ki18n(b"(c) Timo Paulssen"),
    kdecore.ki18n(b"nothing"),
    "http://github.com/timo/qpainter-experiment",
    "root@localhost")

kdecore.KCmdLineArgs.init(sys.argv, about)

app = kdeui.KApplication()

canvas_size = QSize(300, 300)

class MainWindow(kdeui.KMainWindow):
    def __init__(self):
        super().__init__()

        self.last_working_code = compile("", "<initial data>", "exec")
        self.last_correct_code = self.last_working_code

        self.animation_time = 0

        self.setup_ui()

        self.refresh_timer = self.startTimer(50)

    def setup_ui(self):
        cw = QWidget()
        layout = QHBoxLayout()

        factory = kdecore.KLibLoader.self().factory("katepart")
        self.kate = factory.create(self, b"KatePart")
        #print("\n".join(dir(self.kate)))
        self.kate.setHighlightingMode("Python")

        self.canvas = QLabel()
        self.canvas.setFixedSize(canvas_size)
        self.canvas.setFrameShape(QFrame.Box)
        self.image = QPixmap(canvas_size)
        self.image.fill()
        self.canvas.setPixmap(self.image)

        layout.addWidget(self.kate.widget())
        layout.addWidget(self.canvas)

        self.kate.textChanged.connect(self.onTextChanged)
        print(dir(self.kate.markInterface()))
        self.kate.markInterface().markToolTipRequested.connect(self.onMarkToolTip)

        cw.setLayout(layout)
        self.setCentralWidget(cw)

    def onTextChanged(self):
        #print(self.kate.text())
        #print(self.kate.activeView().cursorPosition().line())

        try:
            ast = compile(self.kate.text(), "<editor>", "exec")
            self.last_correct_code = ast
            #print("the last correct code is now good")
        except SyntaxError:
            print("there were syntax errors")
            self.markup_errors()

    def onMarkToolTip(self, doc, mark, position):
        QToolTip.showText(position, "<p style='white-space:pre'>%s</p>" % (self.current_error), self.kate.widget())

    def markup_errors(self):
        tbs = traceback.extract_tb(sys.exc_info()[2])
        mi = self.kate.markInterface()

        mi.clearMarks()

        self.current_error = sys.exc_info()[1]

        for tb in tbs:
            if tb[0] != "<editor>":
                continue
            #print("\n".join(dir(mi.marks())))
            #print(mi.marks())
            mi.setMark(tb[1] - 1, 0x40)

    def clear_errors(self):
        mi = self.kate.markInterface()
        mi.clearMarks()

    def timerEvent(self, event):
        self.animation_time += 0.02
        self.image = QPixmap(canvas_size)
        self.image.fill()
        painter = QPainter(self.image)
        globaldict = dict()
        globaldict.update(PyQt4.QtCore.__dict__)
        globaldict.update(PyQt4.QtGui.__dict__)
        try:
            exec(self.last_correct_code, dict(t=self.animation_time, p=painter, m=math), globaldict)
            self.last_working_code = self.last_correct_code
            self.clear_errors()
        except:
            painter.end()
            del painter
            self.image.fill()
            painter = QPainter(self.image)
            self.last_working_code = self.last_working_code
            self.markup_errors()
            exec(self.last_working_code, dict(t=self.animation_time, p=painter, m=math), globaldict)
        del painter
        self.canvas.setPixmap(self.image)


win = MainWindow()
win.show()
app.exec_()



