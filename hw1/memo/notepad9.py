from importlib.resources import path
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPlainTextEdit, QAction, qApp, QMessageBox, QFileDialog)

def about_dialog():
    text = "<center>" \
        "<h1>Simple Notepad</h1>"\
        "&#8291;" \
        "</center>" \
        "<p>version 1.0 <br>" \
        "Created by pagichacha<br />" \
        "MIT License</p>"
    QMessageBox.about(window, "About Simple Notepad", text)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.text_widget = QPlainTextEdit()
        self.setCentralWidget(self.text_widget)

        self.title = 'Simple NotePad'
        self.window_icon = 'pagichacha3.png'
        self.left = 300
        self.top = 100
        self.width = 700
        self.height = 800

        self.quit_action = QAction('&Quit', self)
        self.about_action = QAction('&About', self)
        self.open_action = QAction('&Open', self)
        self.save_action = QAction('&Save', self)
        self.save_as_action = QAction('&Save as', self)

        print("5")

        self.file_path = None

        self.create_actions()
        self.init_ui()

    def create_menubar(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addAction(self.quit_action)
        self.help_menu.addAction(self.about_action)

    def create_actions(self):
        pass
        self.quit_action.setShortcut('Ctrl+Q')
        self.quit_action.triggered.connect(qApp.quit)

        self.about_action.setShortcut('Ctrl+A')
        self.about_action.triggered.connect(about_dialog) 

        self.open_action.setShortcut('Ctrl+O')
        self.open_action.triggered.connect(self.open_file)

        self.save_action.setShortcut('Ctrl+S')
        self.save_action.triggered.connect(self.save_file)

        self.save_as_action.triggered.connect(self.save_as_file)

    def open_file(self):
        global path
        path = QFileDialog.getOpenFileName(window, "Open")[0]
        print(path,"++++++++++++++++++++++++++ 9")
        self.title="test"
        if path:
            # self.text_widget.setPlainText(path+"\n"+open(path).read())
            self.text_widget.setPlainText(open(path).read())
            self.title = path
            self.file_path = path

    def save_file(self):
        # print(self.file_path,"+++++++++++++++++ 10")
        if self.file_path is None:
            print("1")
            self.save_as_file()
            print("2")
        else:
            with open(self.file_path, "w") as f:
                f.write(self.text_widget.toPlainText())
            self.text_widget.document().setModified(False)
            print("7")


    def save_as_file(self):
        pass
        path = QFileDialog.getSaveFileName(window, 'Save As')[0]
        print(path)
        print("3")
        if path:
            self.file_path = path
            print("5")
            self.save_file()
            print("6")



    def init_ui(self):
        self.file_menu = self.menuBar().addMenu("&File")
        self.help_menu = self.menuBar().addMenu("&Help")
        self.create_menubar()

        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(self.window_icon))
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width, self.height)

        
        self.show()
        print("4")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    print("1")
    window = MainWindow()
    print("2")
    sys.exit(app.exec_())
    print("3")