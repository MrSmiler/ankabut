#!/usr/bin/python3
import usefultools
import platform
import os

# oprating system type .etc. windows - linux
os_type = platform.system() 

user_path = os.path.expanduser('~')

#download manger config folder
if os_type == 'Linux':
    config_folder = os.path.join(user_path , '.config/Ankabot')

elif os_type == 'Windows':
    config_folder = os.path.join(user_path , 'AppData','local','Ankabot')

#download information
download_info_folder = os.path.join(config_folder , 'download_info')

#its folder that holds partially downloaded files
download_part_folder = os.path.join(config_folder , 'download_files')

config_file = os.path.join(config_folder,'ankabot.config')

#contain the links found by scraper
#future : saved_links_file = os.path.join(config_folder , 'saved_links')


#downloaded files goes here
download_path = os.path.join(user_path , 'Downloads' , 'Ankabot')



def init():
    

    

    #make folders 
    for path in [ config_folder , download_info_folder , download_part_folder, download_path]:
        usefultools.makedir(path)


    #make files
    for path in []:
        usefultools.makefile(path)


if __name__ == '__main__':
    init()
