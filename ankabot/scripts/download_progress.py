
from PyQt5.QtCore import QThread , pyqtSignal , pyqtSlot
from download_progress_ui import Ui_Dialog
from download_finished import DownloadFinished
from usefultools import StopWatch , Timer
from urllib.parse import unquote
from download import Download
import initialization as init
from PyQt5 import QtWidgets 
import json
import time
import os
import re

class TimerThread(QThread):
    st_watchSig = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_counting= True
        self.s = 0
        self.m = 0
        self.str_time = ''

    def run(self):

        while self.is_counting:
            time.sleep(1)
            self.s += 1
            if self.s == 60 :
                self.m += 1
                self.s = 0
            self.s = '0'+str(self.s) if self.s < 10 else str(self.s)
            self.m = '0'+str(self.m) if self.s < 10 else str(self.m)
            self.str_time = self.s+':'+self.m
            self.st_watchSig.emit(self.str_time)





class DownloadThread( Download,QThread  ):
    downloadedsizeSig = pyqtSignal(str) 
    transferrateSig = pyqtSignal(str)
    percentSig = pyqtSignal(int)
    estimatedtimeSig = pyqtSignal(int)
    downloadstopedSig = pyqtSignal(str)
    def __init__(self,link,file_path,file_size , frange = '0-' , chunk_counter=0):
        Download.__init__(self,link , file_path , file_size , frange ,chunk_counter)
        QThread.__init__(self)
        self.m_time = 1
        
        self.timer = Timer()

        #we need stop watch for counting every one second
        self.st_watch = StopWatch(self.m_time)

        #this the downloaded amount within one second
        self.tmp_downloaded = 0

    def run(self): 

        self.timer.start()
        self.st_watch.start()
        if self.frange == '0-' :
            self.download(self.progress,self.stop_signal)
        else :
            self.download(self.progress,self.stop_signal)
 
    def stop_signal(self,status):
        self.downloadstopedSig.emit(status)

    def progress(self,chunk_counter):
        downloaded = chunk_counter * Download.chunk_size

        #this is executed every one second
        if self.st_watch.is_passed():
            rate = (downloaded - self.tmp_downloaded) // (self.m_time * 1000)
            self.transferrateSig.emit(str(rate)+' KB/s')
            e_time = self.timer.elapsed_time()
            time =  (e_time * self.file_size) // downloaded
            time = time - e_time
            self.estimatedtimeSig.emit(time)
            self.tmp_downloaded = downloaded 
            self.st_watch.restart()
            #this might step aside
            self.downloadedsizeSig.emit(str(downloaded))
            percent = (downloaded * 100 ) / self.file_size 
            self.percentSig.emit(int(percent)) 


class DownloadProgress(QtWidgets.QDialog , Ui_Dialog):
    def __init__(self,parent=None, url='' , size=0 ,resume = False):
        QtWidgets.QDialog.__init__(self,parent)
        self.setupUi(self)
        self.url = url
        self.file_size = size 
        self.resume = resume
        self.stop_pb.clicked.connect(self.stop_button_slot)
        self.pause_pb.clicked.connect(self.pause_button_slot)
        self.resume_pb.clicked.connect(self.resume_button_slot)
        if parent:
            self.parent = parent
        self.resume_pb.setEnabled(False)

    def showEvent(self,event):
        self.url_le.setText(self.url)
        print('downloading')
        self.status_la.setText('Downloading ...')
        self.fileSize_la.setText(Download.h_size(self.file_size))

        #download the url in seprate thread
        self.make_thread(self.resume)
    
    #if resume is True this begins from the last downloaded byte to the end
    def make_thread(self,resume=False):
        self.file_name= unquote(os.path.basename(self.url))
        #temprory solution for pdf files which is not right at all but ....
        if not re.search(r'\.\w{3}$',self.file_name) and re.search(r'\.pdf',self.file_name):
            self.file_name = self.file_name +'.pdf'

        file_path = os.path.join(init.download_part_folder,self.file_name)
        if resume:
            info_path = os.path.join(init.download_info_folder,self.file_name)
            with open(info_path+'.info' ) as f:
                info = f.read()
            info = json.loads(info)
            begin = info['last_byte']
            chunk = int(info['last_byte']) // 124
            frange = begin + '-'
            self.dt  = DownloadThread(self.url ,file_path, int(self.file_size),frange = frange , chunk_counter = chunk)


        else:
            self.dt = DownloadThread(self.url ,file_path ,int(self.file_size))

        self.dt.downloadedsizeSig.connect(self.downloaded_slot)
        self.dt.estimatedtimeSig.connect(self.estimated_time_slot)
        self.dt.transferrateSig.connect(self.transfer_rate_slot)
        self.dt.downloadstopedSig.connect(self.download_finished_or_stoped)
        self.dt.percentSig.connect(self.percent_slot)
        self.dt.start()

    @pyqtSlot(str)
    def download_finished_or_stoped(self,status):
        self.parent.init_downloads_table()
        if status == 'complete':
            print('download complete')
            self.parent.download_finished(self.url,Download.h_size(self.file_size) , self.file_name)
            self.close()
        elif status == 'stoped':
            print('download stoped')
            self.close()
            print('download stoped')
        elif status == 'paused':
            pass


    def stop_button_slot(self):
        self.dt.stop_download()

    def pause_button_slot(self):
        print('download paused')
        self.status_la.setText('paused')
        self.dt.pause_download()
        self.pause_pb.setEnabled(False)
        self.resume_pb.setEnabled(True)

    def resume_button_slot(self):
        print('downloading ')
        self.status_la.setText('downloading ...')
        self.make_thread(resume=True)
        self.pause_pb.setEnabled(True)
        self.resume_pb.setEnabled(False)

    #time parameter is in second
    def estimated_time_slot(self,time):
        minutes= time // 60
        second = int(time % 60)
        minutes = '0'+str(minutes) if minutes < 10 else str(minutes)
        second = '0'+str(second) if second < 10 else str(second)
        self.estimatedTime_la.setText(minutes+':'+second)


    def transfer_rate_slot(self,value):
        self.transferRate_la.setText(value)


    def downloaded_slot(self,size):
        self.downloaded_la.setText(Download.h_size(size))
    
    def percent_slot(self , value):
        self.progressBar_prb.setValue(value)

    def closeEvent(self ,event):
        self.dt.stop_download()
        super().closeEvent(event)

        
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = DownloadProgress()
    window.show()
    code =app.exec_()
    sys.exit(code)

