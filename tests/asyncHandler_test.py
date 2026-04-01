
from utils.asyncHandler import asyncHandler
import asyncio
@asyncHandler
async def divide():
    x = 10 / 0
    return x


asyncio.run(divide())    

