# from importlib.resources import path
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPlainTextEdit, QAction, qApp, QMessageBox, QFileDialog)

def about_dialog():
    # About 대화상자 표시
    # QMessageBox.about을 사용해 모달 다이얼로그 생성 부모로 전연 window를 사용(현 인스턴스 참조)
    text = "<center>" \
        "<h1>Simple Notepad</h1>"\
        "&#8291;" \
        "</center>" \
        "<p>version 1.0 <br>" \
        "Created by pagichacha<br />" \
        "MIT License</p>"
    QMessageBox.about(window, "About Simple Notepad", text)


class MainWindow(QMainWindow):
    # 메인 윈도우 구현
    # QMainwindow를 상속. 중앙 위젯에 QPlainTextEdit 배치 
    def __init__(self):
        super().__init__()
        # 간단한 텍스트 편집을 위한 위젯
        self.text_widget = QPlainTextEdit()
        self.setCentralWidget(self.text_widget)
        # 타이틀 / 레이아웃
        self.title = 'Simple NotePad'
        self.left = 300
        self.top = 100
        self.width = 700
        self.height = 800
        # 각 메뉴
        self.quit_action = QAction('&Quit', self)
        self.about_action = QAction('&About', self)
        self.open_action = QAction('&Open', self)
        self.save_action = QAction('&Save', self)
        self.save_as_action = QAction('&Save as', self)
        # 디버그 로그(숫자들을 통해 어디에서 오류가 나는지 확인 가능)
        print("5")
        # 현재 열린 파일 경로 저장
        self.file_path = None
        # 단축키 / 시그널 연결
        self.create_actions()
        #  UI 초기화
        self.init_ui()

    def create_menubar(self):
        # 메뉴바, 메뉴 항목 구성
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addAction(self.quit_action)
        self.help_menu.addAction(self.about_action)

    def create_actions(self):
        # 단축키와 동작 연결
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
        # 파일 열기
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
        # 파일 저장
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
        # 현재 편집 내용 파일에 저장
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
        # 메뉴 객체 생성 / 배치
        self.file_menu = self.menuBar().addMenu("&File")
        self.help_menu = self.menuBar().addMenu("&Help")
        self.create_menubar()

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width, self.height)

        
        self.show()
        print("4")

if __name__ == "__main__":
    #  메인 윈도우 인스턴스화
    app = QApplication(sys.argv)
    print("1")
    window = MainWindow()
    print("2")
    sys.exit(app.exec_())
    print("3")