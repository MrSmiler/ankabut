#!/usr/bin/python3

class error(Exception):
    pass

class WithoutParenthesis(Exception):
    #this happens when user forgot to put parenthesis in the file name
    #when not sure mode is checked
    pass
