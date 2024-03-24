import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QGridLayout, QLineEdit, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QClipboard

class CopyToClipboardExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Copy to Clipboard Example')
        self.setGeometry(100, 100, 400, 200)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.layout = QVBoxLayout()
        self.centralWidget.setLayout(self.layout)

        self.label = QLabel('Enter text to copy:')
        self.layout.addWidget(self.label)

        self.textEdit = QLineEdit()
        self.layout.addWidget(self.textEdit)

        self.button = QPushButton('Copy to Clipboard')
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.copyToClipboard)

    def copyToClipboard(self):
        text = self.textEdit.text()
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.label.setText('Text copied to clipboard: ' + text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CopyToClipboardExample()
    ex.show()
    sys.exit(app.exec_())
