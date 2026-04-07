import yaml
import os
from exception import MyException
import sys
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