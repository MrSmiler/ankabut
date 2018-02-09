#!/usr/bin/python3
# -*- coding: utf-8 -*-

from ankabot.scripts.ankabot_config import get_exts, get_query, get_langs, config_check, get_advanced_query
from PyQt5.QtCore import QThread, QTime, pyqtSignal, pyqtSlot, QObject, Qt, QSize
from ankabot.scripts.download_finished import DownloadFinished
from ankabot.scripts.download_progress import DownloadProgress
from multiprocessing import Process , Queue , freeze_support
from ankabot.gui.mainwindow_ui import Ui_MainWindow
from ankabot.scripts import initialization as init
from ankabot.scripts.ask_download import AskDialog
from ankabot.scripts.search_engine import Google
from ankabot.scripts.settings import Settings
from ankabot.scripts.download import Download
from ankabot.scripts.add_link import AddLink
from ankabot.scripts.scraper import Scraper
from ankabot.scripts import exceptions
from urllib.parse import unquote
from PyQt5.QtGui import QMovie
from PyQt5 import  QtWidgets
import platform
import time
import json
import os
import re

#determinning the oprating system
os_name = platform.system()



#google search engine thread 
#this search for websites related to the search query
class GoogleThread(QThread):
    links_found = pyqtSignal(list) 
    def __init__(self, query,page,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.page = page
        self.q = query

    def run(self):
        self.gog = Google(self.q,self.page)
        links = self.gog.get_links()
        #when google find the website links this signal will emit
        self.links_found.emit(links)
   


#website scraper thread this is gonna execute in windows op
class ScraperThread(QThread,Scraper):
    linkhasfound = pyqtSignal(tuple)
    searchedlinkinc = pyqtSignal() 
    scrapfinished = pyqtSignal()

    def link_counter_signal(self):
        self.searchedlinkinc.emit()

    def scrap_finished_signal(self):
        self.scrapfinished.emit()


    def run(self):
        for tup in self.crawle():
            self.linkhasfound.emit(tup)


#website scraper this is gonna execute in a different process in linux op
class ScraperProcess(Scraper):
    def __init__(self,*args,**kwargs):
        Scraper.__init__(self,*args , **kwargs)

    def link_counter_signal(self):
        self.qsearched.put(1)

    def scrap_finished_signal(self):
        self.qfinished.put(1)
    
    def run(self):
        for tup in self.crawle():
            self.qlinks.put(tup)


    def set_q(self,qlinks,qsearched,qfinished):
        self.qlinks = qlinks
        self.qsearched = qsearched
        self.qfinished = qfinished

#if op is linux scrapers are executing in different processes
#so in order to get data from those process as fast as possible and show
#them to user i used multiprocessing.Queue 
#this thread send signal when a link is searched
class GetSearchedThread(QThread):
    searchedlinkinc = pyqtSignal() 
    def __init__(self,squeue,*args , **kwargs ):
        super().__init__(*args , **kwargs)
        self.isrunning = True
        self.squeue = squeue

    def run(self):
        while self.isrunning:
            try:
                time.sleep(0.01)
                number = self.squeue.get()
                if number :
                    self.searchedlinkinc.emit()

            except:
                pass

    def do_stop(self):
        self.isrunning = False

#as same as above thread but this send signal when a scraper finished
class GetFinishedThread(QThread):
    scrapfinished = pyqtSignal()
    def __init__(self,fqueue,*args , **kwargs ):
        super().__init__(*args , **kwargs)
        self.isrunning = True
        self.fqueue = fqueue

    def run(self):
        while self.isrunning:
            try:
                time.sleep(0.01)
                number = self.fqueue.get()
                if number :
                    self.scrapfinished.emit()

            except:
                pass

    def do_stop(self):
        self.isrunning = False

#this send signal when a result link is found
class GetLinksThread(QThread):
    linkhasfound = pyqtSignal(tuple)

    def __init__(self,qlinks,*args , **kwargs ):
        super().__init__(*args , **kwargs)
        self.isrunning = True
        self.qlinks = qlinks

    def run(self):
        while self.isrunning:
            try:
                time.sleep(0.01)
                link=self.qlinks.get() 
                if link:
                    self.linkhasfound.emit(link)

            except:
                pass



    def do_stop(self):
        self.isrunning = False

#this thread counts the elapsed time and send signals for those square animations
class SearchAnimThread(QThread):
    colorize = pyqtSignal(int)
    counttime = pyqtSignal()
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.c = 0 
        self.isrunning = True
    def run(self):
        self.animate()
    
    def stop(self):
        self.isrunning = False 

    #this emit number 1-4 every time 
    def animate(self):
        while self.isrunning:
            self.c = ( self.c  % 4 ) + 1
            self.colorize.emit(self.c)
            if self.c % 2 == 0:
                self.counttime.emit()
            time.sleep(0.5)



#i think its obvious        
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.setupUi(self)
        self.init_properties()
        self.connect_signals()
        self.downloads_tw_cols = 6
        self.scraper_threads = []
        self.finished_scraper = 0
        self.started_scrapers = 0
        self.searched_links = 0
        self.google_pages = []
        self.result_links = 0
        self.scraper_id = 1
        self.second = 0
        self.minute = 0
        self.tw_row = 0

        #these queues are for connecting processes in order to 
        #get information from them on the run
        if not os_name == 'Windows':
            self.qlinks = Queue()
            self.qsearched = Queue()
            self.qfinished = Queue()

        


    #this is the widgets events
    def connect_signals(self):
        self.search_pb.clicked.connect(self.search_button_clicked)
        self.stop_pb.clicked.connect(self.stop_pb_clicked)
        self.downloads_tw.itemClicked.connect(self.downloads_table_clicked)
        self.downloadDelete_pb.clicked.connect(self.delete_button_clicked)
        self.downloadResume_pb.clicked.connect(self.resume_button_clicked)
        self.downloadAdd_pb.clicked.connect(self.addlink_button_clicked)
        self.settings_pb.clicked.connect(self.settings_button_clicked)
    


    def settings_button_clicked(self):
        self.se = Settings(parent=self)
        self.se.show()

    #this slot is invoked when delete button in download manager is clicked
    def delete_button_clicked(self):
        url=self.downloadDelete_pb.url 
        file_name = unquote(os.path.basename(url))
        ans=QtWidgets.QMessageBox.question(self,'Ankabot','are you sure about removing the this download ?')
        if ans == QtWidgets.QMessageBox.Yes:
            info_path = os.path.join(init.download_info_folder,file_name+'.info') 
            file_path = os.path.join(init.download_part_folder,file_name) 
            try:
                os.remove(info_path)
                os.remove(file_path)
            except Exception as e:
                print(str(e))
            self.init_downloads_table()


        
    #in download manager tab add link button 
    def addlink_button_clicked(self):
        self.add_link_window = AddLink(self)
        self.add_link_window.show()
        
    

    #when click on cell on the downloads table all the other cells on same row are selected
    def downloads_table_clicked(self,item):
        row = item.row()
        for i in range(self.downloads_tw_cols):
            item = self.downloads_tw.item(row , i)
            item.setSelected(True)
            if i == 1:
                if item.text() == 'stoped' or item.text()=='complete' or item.text()=='paused':
                    #show the resume button
                    self.downloadResume_pb.setEnabled(True)
                    self.downloadDelete_pb.url = item.url
                    self.downloadResume_pb.url = item.url
                    self.downloadResume_pb.file_size = item.file_size
                    self.downloadResume_pb.status = item.text() 
        
                else:
                    self.downloadResume_pb.setEnabled(False)

    def resume_button_clicked(self):
        url =self.downloadResume_pb.url
        size = self.downloadResume_pb.file_size

        #if download is complete ask for restart
        if self.downloadResume_pb.status == 'complete':
            ans=QtWidgets.QMessageBox.question(self,'Ankabot', 'would like to restart the download ? ')
            if ans == QtWidgets.QMessageBox.Yes:
                file_name = unquote(os.path.basename(url))+'.info'

                try:
                    info_path = os.path.join(init.download_info_folder,file_name) 
                    os.remove(info_path)

                except Exception as e:
                    QtWidgets.QMessageBox.warning(self,'Ankabot',str(e))

                else:
                    #download the file
                    self.dp = DownloadProgress(self, url , size , resume = False)
                    self.dp.show()


                
            
        else:
            self.dp = DownloadProgress(self,url , size , resume = True)
            self.dp.show()



    #this return a list of google pages that must be scrap
    def google_pages_toscrap(self):
        fpage = self.gogPageFrom_sb.value()
        tpage = self.gogPageTo_sb.value()
        if fpage > tpage:
            raise exceptions.GooglePageError("'from' page can not be greater than 'to' page")
        self.google_pages =  list(range(fpage , tpage+1))






    #this stops the searching 
    def stop_pb_clicked(self):
        try:
            if not os_name == 'Windows':
                self.getlinksthread.do_stop()
                self.getfinishedthread.do_stop()
                self.getsearchedthread.do_stop()
            
                #deleting the queue objects because they hold previous data
                #unfortunatly multiprocessing Queue doesnt supprot Queue.queue.clear() method 
                #and i have to use this queue because i want to get information from each process and show them to user when srapers are running 
                del self.qlinks
                del self.qsearched
                del self.qfinished
                #and making them againe
                self.qsearched = Queue()
                self.qfinished = Queue()
                self.qlinks = Queue()

            #if self.finished_scraper < self.started_scrapers and self.scraper_threads:
            #    self.dialog.show() 

            self.search_stop = True
            self.statusVal_la.setText('inactive')

            self.anim.stop()
        except:
            pass

        self.anim_fr.setStyleSheet('background-color:white')
        self.anim_fr2.setStyleSheet('background-color:white')
        self.anim_fr3.setStyleSheet('background-color:white')
        self.anim_fr4.setStyleSheet('background-color:white')
        if self.scraper_threads:
            for t in self.scraper_threads:
                t.terminate()
                self.scraper_finished_count()
                print('thread called scraper to stop')
        
        self.search_pb.setEnabled(True)

    #in linux at the time of creating a new process the process will execute this function
    def scrap(self,file_name , exts,link , not_sure , scraper_id ):
        p = ScraperProcess( file_name=file_name , categories=exts ,link=link,not_sure=not_sure,scraper_id=scraper_id)
        p.set_q(self.qlinks,self.qsearched,self.qfinished)
        p.run()

    #this initiate the scrapers job 
    def thread_creator(self):
        exts = get_exts(self.category.lower())
        if not self.links:
            self.stop_pb_clicked()
        not_sure = True if self.notSureSpell_chb.isChecked() else False
        self.started_scrapers = 0 
        for link in self.links[:self.web_number]:

            if os_name == 'Windows':
                self.s = ScraperThread(file_name = self.file_name , categories = exts , link=link , not_sure=not_sure ,scraper_id=self.scraper_id)
                self.s.searchedlinkinc.connect(self.searched_link_inc)
                self.s.scrapfinished.connect(self.scraper_finished_count)
                self.s.linkhasfound.connect(self.link_has_found)

            else:
                self.s = Process(target=self.scrap , args=(self.file_name , exts , link , not_sure , self.scraper_id))
            self.scraper_id += 1
            self.scraper_threads.append(self.s)
        for t in self.scraper_threads:
            self.started_scrapers += 1 
            t.start()
        
        del self.links[:self.web_number]



    #this slot call when google found the websites
    @pyqtSlot(list)
    def google_links_found(self,links):
        try: 
            if not links:
                raise ConnectionError('there is no internet connection')

            if not self.search_stop:
                self.links = links
                self.thread_creator()
        except ConnectionError as e:
            self.stop_pb_clicked()
            QtWidgets.QMessageBox.warning(self,'Ankabot',str(e))

    #this counts the finished scraper threads in order to begin the new ones
    def scraper_finished_count(self):
        self.finished_scraper += 1 

        #this continue the search after scraping websites at the same time
        #it scrapes another group of websites 
        #and if user determine other google pages this handles that
        if self.finished_scraper >= self.started_scrapers and not self.search_stop:
            if not self.links:
                if not self.google_pages:
                    self.stop_pb_clicked()
                    return 
                else:
                    self.t = GoogleThread(self.main_query,self.google_pages[0])
                    self.t.links_found.connect(self.google_links_found)
                    self.t.start()
                    self.google_pages.pop(0)
                    self.scraper_threads.clear()
                    self.finished_scraper = 0 
                    return 

            self.scraper_threads.clear()
            self.finished_scraper = 0 
            self.thread_creator()    


    

    #this slot is for counting the searched links
    def searched_link_inc(self):
        self.searched_links += 1
        self.searchedLinksVal_la.setText(str(self.searched_links))

            

    #this slot is called when a link is found
    @pyqtSlot(tuple)
    def link_has_found(self,tup):
        website_url , link = tup
        self.result_links += 1
        if self.result_links > self.resultsStop_sb.value():
            self.stop_pb_clicked()
            return 
        self.resultLinksVal_la.setText(str(self.result_links))
        self.results_tw.setRowCount(self.tw_row + 1)
        for col in range(5):
            if col == 0:
                text = unquote(os.path.basename(link))
                item = QtWidgets.QTableWidgetItem(text) 
                self.results_tw.setItem(self.tw_row,col,item )
            elif col == 1:
                widget = QtWidgets.QPushButton()
                widget.clicked.connect(lambda :self.download_button_clicked(link))

                widget.setText('Download')
                self.results_tw.setCellWidget(self.tw_row , col , widget) 
            elif col == 2:
                widget = QtWidgets.QLabel()
                widget.setText("<a href='"+link+"' > Download with browser </a>")
                widget.setTextFormat(Qt.RichText)
                widget.setTextInteractionFlags(Qt.TextBrowserInteraction)
                widget.setOpenExternalLinks(True)
                widget.setAlignment(Qt.AlignHCenter)
                self.results_tw.setCellWidget(self.tw_row , col , widget) 
            
            elif col == 3:
                #website link
                widget = QtWidgets.QLabel()
                widget.setText("<a href='"+website_url+"' > Visit Website </a>")
                widget.setTextFormat(Qt.RichText)
                widget.setTextInteractionFlags(Qt.TextBrowserInteraction)
                widget.setOpenExternalLinks(True)
                widget.setAlignment(Qt.AlignHCenter)
                self.results_tw.setCellWidget(self.tw_row , col , widget) 
            

                pass


        self.tw_row += 1
    
    #after search , in the results table widget there are some download buttons
    def download_button_clicked(self,url):
        
        dialog = AskDialog(self)
        dialog.url_le.setText(url)
        dialog.show() 
         

    #this slot handle the squares animations 
    @pyqtSlot(int)
    def animate_frames(self,fr_num):
        if fr_num == 1:
            self.anim_fr4.setStyleSheet('background-color:white ')
            self.anim_fr2.setStyleSheet('background-color:white ')
            self.anim_fr.setStyleSheet('background-color: #2ecc71 ')
        if fr_num == 2:
            self.anim_fr3.setStyleSheet('background-color:white ')
            self.anim_fr.setStyleSheet('background-color:white ')
            self.anim_fr2.setStyleSheet('background-color: #2ecc71 ')
        if fr_num == 3:
            self.anim_fr4.setStyleSheet('background-color:white ')
            self.anim_fr2.setStyleSheet('background-color:white ')
            self.anim_fr3.setStyleSheet('background-color: #2ecc71 ')
        if fr_num == 4:
            self.anim_fr.setStyleSheet('background-color:white ')
            self.anim_fr3.setStyleSheet('background-color:white ')
            self.anim_fr4.setStyleSheet('background-color: #2ecc71 ')


    #this slot is executed when search push button clicked
    def search_button_clicked(self):
        try:
            if not self.fileName_le.text():
                raise exceptions.EmptyFileNameError('there must be a file name')

            self.search_pb.setEnabled(False)
            if not os_name == 'Windows':
                self.getlinksthread = GetLinksThread(self.qlinks)
                self.getlinksthread.linkhasfound.connect(self.link_has_found)
                self.getsearchedthread = GetSearchedThread(self.qsearched)
                self.getsearchedthread.searchedlinkinc.connect(self.searched_link_inc)
                self.getfinishedthread = GetFinishedThread(self.qfinished)
                self.getfinishedthread.scrapfinished.connect(self.scraper_finished_count)
                self.getfinishedthread.start()
                self.getsearchedthread.start()
                self.getlinksthread.start()
            self.file_name = self.fileName_le.text()
            if self.notSureSpell_chb.isChecked():
                if not re.search(r'.*\(\w*\).*',self.file_name):
                    raise  exceptions.WithoutParenthesis('when you are not sure about the file name spell you must use parenthesis around the part you dont know the spell')

            else:
                if  re.search(r'.*\(\w*\).*',self.file_name):
                    raise exceptions.WithoutParenthesis('dont use parenthesis in regular mode')

            self.google_pages_toscrap()
            self.results_tw.clearContents()
            self.scraper_id = 1
            self.searched_links = 0
            self.finished_scraper = 0
            self.result_links = 0
            self.scraper_threads.clear()
            self.tw_row = 0
            self.search_stop = False
            self.web_number =  self.scrapWebsites_sb.value()
            self.category = self.queryCategory_cb.currentText()
            search_t = self.basicSearchType_cb.currentIndex()

            #in not_sure mode parenthesis must not be in the google search query 
            if self.notSureSpell_chb.isChecked():
                file_name = self.file_name
                file_name = file_name.replace('(','')
                file_name = file_name.replace(')','')
            else:
                file_name = self.file_name 

            #search_t == 0 means regular google search
            if search_t == 0: 
                language= self.queryLanguage_cb.currentText() 
                query = get_query(language,self.category.lower()) 
                self.main_query =file_name+' '+query 

            #google advanced search query
            elif search_t == 1:
                types= get_exts(self.category.lower())
                types = '|'.join(types)
                ad_query = get_advanced_query()
                self.main_query= '{0} {1} ({2})'.format(file_name,ad_query,types)
                print(self.main_query)
            self.t = GoogleThread(self.main_query,self.google_pages[0])
            self.t.links_found.connect(self.google_links_found)
            self.t.start()
            self.google_pages.pop(0)
    
        except Exception as e:
            QtWidgets.QMessageBox.warning(self,'Ankabot' , str(e))

        else:
            #time cleaning 
            self.second = 0
            self.minute = 0
            #labels cleaning
            self.timeVal_la.setText('00:00')
            self.resultLinksVal_la.setText('0')
            self.searchedLinksVal_la.setText('0')
            #animation init
            self.anim = SearchAnimThread() 
            self.anim.colorize.connect(self.animate_frames)
            self.anim.counttime.connect(self.timer)
            self.anim.start()
            self.statusVal_la.setText('searching')
            #time init

   
    #counts the time after search began
    def timer(self):
        self.second += 1
        if self.second == 60:
            self.second = 0 
            self.minute += 1
        minute = '0'+str(self.minute) if self.minute < 10 else str(self.minute) 
        second= '0'+str(self.second) if self.second< 10 else str(self.second) 
        time_string =minute+':'+second
        self.timeVal_la.setText(time_string)

  
    #this function is invoked when 'yes' clicked in ask_download Qdialog
    def download_progress_clicked(self,url,file_size):
        
        self.win = DownloadProgress(self,url , file_size) 
        self.win.show()

    #this initialize those language query combo box and category combo box 
    def init_lang_category(self):
        cats=get_exts()
        langs=get_langs()
        self.queryCategory_cb.clear()
        self.queryLanguage_cb.clear()
        if 'persian' in langs:
            self.queryLanguage_cb.addItem('persian')
            langs.remove('persian')
        if 'video' in cats:
            self.queryCategory_cb.addItem('video')
            del cats['video']

        for lang in langs:
            self.queryLanguage_cb.addItem(lang)

        for category in cats :
            self.queryCategory_cb.addItem(category)

    def init_properties(self):

        #make files and folders and other init things 
        init.init()
        config_check()
        

        self.setWindowTitle('Ankabot')
        self.results_tw.setColumnWidth(0,400)
        self.results_tw.setColumnWidth(2,200)
        self.downloads_tw.setColumnWidth(0,600)
        self.init_lang_category()
                
        
        #when we want to make executable file for windows and also we want to use multiprocessing this function 
        #must be in the program to make the program Windows compatible
        freeze_support()

    def download_finished(self,url ,size , file_name):
        self.window = DownloadFinished(self,url,size , file_name)
        self.window.show()

    #this show the downloaded files and their information on download manger tab
    def init_downloads_table(self):
        datas =[]
        row = 0
        files= os.listdir(init.download_info_folder)
        for file_path in files:
            with open(os.path.join(init.download_info_folder,file_path)) as f:
                info = f.readline()
                info = json.loads(info)
            datas.append(info)

        for i in range(len(datas)-1):
            Max=float((datas[i])['last_try'])
            index = i
            for j in range(i+1,len(datas)):
                el =float((datas[j])['last_try'])
                if el > Max :
                    Max = el
                    index = j
            t = datas[i]
            datas[i] = datas[index]
            datas[index] = t

        for info in datas:
            self.downloads_tw.setRowCount(row+1)
            for j in range(self.downloads_tw_cols):
                if j == 0:
                    item = QtWidgets.QTableWidgetItem(unquote(os.path.basename(info['file_path'])))
                    self.downloads_tw.setItem(row , j , item)
                if j == 1:
                    item = QtWidgets.QTableWidgetItem(info['status'])
                    item.url = info['link']
                    item.file_size = info['file_size']
                    self.downloads_tw.setItem(row , j , item)

                if j == 2:
                    item = QtWidgets.QTableWidgetItem(Download.h_size(info['file_size']))
                    self.downloads_tw.setItem(row , j , item)
                if j == 3:
                    
                    item = QtWidgets.QTableWidgetItem(info['percent']+' %')
                    self.downloads_tw.setItem(row , j , item)
                
                if j == 4:
                    item = QtWidgets.QTableWidgetItem(Download.h_size(info['last_byte']))
                    self.downloads_tw.setItem(row , j , item)

                if j== 5:
                    item = QtWidgets.QTableWidgetItem(time.ctime(float(info['last_try'])))
                    self.downloads_tw.setItem(row , j , item)




            row += 1



    def showEvent(self,event):
        self.init_downloads_table()
            


    #if user closed the window in the middle of the search, threads or processes must be terminate
    def closeEvent(self,event):
        if self.scraper_threads:
            for p in self.scraper_threads:
                p.terminate()
        super().closeEvent(event)



def main():

    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    exit_code=app.exec_()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

    
