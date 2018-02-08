from ankabot.scripts import initialization as init
import json
import os



#this is the default data if user click the reset button in settings this
#dictonary is written to config.file
default ={"config":{
	"categories":{
		"video": ["mp4","mkv","avi"],
		"audio": ["mp3"],
		"book":  ["pdf","zip"],
		"software": ["exe","zip","rar"],
                "subtitle": ["srt","zip","rar"],
                }
	
	,
	"queries":
		{"persian":
			{"video":"دانلود فیلم",
               	 	"audio":"دانلود آهنگ",
                 	"book" :"دانلود pdf ",
                 	"software":"دانلود نرم افزار",
                        "subtitle":"دانلود زیرنویس "
			}
		,
		"english":
			{"video":"download free movie",
			 "audio":"download free music",
			 "book":"pdf",
			 "software":"download free software", 
                         "subtitle":"download english subtitle",

			}


                }	
                ,
        "advanced query":"-inurl:(htm|html|php|pls|txt) intitle:index.of “last modified” "
                    
    }	


}




CONFIG_FILE_NAME = init.config_file


def config_check():
    try:
        open(CONFIG_FILE_NAME )
    except Exception as e:
        print(str(e))
        reset_data()
        
    

def reset_data():
    write_config_file(default)


#this read the json data inside the config file and return them to python object
def read_config_file():
    try:
        with open(CONFIG_FILE_NAME) as f:
            data = f.read()
    except Exception as e:
        raise Exception('config file is missing')

    conf_data = json.loads(data)

    return conf_data

def write_config_file(data):
    try:
        data = json.dumps(data)
        with open(CONFIG_FILE_NAME,'w') as f:
            f.write(data)
    except Exception as e :
        raise Exception('config file is missing')


def get_advanced_query():
    conf_data = read_config_file()

    return conf_data['config']['advanced query']



#this returns the file types 
def get_exts( category=None):
    
    conf_data = read_config_file()

    if category:

        return conf_data['config']['categories'][category]
    
    else:
        return  conf_data['config']['categories'] 

def add_ext(category ,exts):
    conf_data = read_config_file()
    
    exts_list = conf_data['config']['categories'][category]
    exts_list.extend(exts)
    conf_data['config']['categories'][category] = exts_list 

    write_config_file(conf_data)

def remove_ext(category , ext):
    conf_data = read_config_file()
    
    exts_list = conf_data['config']['categories'][category]
    exts_list.remove(ext)
    conf_data['config']['categories'][category] = exts_list 
    write_config_file(conf_data)



#this return the proper query for search in google
def get_query(language=None , category=None):
    conf_data = read_config_file()

    if language and category:
        return conf_data['config']['queries'][language][category]
    else:
        return conf_data['config']['queries']



def get_langs():
    conf_data = read_config_file()
    
    langs = []
    for key , value in conf_data['config']['queries'].items():
        langs.append(key)

    return langs
    
def add_lang(lang):
    conf_data = read_config_file()
    d_lang = {lang:{"video":"",
			 "audio":"",
			 "book":"",
			 "software":"",
                         "subtitle":""
			}
                        }

    conf_data['config']['queries'].update(d_lang)
    write_config_file(conf_data)

#add category to both extensions and queries
def add_category(cat):
    conf_data = read_config_file()
    d_cat = {cat:[]}
    for lang in get_langs():
        conf_data['config']['queries'][lang].update(d_cat)
    conf_data['config']['categories'].update(d_cat)
    write_config_file(conf_data)

    

#changes the query for a specific category and language
def change_query(lang,cat,query):
    conf_data = read_config_file()
    conf_data['config']['queries'][lang][cat] = query
    write_config_file(conf_data)

def change_advanced_query(query):
    conf_data = read_config_file()
    conf_data['config']['advanced query'] = query
    write_config_file(conf_data)




if __name__ == '__main__':
    a = get_advanced_query()
    print(a)
    pass


