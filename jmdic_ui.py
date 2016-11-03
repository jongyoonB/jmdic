import sys
from PyQt4.QtGui import *

class filedialogdemo(QWidget):
   def __init__(self, parent = None):
      super(filedialogdemo, self).__init__(parent)

      layout = QVBoxLayout()
      self.btn = QPushButton("QFileDialog static method demo")
      self.btn.clicked.connect(self.getfile)

      layout.addWidget(self.btn)
      self.le = QLabel("Hello")


      self.setLayout(layout)

      self.setWindowTitle("File Dialog demo")

      dir_ = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
      QMessageBox.information(self, "Directory Name", dir_)

   def getfile(self):
      fname = QFileDialog.getOpenFileName(self, 'Open file',
         'c:\\')
      self.le.setPixmap(QPixmap(fname))


def main():
   app = QApplication(sys.argv)
   ex = filedialogdemo()
   ex.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()