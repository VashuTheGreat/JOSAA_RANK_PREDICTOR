import yaml
import os
from exception import MyException
import sys
from dataclasses import asdict
import dill
# traces size of every file in a folder
def get_dir_size(path):
    total_size=0
    for dirpath,_,filenames in os.walk(path):
        for f in filenames:
            fp=os.path.join(dirpath,f)
            if os.path.exists(fp):
                total_size+=os.path.getsize(fp)
    return total_size 


async def read_yaml_file(file_path:str)->dict:
    try:
        with open(file_path,"rb") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise MyException(e,sys)    



def read_yaml_file_sync(file_path:str)->dict:
    try:
        with open(file_path,"rb") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise MyException(e,sys) 
    

async def write_yaml_file(file_path:str,content:object,replace:bool=False)->None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        if hasattr(content,"__dataclass_fields__"):
            content=asdict(content)
        if hasattr(content,"__dict__"):
            content=content.__dict__    
        with open(file_path,"w") as file:
            yaml.dump(content,file)
    except Exception as e:
        raise MyException(e,sys)                    
    
async def save_object(file_path:str,obj:object)->None:

    try:
        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        with open(file_path,"wb") as file_obj:
            dill.dump(obj,file_obj)


    except Exception as e:
        raise MyException(e,sys)   