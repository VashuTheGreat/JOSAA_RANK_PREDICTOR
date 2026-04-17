from dotenv import load_dotenv
load_dotenv()

from logger import *


from api.app import app


import uvicorn as uv


# if __name__=="__main__":
#     uv.run("main:app",host="0.0.0.0",port=7860,reload=True)