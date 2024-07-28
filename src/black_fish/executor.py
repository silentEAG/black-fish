from typing import List
from .base_spider import BaseArticleSpider
from .config import Config
from loguru import logger
import asyncio
import hashlib

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

        # # fetch remote article preview via spiders
        # total_remote_articles = await asyncio.gather(*[spider.fetch_remote_preview_articles() for spider in self.spiders])

        # fetch_tasks: List[asyncio.Task] = []
        # for spider, remote_articles in zip(self.spiders, total_remote_articles):

        #     logger.info("{} spider fetch {} remote articles", spider.source, len(remote_articles))

        #     # load local article preview
        #     await spider.load_index()
        #     logger.info("{} spider load {} local articles", spider.source, len(spider.article_preview_local))

        #     # compare remote and local
        #     fresh_articles = [article for article in remote_articles if article.hash not in spider.article_preview_local]
        #     logger.info("{} spider find {} fresh articles", spider.source, len(fresh_articles))

        #     # fetch full article content
        #     spider.article_preview = fresh_articles
        #     fetch_task = asyncio.create_task(spider.fetch_remote_full_articles(fresh_articles))
        #     fetch_tasks.append(fetch_task)

        # full_articles_result: List[asyncio.Task] = await asyncio.gather(*fetch_tasks)

        # fetch_img_tasks = []
        # for spider, remote_imgs in zip(self.spiders, full_articles_result):
        #     remote_imgs = [img for img_list in remote_imgs for img in img_list]
        #     # unique img
        #     remote_imgs: List[str] = list(set(remote_imgs))
        #     logger.info("{} spider fetch {} images", spider.source, len(remote_imgs))
        #     img_sem = asyncio.Semaphore(10)
        #     for img_url in remote_imgs:
        #         img_name = hashlib.sha256(f"{img_url}".encode()).hexdigest() + "." + img_url.split(".")[-1]
        #         # download img
        #         task = asyncio.create_task(
        #             spider.parallel_fetch_source(
        #                 img_url,
        #                 callback=spider.fetch_and_store_img,
        #                 is_bytes=True,
        #                 ignore_exception=True,
        #                 img_name=img_name,
        #                 fresh_sem=img_sem
        #             )
        #         )
        #         fetch_img_tasks.append(task)
        
        # await asyncio.gather(*fetch_img_tasks)



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
