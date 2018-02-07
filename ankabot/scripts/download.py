# this is the download manager engine

from urllib.parse import urlunparse , unquote
import initialization as init
import usefultools 
import requests 
import time
import json
import os

class Download:
    chunk_size = 124
    def __init__(self,link ,file_path,file_size, frange='0-',chunk_counter=0):
        self.headers = {}
        self.stop_downloading = 0 
        self.link = link
        self.file_path = file_path
        self.file_size = file_size
        self.frange = frange
        self.chunk_counter = chunk_counter
        self.begin_time= time.time()
        
    
    def stop_download(self):
        self.stop_downloading = 1 

    
    def pause_download(self):
        self.stop_downloading = 2

    def set_frange(self,begin , end=''):
        self.frange = '{0}-{1}'.format(begin,end) 

    #this function gets the file size in bytes and return human readable size
    @staticmethod
    def h_size(size):
        labels = [  'KB' , 'MB' , 'Gb' , 'TB' , 'PB']
        i = -1
        if type(size) == str:
            size = int(size)
        
        if size < 1000:
            return str(size)+' B'
        while size >= 1000:
            i += 1
            m = size % 1000
            size = int(size / 1000)

        return str(size)+'.'+str(m)[0]+' ' +labels[i]






    @staticmethod
    def check_url(url):
        try:

           res = requests.head(url,timeout=(9,27),allow_redirects = True) 


        except Exception as e:
            print(str(e))

        else:
            
           size = res.headers['Content-Length']
           fileType = res.headers['Content-Type']
           
           return (size , fileType)


    #downloads the file .    
    def download(self,progress , stoped_signal):
        try:
            
            self.headers['Range'] = 'bytes='+self.frange        
            res = requests.get(self.link,stream=True, headers = self.headers, timeout=(9,27)) 
            if res.status_code != 206 and res.status_code != 200 :
                raise Exception('can not download the file')
            with open(self.file_path , 'ab') as f:
                for chunk in res.iter_content(chunk_size = self.chunk_size):
                    if self.stop_downloading :
                        break
                    f.write(chunk)
                    self.chunk_counter += 1
                    progress(self.chunk_counter)
           
            

        except Exception as e:
            status = 'stoped'
            print(str(e))
        else:
            if self.stop_downloading == 1:
                status = 'stoped'
            
            elif self.stop_downloading == 2:
                status = 'paused'

            else:
                #downloading has finished copy the file to download path
                status = 'complete'
                file_name = os.path.basename(self.file_path)
                #cut file 
                usefultools.move(self.file_path ,os.path.join(init.download_path,file_name ) )


        #save the information of download
        finally:
            self.stop_downloading = 0

            info = {'link':self.link , 'status':status,
                        'file_size':self.file_size,'file_path':self.file_path ,
                        'last_try':self.begin_time}

            if res.status_code == 206:
                inf = {'percent':str(100*self.chunk_counter*self.chunk_size // self.file_size),'last_byte':str(self.chunk_counter*self.chunk_size )}

            #it doesnt support resuming 
            elif res.status_code == 200:
                inf = {'last_byte':'0','percent':'0'}
                         
            info.update(inf)     

            info =json.dumps(info)
            file_name = unquote(os.path.basename(self.file_path))
            path = os.path.join(init.download_info_folder,file_name)
            path = path+'.info'
            with open(path, 'w') as f :
                    f.write(info)
                            
            stoped_signal(status)

    

if __name__ == '__main__':
    #test
    url = 'http://dl13.idlshare.com/se/T/mostaed/S01/The.Gifted.S01E11.480p.HDTV.x264.RMTeam.BLAXUP.NET.mkv'
    info = Download.check_url(url)
    print(info)
    print(Download.h_size(int(info[0])))
