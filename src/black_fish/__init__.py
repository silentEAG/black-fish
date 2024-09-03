import asyncio
import sys

from loguru import logger

from black_fish.executor import Executor
from .config import Config
from .spiders.xz import XZSpider
from .spiders.tttang import TTTangSpider
from .spiders.qianxin import QAXSpider
from .base_spider import BaseArticleSpider

import time

async def runtime():
    config = Config()
    executor = Executor(config)
    # xz_spider = XZSpider()
    # tttang_spider = TTTangSpider()
    qax_spider = QAXSpider()
    executor.spiders = [qax_spider]

    start = time.time()
    await executor.run()

    end = time.time()
    print(end - start)
    

def main():
    logger.remove()
    logger.add(sys.stdout, colorize=True, format="<green>{time}</green> <level>{message}</level>")
    asyncio.run(runtime())