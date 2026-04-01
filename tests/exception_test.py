import sys
from exception import MyException

try:
    a=10/0

except Exception as e:
    raise MyException(e,sys)