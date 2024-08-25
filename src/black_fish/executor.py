from typing import List
from loguru import logger
import asyncio
import hashlib

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
        full_article_imgs = await spider.fetch_remote_full_articles(fresh_articles)

        remote_imgs = [img for img_list in full_article_imgs for img in img_list]
        remote_imgs: List[str] = list(set(remote_imgs))
        logger.info("{} spider fetch {} images", spider.source, len(remote_imgs))

        img_sem = asyncio.Semaphore(10)
        fetch_img_tasks = []
        for img_url in remote_imgs:
            img_name = hashlib.sha256(f"{img_url}".encode()).hexdigest() + "." + img_url.split(".")[-1]
            task = asyncio.create_task(
                spider.parallel_fetch_source(
                    img_url,
                    callback=spider.fetch_and_store_img,
                    is_bytes=True,
                    fresh_sem=img_sem,
                    # pass img_name to callback
                    img_name=img_name
                )
            )
            fetch_img_tasks.append(task)
        await asyncio.gather(*fetch_img_tasks)

        logger.info("{} spider save index", spider.source)
        await spider.save_index()
        await spider.close()
