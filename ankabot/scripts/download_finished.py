
from ankabot.gui.download_finished_ui import Ui_Dialog
from ankabot.scripts import initialization as init
from PyQt5 import QtWidgets 
import ankabot.scripts.usefultools 
import os

class DownloadFinished(QtWidgets.QDialog , Ui_Dialog ):
    def __init__(self,parent=None,url='',size=0,file_name=''):
        QtWidgets.QDialog.__init__(self,parent)
        self.setupUi(self)
        self.url = url
        self.size = size
        self.download_path = init.download_path
        self.file_name = file_name
        self.ok_pb.clicked.connect(self.ok_button_clicked)
        self.openFile_pb.clicked.connect(self.openfile_button_clicked)
        self.openFolder_pb.clicked.connect(self.openfolder_button_clicked)
        self.link_le.setText(self.url)
        self.fileName_le.setText(self.file_name)
        self.saveAs_le.setText(self.download_path)
        self.fileSize_la.setText(size)
    
    def ok_button_clicked(self):
        self.close()

    def openfile_button_clicked(self):
        #open the file
        usefultools.xdg_open(os.path.join(self.download_path,self.file_name))
        self.close()

    def openfolder_button_clicked(self):
        #open folder
        usefultools.xdg_open(self.download_path)
        self.close()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = DownloadFinished()
    window.show()
    sys.exit(app.exec_())
