# -*- coding: utf-8 -*-


#this is the search engine





from ankabut.scripts import exceptions
from bs4 import BeautifulSoup
import requests
import re

#this class is doing the search in google 
class Google:
    def __init__(self, query,page):
        #this the proper query chosen by user in combobox
        self.query = query
        self.page = page
        #this is the link
        self.link = "https://google.com/search?q="+self.query
        #this is the websites link which match the query
        self.websites_list = []


    def find_page_link(self):
        res = requests.get(self.link , timeout=(9,27))
        html = res.text 
        soup = BeautifulSoup(html , 'html.parser')
        for tag in soup.find_all('a'):
            try:
                if tag.get('class')[0] ==  'fl' :
                    if re.search(r'/search\?q=.*start={0}.*'.format(self.page-1),tag.get('href')):
                        return self.attach_google_url(tag.get('href'))

            except:
                pass
        
        raise exceptions.GooglePageError('cant find google page') 

    def get_links(self):
        try:
            print('google has begun')
            if self.page == 1:
                the_link = self.link
            else:
                the_link = self.find_page_link()
            #timeout first number waits for the clients to stablish a connection with server
            #timeout, second number waits for the response of the server
            res = requests.get(the_link, timeout=(3 ,12 ))
            html = res.text
            soup = BeautifulSoup(html , 'html.parser')
            for tag in soup.find_all('a'):
                link = tag.get('href')
                if self.validate_urls(link):
                    link = self.attach_google_url(link)
                    self.websites_list.append(link)
            print('google has finished')
            if not self.websites_list:
                raise exceptions.EmptyWebsitesError("empty websites list ")

            return self.websites_list
        

        
        except requests.exceptions.ConnectionError :
            print('there is no internet connection ')
            return []

        except requests.exceptions.Timeout:
            print('Timeout happend ')
            return []

        except Exception as e :
            print(str(e))
            return []


    def validate_urls(self,link):
        #if you search on google the website links you click the href of that tag begins with "/url"
        if re.search('^/url.*',link):
            if not re.search('^/url.*?webcache.*',link):
                return True
        return False


    def attach_google_url(self,link):
        url = "https://google.com"
        link = url+link
        return link




if __name__ == '__main__':
    main_query= '{0} -inurl:(htm|html|php|pls|txt) intitle:index.of ({1})'.format('thor','mkv|avi|mp4')

    ob = Google(main_query,1)
    try:
        links = ob.get_links()
        for link in links:
            print(link)

    except TypeError:
        print('type Error')
