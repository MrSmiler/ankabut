from setuptools import setup

try:
    import PyQt5
except ImportError:
    print('pyqt5 is not found')
else:
    print('pyqt5 was found ')

try:
    import bs4
except ImportError:
    print('bs4 is not found')
else:
    print('bs4 was found ')


try:
    import requests
except ImportError:
    print('requests is not found')
else:
    print('requests was found ')


setup(
       name='ankabot',
       version='1.0',
       description='',
       long_description='',
       author='Mr.smiler',
       author_email='mr.smiler.0@gmail.com',
       packages=['ankabot','ankabot.gui','ankabot.scripts'],
       install_requires=['PyQt5','bs4','requests']
        )
