from typing import List
from loguru import logger
import asyncio

from .base_spider import BaseArticleSpider
from .config import Config

class Executor(object):
    def __init__(self, config: Config):
        self.config = config
        self.spiders: List[BaseArticleSpider] = ...

    def set_directory(self, directory: str):
        for spider in self.spiders:
            spider.set_save_directory(directory)

    async def run(self):

        spider_tasks = []
        for spider in self.spiders:
            task = asyncio.create_task(self.run_spider(spider))
            spider_tasks.append(task)
        await asyncio.gather(*spider_tasks)

    async def run_spider(self, spider: BaseArticleSpider):

        await spider.load_index()
        logger.info("{} spider load {} local articles", spider.source, len(spider.article_preview_local))
        
        remote_articles = await spider.fetch_remote_preview_articles()
        logger.info("{} spider fetch {} remote articles", spider.source, len(remote_articles))

        fresh_articles = [article for article in remote_articles if article.hash not in spider.article_preview_local]
        logger.info("{} spider find {} fresh articles", spider.source, len(fresh_articles))

        spider.article_preview = fresh_articles
        await spider.fetch_remote_full_articles(fresh_articles)

        logger.info("{} spider save index", spider.source)
        await spider.save_index()
        await spider.close()
