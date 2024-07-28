import asyncio
import sys

from loguru import logger

from black_fish.executor import Executor
from .config import Config
from .spiders.xz import XZSpider
from .spiders.tttang import TTTangSpider
from .base_spider import BaseArticleSpider

import time

async def runtime():
    config = Config()
    executor = Executor(config)
    xz_spider = XZSpider()
    # tttang_spider = TTTangSpider()
    executor.spiders = [xz_spider]

    start = time.time()
    await executor.run()

    # await tttang_spider.fetch_remote_preview_articles()

    # await xz_spider.prepare_for_run()
    # await xz_spider.close()

    # f = open("./xz-sample.html", "r")
    # xz_sample_content = f.read()
    # xz_spider.parse_to_md(xz_sample_content)

    end = time.time()
    print(end - start)
    

def main():
    logger.remove()
    logger.add(sys.stdout, colorize=True, format="<green>{time}</green> <level>{message}</level>")
    asyncio.run(runtime())