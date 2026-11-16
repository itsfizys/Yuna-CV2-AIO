"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import yaml 
import json 
import os 


config = {}
_config_path = 'config.yml'
if os.path.exists(_config_path):
    with open(_config_path, 'r', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file) or {}


valid_language_codes = []
lang_directory = "lang"

current_language_code = config.get('LANGUAGE', 'en')

if os.path.isdir(lang_directory):
    for filename in os .listdir (lang_directory ):
        if filename .startswith ("lang.")and filename .endswith (".json")and os .path .isfile (
        os .path .join (lang_directory ,filename )):
            language_code =filename .split (".")[1 ]
            valid_language_codes .append (language_code )

def load_current_language ()->dict :
    lang_file_path =os .path .join (
    lang_directory ,f"lang.{current_language_code}.json")
    if not os.path.exists(lang_file_path):
        return {}
    try:
        with open (lang_file_path ,encoding ="utf-8")as lang_file :
            current_language =json .load (lang_file )
        return current_language 
    except (json.JSONDecodeError, PermissionError):
        return {}


def load_instructions ()->dict :
    instructions ={}
    if not os.path.exists("instructions"):
        return instructions
    try:
        for file_name in os .listdir ("instructions"):
            if file_name .endswith ('.txt'):
                file_path =os .path .join ("instructions",file_name )
                with open (file_path ,'r',encoding ='utf-8')as file :
                    file_content =file .read ()

                    variable_name =file_name .split ('.')[0 ]
                    instructions [variable_name ]=file_content 
    except Exception:
        pass
    return instructions 

def load_active_channels ()->dict :
    if os .path .exists ("channels.json"):
        try:
            with open ("channels.json","r",encoding ='utf-8')as f :
                return json .load (f )
        except json.JSONDecodeError:
            return {}
    return {}
"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
