
# coding: utf-8
 
import sys
from PyQt4 import QtGui
from PyQt4 import uic
 
class Form(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("jmdic.ui")
        self.ui.show()
 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = Form()
    sys.exit(app.exec_())