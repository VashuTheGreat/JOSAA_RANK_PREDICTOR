
import os

# traces size of every file in a folder
def get_dir_size(path):
    total_size=0
    for dirpath,_,filenames in os.walk(path):
        for f in filenames:
            fp=os.path.join(dirpath,f)
            if os.path.exists(fp):
                total_size+=os.path.getsize(fp)
    return total_size 