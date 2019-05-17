#!/usr/bin/env python

from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QMainWindow,
        QAction, QShortcut, QCheckBox, QGridLayout)
from PyQt5.QtGui import QIcon, QKeySequence
import sys

class VideoWindow(QMainWindow):

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("TILU Media Player")
        self.setWindowIcon(QIcon("icon.png"))
        self.mediaPlayers = []
        self.videoWidgets = []
        self.selector = []

        for i in range(3):
            self.mediaPlayers.append(QMediaPlayer(None, QMediaPlayer.VideoSurface))
            self.videoWidgets.append(QVideoWidget())
            self.mediaPlayers[i].setVideoOutput(self.videoWidgets[i])

        # create video layout
        upperLayout = QHBoxLayout()
        upperLayout.setContentsMargins(0, 0, 0, 0)
        upperLayout.addWidget(self.videoWidgets[0])
        upperLayout.addWidget(self.videoWidgets[1])

        finalLayout = QVBoxLayout()
        finalLayout.setContentsMargins(0, 0, 0, 0)
        finalLayout.addLayout(upperLayout)
        finalLayout.addWidget(self.videoWidgets[2])

        # Create play button and shortcuts
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        playShortcut = QShortcut(QKeySequence("Space"), self)
        playShortcut.activated.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)

        sidebar = QVBoxLayout()
        sidebar.insertSpacing(0, 100)

        # Create open button
        openButton = QPushButton(QIcon('open.png'), "Open Video", self)
        openButton.setToolTip("Open movie")
        openButton.clicked.connect(self.openFile)
        sidebar.addWidget(openButton)
        openShortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        openShortcut.activated.connect(self.openFile)

        # Checkboxes for displaying video
        for i in range(3):
            boxId = str(i+1)
            checkbox = QCheckBox("Video &" + boxId, self)
            checkbox.setChecked(True)
            shortcut = QShortcut(QKeySequence(boxId), self)
            self.selector.append(checkbox)
            sidebar.addWidget(self.selector[i])

        displayButton = QPushButton("Display Selected", self)
        displayButton.setToolTip("Display only selected videos on screen")
        displayButton.clicked.connect(self.selectVideo)
        sidebar.addWidget(displayButton)
        displayShortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        displayShortcut.activated.connect(self.selectVideo)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        mainScreen = QGridLayout()
        mainScreen.addLayout(finalLayout, 0, 0)
        mainScreen.addLayout(controlLayout, 3, 0)
        mainScreen.addWidget(self.errorLabel, 4, 0)
        sidebar.addStretch()
        mainScreen.addLayout(sidebar, 0, 1)

        # Set widget to contain window contents
        wid.setLayout(mainScreen)

        for i in self.mediaPlayers:
            i.stateChanged.connect(self.mediaStateChanged)
            i.positionChanged.connect(self.positionChanged)
            i.durationChanged.connect(self.durationChanged)
            i.error.connect(self.handleError)

    def selectVideo(self):
        for s, w in zip(self.selector, self.videoWidgets):
            if s.isChecked():
                w.show()
            else:
                w.hide()

    def openFile(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select 3 Files", QDir.homePath())
        for m, f in zip(self.mediaPlayers, files):
            m.setMedia(QMediaContent(QUrl.fromLocalFile(f)))
        self.playButton.setEnabled(True)

    def play(self):
        for i in self.mediaPlayers:
            if i.state() == QMediaPlayer.PlayingState:
                i.pause()
            else:
                i.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayers[0].state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        for i in self.mediaPlayers:
            i.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayers[0].errorString())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.showMaximized()
    sys.exit(app.exec_())
