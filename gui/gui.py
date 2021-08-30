import sys
import time
from threading import Thread
from pytube.exceptions import VideoUnavailable

from logic.youtube import Video
from PyQt5 import QtCore, Qt, QtGui
from PyQt5.QtWidgets import *

help(Qt)
app = QApplication(sys.argv)

with open('css/style.css', 'r') as f:
    style = f.read()
    app.setStyleSheet(style)


class Windows(QWidget):

    def __init__(self):
        super().__init__()

        self.row = 0
        self.data = {}
        self.column = 0
        self.youtube = None
        self.listview = None

        self.data_collect_thread = None

        self.flag = QLabel()
        self.fields = [QLineEdit(), QLineEdit()]
        self.checkboxes = [QCheckBox(), QCheckBox()]
        self.buttons = [QPushButton(), QPushButton(), QPushButton()]

        self.initUI()

    def initUI(self):
        # Set a fixed window width and height
        self.setFixedWidth(800)
        self.setFixedHeight(400)

        label = QLabel()
        label.setText("︱")
        label.setObjectName("lbl_line")

        self.fields[0].setObjectName("url_field")
        self.fields[0].setPlaceholderText("Paste the YouTube URL here")
        self.fields[0].setFixedHeight(33)
        self.fields[0].textChanged.connect(self.runThread)
        # self.fields[0].returnPressed.connect(self.sequence)

        self.fields[1].setObjectName("loc_field")
        self.fields[1].setEnabled(False)
        self.fields[1].setPlaceholderText("Save location")
        self.fields[1].setFixedHeight(33)

        self.buttons[1].setText("...")
        self.buttons[1].setFixedWidth(60)
        self.buttons[1].setFixedHeight(33)
        self.buttons[1].setObjectName('add_loc_btn')
        self.buttons[1].setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttons[1].clicked.connect(self.save_dialog)

        self.buttons[2].setText("Download")
        self.buttons[2].setFixedWidth(100)
        self.buttons[2].setFixedHeight(33)
        self.buttons[2].setObjectName('download_btn')
        self.buttons[2].setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttons[2].clicked.connect(self.download_files)

        layout = QHBoxLayout()
        layout.addWidget(self.buttons[0])

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.fields[0])

        self.checkboxes[0].setText("Video")
        self.checkboxes[0].setChecked(True)
        self.checkboxes[1].setText("Audio")

        h_layout_cb = QHBoxLayout()
        h_layout_cb.setContentsMargins(10, 10, 0, 10)
        h_layout_cb.addWidget(self.checkboxes[0])
        h_layout_cb.addWidget(self.checkboxes[1])
        h_layout_cb.addWidget(label)
        h_layout_cb.addWidget(self.flag)
        h_layout_cb.addStretch(2)

        self.listview = QTableWidget()
        self.listview.setColumnCount(4)
        self.listview.setHorizontalHeaderLabels(["Index", "Title", "Duration", "Size"])
        self.listview.setColumnWidth(0, 50)
        self.listview.setColumnWidth(1, 458)
        self.listview.setColumnWidth(2, 150)
        self.listview.setColumnWidth(3, 100)
        self.listview.verticalHeader().setVisible(False)
        self.listview.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.listview.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)
        self.listview.horizontalHeader().setStyleSheet("""background:#e8eaeb; font-size: 12px; font-weight:normal;""")

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addLayout(h_layout_cb)
        v_layout.addWidget(self.listview)

        h_btn_r_layout = QHBoxLayout()
        h_btn_r_layout.addWidget(self.buttons[1])
        h_btn_r_layout.addWidget(self.buttons[2])
        h_btn_r_layout.setSpacing(20)

        h_layout_loc = QHBoxLayout()
        h_layout_loc.addWidget(self.fields[1])
        h_layout_loc.addLayout(h_btn_r_layout)
        h_layout_loc.setSpacing(10)

        v_layout.addLayout(h_layout_loc)

        self.setLayout(v_layout)
        self.show()

    def sequence(self):
        self.data_collecting()
        self.data_inserting()

    def itemExists(self, item):
        rows = self.listview.rowCount()
        for i in range(0, rows):
            if self.listview.item(i, 1).text() == item.text():
                return True

        return False

    def invalidURLMessage(self):
        self.flag.setStyleSheet("""color: red""")
        self.flag.setText("Video is unavaialable, skipping.")

    def data_collecting(self):
        url = self.fields[0].text()

        try:
            self.youtube = Video(url)
        except VideoUnavailable:
            self.invalidURLMessage()
        else:
            self.flag.setStyleSheet("""color: black""")
            self.flag.setText("Collecting data from URL")
            row = self.listview.rowCount()
            self.data[row] = {
                'index': QTableWidgetItem(f'{row + 1}'),
                'title': QTableWidgetItem(self.youtube.title()),
                'duration': QTableWidgetItem(self.youtube.duration()),
                'size': QTableWidgetItem(self.youtube.videolength()),
                'url': url
            }


    def data_inserting(self):
        nr_of_items = len(self.data.items())
        self.listview.setRowCount(nr_of_items)

        for row, values in self.data.items():
            for column, (_, value) in enumerate(values.items()):
                item = QTableWidgetItem(value)

                if column < 1:
                    item.setTextAlignment(QtCore.Qt.AlignCenter)

                self.listview.setItem(int(row), int(column), item)
                self.listview.setItem(int(row), 4, QTableWidgetItem())

        self.fields[0].setText("")
        time.sleep(1)
        self.flag.setText("Data inserted to the list")
        time.sleep(2)
        self.flag.setText("Choose location and start downloading or paste another url")

    def runThread(self):
        thread = Thread(target=self.sequence, args=())
        thread.start()

    def save_dialog(self):
        self.fields[1].setStyleSheet("""border: 0.5px solid #00abff;""")
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.fields[1].setText(file)

    def download_thread(self, url):
        location = self.fields[1].text()
        self.youtube.download(location)

    def download_files(self):
        for _, values in self.data.items():
            for name, url in values.items():
                if name == "url":
                    if self.fields[1].text() != "":
                        if self.checkboxes[0].isChecked() or self.checkboxes[1].isChecked():
                            if self.checkboxes[0].isChecked():
                                def run_thread():
                                    self.flag.setText("Downloading... please wait")
                                    self.buttons[2].setStyleSheet("""background: grey""")
                                    self.buttons[2].setEnabled(False)

                                    Video(url).download("mp4", self.fields[1].text() + "/Video/")

                                    self.buttons[2].setStyleSheet("""background: #33C30B""")
                                    self.buttons[2].setEnabled(True)
                                    self.flag.setText("Downloading completed")

                                thread = Thread(target=run_thread)
                                thread.start()

                            if self.checkboxes[1].isChecked():
                                Video(url).download("mp3", self.fields[1].text() + "/Audio/")
                        else:
                            self.flag.setText("Checkbox is not checked")
                            return
                    else:
                        self.fields[1].setStyleSheet("""border: 0.5px solid red;""")

        self.buttons[2].setEnabled(True)

    @staticmethod
    def run():
        Windows()
        sys.exit(app.exec_())
