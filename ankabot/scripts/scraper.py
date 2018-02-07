# -*- coding: utf-8 -*- 

#this file contain the webscraper code 

from usefultools import StopWatch
from search_engine import Google
from bs4 import BeautifulSoup
import requests
import queue
import re
import os





class Scraper:
    def __init__(self,file_name , categories,link,not_sure,scraper_id):
        self.extensions = categories 
        self.not_sure = not_sure 
        self.issearching = True
        self.name = file_name 
        self.thelink = link
        self.scraper_id = scraper_id

        #this timer breaks the loop after duration if scraper doesnt find any link 
        self.timer = StopWatch(duration=20)
        self.timer.start()
        
        #this queue contains the urls that should be crawled
        self.will_search = queue.Queue()
        # this list contains the searched links 
        self.searched_links = []


    #this stops the scraper but it might not work so fast because scrapers are doing i/o 
    #and they are blocking
    def stop_scraper(self):
        self.issearching = False


   
    #sometimes in a link a the text in the href attribute doesn't contain the http or https name
    #so we add it manually
    def correct_the_link(self,full_link,main_link ,link):
        try:
            #the links in the index of pages do not contain the whole link 
            #they just have the file name so in the href text if it wasnt any '/' means that its not link
            #its file name and then do the concat
            if not re.search(r'/',link):
                return full_link+link


            if not re.search(r'(https?://.*?)/?',link) :
                return main_link+link
        except Exception as e:
            print(str(e))

        return link
            

    #this checks whethere the link is the file we are looking for
    def is_file_found(self,file_name ,link):
        for ext in self.extensions:
            if re.search(r'{0}.*\.{1}$'.format(file_name,ext),link,re.IGNORECASE):
                return True
        return False

    #this determine whether or not this link is related to the file_name
    def is_link_related(self,file_name,main_url,link):
        if re.search(r'.*{0}.*'.format(file_name),link,re.IGNORECASE):
            if re.search(r'.*{0}.*'.format(main_url) , link , re.IGNORECASE):
                return True
        return False
   
    #every time a link is appending to a searched links this function will call
    def link_counter_signal(self):
        pass

    #when scaper reached to the end of crawler function this function is emited
    def scrap_finished_signal(self):
        pass
    
    #this is generator which returns the links
    def crawle(self):
        print('scraper {0} has started'.format(self.scraper_id))

        #make regex pattern for file name 
        #if user is not sure about file name spell
        #some another pattern will use
        if not self.not_sure:  
            file_name = '.*'.join(self.name.split(' '))
        else:
            chars = []
            isnotsure = False
            for l in self.name:
                if l == '(':
                    isnotsure = True
                elif l == ')':
                    isnotsure = False

                elif isnotsure:
                    if not l.isspace():
                        chars.append(l+'?[a-zA-Z]{,2}')

                elif l.isspace():
                    chars.append('.*')

                else:
                    chars.append(l)
                
            file_name = ''.join(chars)


        self.will_search.put(self.thelink)
        while not self.will_search.empty() and self.issearching:
            if self.timer.is_passed():
                break
            url = self.will_search.get()
            self.searched_links.append(url)
            self.link_counter_signal()
            try:
                
                #parsing the html code and find the links
                links = []
                content = []


                #this is when you search for pdf file in google the pages contains the actual pdf links 
                #so if the website name was link to the actual file return the link to the user
                if 'pdf' in self.extensions:
                    res = requests.get(url,stream=True,timeout=(3,9))
                    if re.search(r'application/pdf',res.headers['Content-Type'],re.IGNORECASE) or re.search(r'application/x-pdf',res.headers['Content-Type'],re.IGNORECASE) :
                        self.timer.restart()
                        yield (url,url )
                        continue
                else:
                    res = requests.get(url,stream=True)
                    for chunk in res.iter_content(chunk_size=128):
                        if not self.issearching:
                            break
                        content.append(chunk)

                #only if the type of file was html scrap it and find links 
                if re.search(r'text/html',res.headers['Content-Type'],re.IGNORECASE):
                    content = b''.join(content)
                    html = content.decode()
                    soup = BeautifulSoup(html,'html.parser')
                    main_url = re.search(r'(https?://.*?)/',res.url).group(1)
                    full_url = re.search(r'(https?://.*/)',res.url).group(1)

                    for link in soup.find_all('a'):
                        li = link.get('href')
                        if li: 
                            pure_link = self.correct_the_link(full_url,main_url,li)
                        
                            links.append(pure_link)

                #find the proper links 
                for link in links:
                    if link in self.searched_links:
                        continue

                    #the file has found
                    elif self.is_file_found(file_name, link): 
                        self.searched_links.append(link)
                        self.timer.restart()
                        yield (url,link)
                        continue

                    #is file_name in the link
                    #if it is this link must be search later
                    elif self.is_link_related(file_name ,main_url,link):
                        if not link in self.searched_links:
                            self.will_search.put(link)
                        
            except requests.exceptions.ConnectionError as e:
                print(str(e))

            except requests.exceptions.Timeout as e:
                print(str(e))
                break
            except IOError as e:
                print(str(e))
                break

            except Exception as e:
                print(str(e))
        
        print('scraper {0} has stoped'.format(self.scraper_id))
        self.scrap_finished_signal()


if __name__ == '__main__':
    #test
    gog = Google('دانلود فیلم mad max',1)
    urls = gog.get_links()
    for url in urls:
            c = Scraper('mad max',['mkv','mp4','avi'],url,True,scraper_id=1)
            for link in c.crawle():
                print(link)

