from typing import List
import aiohttp
from parsel import Selector
from loguru import logger
from markdownify import markdownify as md

from ..base_spider import BaseArticleSpider, ArticlePreview

BASE_URL = "https://tttang.com"

class TTTangSpider(BaseArticleSpider):

    def __init__(self):
        super().__init__(source="TTTang", fetch_limit_sem=20)
        self.client = aiohttp.ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                "Referer": "https://tttang.com/"
            },
            timeout=aiohttp.ClientTimeout(8)
        )

    async def prepare_for_run(self):
        
        pass

    async def fetch_remote_preview_articles(self) -> List[ArticlePreview]:
        response = await self.client.get(BASE_URL + "/")
        first_page_text = await response.text()
        first_page_selector = Selector(text=first_page_text)

        total_pages = int(first_page_selector.css("a.page-link::attr(href)").re(r"page=(.*)")[-1])
        logger.debug("total pages: {}", total_pages)
        await self.parse_preview_articles_on_one_page(first_page_text)

        if self.find_local_cache:
            return self.article_preview

        for page in range(2, total_pages + 1):
            if self.find_local_cache:
                break
            resp = await self.client.get(BASE_URL + "/?page={}".format(page))
            text = await resp.text()
            await self.parse_preview_articles_on_one_page(text)

        return self.article_preview

    def parse_to_md(self, html_content: str):
        selector = Selector(text=html_content)
        article_content = selector.css("div.card-content").get()
        article_content_markdown = md(article_content)
        return article_content_markdown

    async def parse_preview_articles_on_one_page(self, text):
        selector = Selector(text=text)
        article_url_array = selector.css("a.title::attr(href)").getall()
        article_title_array = selector.css("a.title::text").getall()
        article_time_array = selector.xpath("//span[@class='time']/text()").re(r'\d{4}-\d{2}-\d{2}')

        article_title_array = [title.strip() for title in article_title_array]
        assert len(article_url_array) == len(article_title_array) == len(article_time_array)
        for url, title, time in zip(article_url_array, article_title_array, article_time_array):
            url = BASE_URL + url
            article_hash = ArticlePreview.calculate_hash(self.source, url)

            # current page and next page have cached
            if article_hash in self.article_preview_local.keys():
                self.find_local_cache = True
            self.add_article_preview(title=title, url=url, publish_at=time)