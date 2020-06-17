import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QUrl, QTimer
from pathlib import Path  # to get home dir
import sys
import os  # for calc folder size
import shutil  # for free space
from datetime import date #
import logging


class ComicSliderGui(QMainWindow):  # use properties in in QMainWindow
    filename = ''
    foldername = ''
    selection = ''
    folderSize = 0
    outputDir = ''
    outputSpace = 0

    def __init__(self):
        super(ComicSliderGui, self).__init__()  # parent constructor
        self.setGeometry(200, 200, 361, 565)  # x & y on screen, x & y dimensions of window
        self.setWindowTitle("ComicSliderDesktop")
        self.initUI()

    def initUI(self):  # all stuff in window

        self.pushB_SelectFile = QtWidgets.QPushButton(self)                 # created
        self.pushB_SelectFile.setObjectName("pushB_SelectFile")             # named
        self.pushB_SelectFile.setGeometry(QtCore.QRect(160, 10, 191, 23))   # moved
        self.pushB_SelectFile.setText("Select file")                        # labeled
        self.pushB_SelectFile.clicked.connect(self.SelectFile)              # action

        self.labelFileSelected = QtWidgets.QLabel(self)
        self.labelFileSelected.setObjectName("labelFileSelected")
        self.labelFileSelected.setGeometry(QtCore.QRect(30, 40, 321, 16))
        self.labelFileSelected.setText(".")

        self.pushB_SelectFolder = QtWidgets.QPushButton(self)
        self.pushB_SelectFolder.setObjectName("pushB_SelectFolder")
        self.pushB_SelectFolder.setGeometry(QtCore.QRect(160, 70, 191, 23))
        self.pushB_SelectFolder.setText("Select Folder")
        self.pushB_SelectFolder.clicked.connect(self.SelectFolder)

        self.labelFolderSelected = QtWidgets.QLabel(self)
        self.labelFolderSelected.setObjectName("labelFolderSelected")
        self.labelFolderSelected.setGeometry(QtCore.QRect(30, 100, 321, 16))
        self.labelFolderSelected.setText(".")

        self.labelFolderSize = QtWidgets.QLabel(self)
        self.labelFolderSize.setObjectName("labelFolderSize")
        self.labelFolderSize.setGeometry(QtCore.QRect(30, 130, 321, 16))
        self.labelFolderSize.setText("Size of folder: ") #TODO Calc folder size

        self.radioButtonFile = QtWidgets.QRadioButton(self)
        self.radioButtonFile.setGeometry(QtCore.QRect(10, 10, 141, 17))
        self.radioButtonFile.setObjectName("radioButtonFile")
        self.radioButtonFile.setText("Single Comic")


        self.radioButtonFolder = QtWidgets.QRadioButton(self)
        self.radioButtonFolder.setGeometry(QtCore.QRect(10, 70, 131, 17))
        self.radioButtonFolder.setObjectName("radioButtonFolder")
        self.radioButtonFolder.setText("Folder of Comics")


        self.pushB_build = QtWidgets.QPushButton(self)
        self.pushB_build.setObjectName("pushB_build")
        self.pushB_build.setGeometry(QtCore.QRect(190, 190, 161, 23))
        self.pushB_build.setText("Build PPTX")
        self.pushB_build.clicked.connect(self.Build)

        self.pushB_output = QtWidgets.QPushButton(self)
        self.pushB_output.setObjectName("pushB_output")
        self.pushB_output.setGeometry(QtCore.QRect(10, 190, 161, 23))
        self.pushB_output.setText("Output Folder")
        self.pushB_output.clicked.connect(self.Output)

        self.labelOutput = QtWidgets.QLabel(self)
        self.labelOutput.setObjectName("labelFreeSpace")
        self.labelOutput.setGeometry(QtCore.QRect(30, 160, 121, 16))
        self.labelOutput.setText("Output:  ")  # TODO CALC FREE SPACE

        self.labelFreeSpace = QtWidgets.QLabel(self)
        self.labelFreeSpace.setObjectName("labelFreeSpace")
        self.labelFreeSpace.setGeometry(QtCore.QRect(220, 130, 121, 16))
        self.labelFreeSpace.setText("Free space: ") #TODO CALC FREE SPACE

        self.labelPPTXbuilt = QtWidgets.QLabel(self)
        self.labelPPTXbuilt.setObjectName("labelPPTXbuilt")
        self.labelPPTXbuilt.setText("PPTX Built: ")
        self.labelPPTXbuilt.setGeometry(QtCore.QRect(30, 460, 311, 16))

        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setGeometry(QtCore.QRect(10, 230, 341, 23))
        self.progressBar.setProperty("value", 24) #TODO PROGRESS BAR

        self.pushB_logfile = QtWidgets.QPushButton(self)
        self.pushB_logfile.setObjectName("pushB_logfile")
        self.pushB_logfile.setGeometry(QtCore.QRect(10, 500, 75, 23))
        self.pushB_logfile.setText("Logfile")
        self.pushB_logfile.clicked.connect(self.launchLogfile)

        self.pushB_savesettings = QtWidgets.QPushButton(self)
        self.pushB_savesettings.setGeometry(QtCore.QRect(190, 500, 75, 23))
        self.pushB_savesettings.setObjectName("pushB_savesettings") #TODO SAVE SETTINGS
        self.pushB_savesettings.setText("Save Settings")

        self.pushB_exit = QtWidgets.QPushButton(self)
        self.pushB_exit.setObjectName("pushB_exit")
        self.pushB_exit.setGeometry(QtCore.QRect(280, 500, 75, 23))
        self.pushB_exit.setText("Exit")
        #self.pushB_exit.clicked.connect(self.exitapp)
        self.pushB_exit.clicked.connect(self.testbutton)

        # I would like the textBrowser to automatically update to
        # loggerfile, but couldn't figure it out
        self.textBrowser = QtWidgets.QTextBrowser(self)
        #self.textBrowser.setPlainText(text)
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.setGeometry(QtCore.QRect(10, 260, 341, 191))

        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.reloadText)
        # self.timer.start(1000)

    # def reloadText(self):
    #     with open(loggerfile, "r") as file:
    #         text = str(file.readlines()[-13:])
    #     self.textBrowser.toHtml()
    #     self.textBrowser.setPlainText(text)
    #     #self.textBrowser.moveCursor(QtGui.QTextCursor.End)
    #     os.system(loggerfile)
    #     self.update()

    def SelectFile(self): #file is returned as a tuple
        filename = QFileDialog.getOpenFileName(self, 'Open file', str(Path.home()), "Comic files (*.cbz *.cbr *.zip *.rar)")
        print("File Selected: " + str(type(filename[0])) + str(filename[0]))
        filename = filename[0]

        if len(filename) > 50:
            self.labelFileSelected.setText(filename[:2] + "..." + filename[-45:]) #shorten file and path
        else:
            self.labelFileSelected.setText(filename)
        self.labelFileSelected.adjustSize()

        self.filename = filename
        self.update()

    def SelectFolder(self):
        foldername = QFileDialog.getExistingDirectory(self, "Select Directory")
        #print("Folder Selected: " + foldername)
        logging.info("Folder Selected: " + foldername)
        if len(foldername) > 50:
            self.labelFolderSelected.setText(foldername[:2] + "..." + foldername[-45:])
        else:
            self.labelFolderSelected.setText(foldername)

        self.labelFolderSelected.adjustSize()
        self.foldername = foldername
        print(foldername)

        #Size
        if self.foldername != '':
            print(self.foldername)
            total_size = 0
            for folders, subfolders, files in os.walk(self.foldername):
                for f in files:
                    fp = os.path.join(folders, f)
                    total_size += os.path.getsize(fp)
            print("Directory size: " + str(total_size))
            self.labelFolderSize.setText("Size of folder: " + str(total_size // (1024 * 1024)) + "MBs")
            self.labelFolderSize.adjustSize()

            self.folderSize = total_size

        self.CalcSpace()
        self.update()



    def Output(self):
        foldername = QFileDialog.getExistingDirectory(self, "Select Directory")
        print("Output folder selected: " + str(type(foldername)) + foldername)

        if len(foldername) > 50:
            self.labelOutput.setText(foldername[:2] + "..." + foldername[-45:])
        else:
            self.labelOutput.setText(foldername)
        self.outputDir = foldername
        self.labelOutput.adjustSize()

        if self.outputDir != '':  #
            total, used, free = shutil.disk_usage(self.outputDir)
            self.labelFreeSpace.setText("Free space: " + str(free // (1024 * 1024)) + "MBs")
            self.labelFreeSpace.adjustSize()
            self.outputSpace = free

        self.CalcSpace()
        self.update()

    def CalcSpace(self):
        print("CalcSpace")
        if self.folderSize > 0 and self.outputSpace > 0:
            if (self.folderSize * 1.3) > self.outputSpace:
                print("Not enough space on target drive")
                self.pushB_build.setEnabled(False)
            else:
                self.pushB_build.setEnabled(True)
        self.update()



    def Build(self):
        #radioButtonFile
        #radioButtonFolder
        if self.radioButtonFile.isChecked():
            if self.filename != '' and self.outputDir != '':
                pass
        if self.radioButtonFolder.isChecked():
            if self.foldername != '' and self.outputDir != '':
                pass

    def launchLogfile(self):
        with open(loggerfile, "r") as file:
            text = str(file.readlines()[-13:])
        self.textBrowser.toHtml()
        self.textBrowser.setPlainText(text)
        #self.textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.update()

        #os.system(loggerfile) #Doesn't work whilst program is running


    def exitapp(self):
        exit()

    def testbutton(self):
        print("test button")
        logging.warning('test button')
        #self.textBrowser.append(str(firstNlines))
        #print(self.filename)

def window():
    app = QApplication(sys.argv)
    win = ComicSliderGui()
    win.show()
    sys.exit(app.exec())
window()





def printLog(string, object=object, ):
    pass
    #check global variable for lambda

    #if lambda = false

        #if ComicSliderGui exists
            #object.textBrowser.append(string)
            #add to logfile.txt
