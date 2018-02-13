
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from ankabot.scripts.download_progress import DownloadProgress
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from ankabot.scripts import initialization as init
from ankabot.gui.ask_download_ui import Ui_Dialog
from ankabot.scripts.download import Download
from ankabot.scripts import resources
from PyQt5 import QtGui
import json
import sys 
import re
import os


def handle_download_before( url ):
    info_files = os.listdir(init.download_info_folder)
    for File in info_files:
        with open(os.path.join(init.download_info_folder,File)) as f:
            data = f.read()
            info = json.loads(data)
            if url == info['link']:
                return (True, File)
    return (False , None)



class FileInfoThread(QThread):
    infoHasFound = pyqtSignal(tuple)
    def __init__(self,url):
        super().__init__()
        self.url = url

    def run(self):
        try: size , file_type = Download.check_url(self.url)

        except Exception as e:
            print(str(e))

        else:
            self.infoHasFound.emit((size,file_type))


class AskDialog(QDialog , Ui_Dialog):
    def __init__(self,parent=None):
        QDialog.__init__(self , parent)
        self.setupUi(self)
        self.url = ''
        self.yes_pb.clicked.connect(self.yes_button_clicked)
        self.no_pb.clicked.connect(self.no_button_clicked)

        if parent:
            self.parent = parent

    def showEvent(self,event):
        self.url = self.url_le.text()
        result, File=handle_download_before(self.url)
        if result:
            ans=QMessageBox.question(self.parent,'Ankabot','you have downloaded this file before, would you like to delete the file and continue ?')
            if ans == QMessageBox.Yes:
                os.remove(os.path.join(init.download_info_folder,File))
                os.remove(os.path.join(init.download_part_folder,(File)[:-5]))
            else:
               QDialog.showEvent(self,event) 

        if self.url:
            self.fiThread = FileInfoThread(self.url) 
            self.fiThread.infoHasFound.connect(self.info_has_found)
            self.fiThread.start()
            self.videoPicAddr = ':/icons/video.png'
            self.musicPicAddr = ':/icons/music.png'
            self.filePicAddr = ':/icons/file.png'
            self.pdfPicAddr = ':/icons/pdf.png'
            self.softPicAddr = ':/icons/software.png' 



        
    def info_has_found(self,info_tuple):
        self.yes_pb.setEnabled(True)
        size , file_type = info_tuple
        self.real_size = size
        try:
            ext = re.search(r'\.((\w{,3}\.)?\w{,3})$' , self.url).group(1)
        except :
            pass
        if re.search(r'application/octet-stream',file_type):
            if 'mkv' in ext or 'mp4' in ext   or 'avi' in ext :
                ext = ext[-3:]
                self.fileType_la.setText(ext)
                self.filePicture_la.setPixmap(QtGui.QPixmap(self.videoPicAddr))
            elif ext == 'exe': 
                self.fileType_la.setText(ext)
                self.filePicture_la.setPixmap(QtGui.QPixmap(self.softPicAddr))
            elif ext == 'mp3': 
                self.fileType_la.setText(ext)
                self.filePicture_la.setPixmap(QtGui.QPixmap(self.musicPicAddr))
            else:
                self.fileType_la.setText('Unknown')

        elif re.search(r'application/pdf',file_type ):
            self.fileType_la.setText('pdf')
            self.filePicture_la.setPixmap(QtGui.QPixmap(self.pdfPicAddr))
        elif re.search(r'text/html',file_type):
            self.fileType_la.setText('html')
            self.filePicture_la.setPixmap(QtGui.QPixmap(self.filePicAddr))

        
        size = Download.h_size(int(size))
        self.size_la.setText(size)
   
    def no_button_clicked(self):
        self.close()

    def yes_button_clicked(self):
        #invoke download progress
        self.parent.download_progress_clicked(self.url,self.real_size)
        self.close()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    dialog = AskDialog() 
    dialog.show()
    sys.exit(app.exec_()) 
