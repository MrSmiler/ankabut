#!/usr/bin/python3

class Error(Exception):
    pass

class WithoutParenthesis(Error):
    #this happens when user forgot to put parenthesis in the file name
    #when not sure mode is checked
    pass


class GooglePageError(Error):
    #raised when google 'from' page is greater than 'to'
    #or when can not find a google page
    pass

class EmptyFileNameError(Error):
    #raised when filename line edit is empty
    pass

class EmptyWebsitesError(Error):
    #raised when google cant find any web pages to 
    pass


class DownloadError(Error):
    #raised when http response status_code is not 206 (partial content) or 200
    pass


class SettingsError(Error):
    #raised when something in settings(config file) goes wrong
    pass

