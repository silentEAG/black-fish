from abc import abstractmethod
from typing import Dict, List, Tuple, Union
from abc import ABC
from asyncio import Semaphore
from aiohttp import ClientSession
import hashlib
import asyncio
import re
import os
import aiofiles
import json
from loguru import logger

safe_filename_regex = re.compile(r"[\/\\\:\*\?\"\<\>\|]")
def safe_filename(filename):
    return safe_filename_regex.sub("_", filename)

class ArtcleStorage(object):
    def __init__(self):
        pass

class ArticlePreview(object):
    def __init__(self, source: str, title: str, url: str, publish_at: str):
        self.source = source
        self.title = title
        self.url = url
        self.publish_at = publish_at
        self.hash = hashlib.sha256(f"{source}{url}".encode()).hexdigest()
    
    def __str__(self) -> str:
        return f"source: {self.source}, title: {self.title}, url: {self.url}, publish_at: {self.publish_at}, hash: {self.hash}"

    """
    calculate sha256 with source and url
    """
    @staticmethod
    def calculate_hash(source, url):
        return hashlib.sha256(f"{source}{url}".encode()).hexdigest()
    
    def to_dict(self):
        return {
            'source': self.source,
            'title': self.title,
            'url': self.url,
            'publish_at': self.publish_at,
            'hash': self.hash
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(data['source'], data['title'], data['url'], data['publish_at'])

class ArticlePreviewEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ArticlePreview):
            return obj.to_dict()
        return super().default(obj)

"""
BaseArticleSpider
"""
class BaseArticleSpider(ABC):
    def __init__(self, source: str, fetch_limit_sem: int = 5, save_diretory: str = "docs"):
        self.source = source
        self.article_preview: List[ArticlePreview] = []
        self.article_preview_local: Dict[str, ArticlePreview] = {}
        self.fetch_limit_sem: Semaphore = Semaphore(fetch_limit_sem)
        self.save_diretory = save_diretory
        self.client: ClientSession = ...
        self.find_local_cache = False

    @abstractmethod
    async def fetch_remote_preview_articles(self) -> List[ArticlePreview]:
        ...

    @abstractmethod
    def parse_to_md(self, html_content: str):
        ...

    async def prepare_for_run(self):
        ...

    def set_save_directory(self, save_directory: str):
        self.save_diretory = save_directory

    async def save_item(self, content: Union[str, bytes], file_name: str, is_img: bool = False):
        save_to_item_path = f"{self.save_diretory}/{self.source}"
        os.makedirs(save_to_item_path, exist_ok=True)
        if is_img:
            save_to_item_path = f"{save_to_item_path}/img"
            os.makedirs(save_to_item_path, exist_ok=True)

        # async with aiofiles.open(f"{save_to_item_path}/{file_name}", "w" if isinstance(content, str) else "wb") as f:
            # await f.write(content)

        with open(f"{save_to_item_path}/{file_name}", "w" if isinstance(content, str) else "wb") as f:
            f.write(content)

    async def save_index(self):
        index_path = f"{self.save_diretory}/{self.source}/index"
        os.makedirs(index_path, exist_ok=True)

        index_file = f"{index_path}/idx.json"

        for article in self.article_preview:
            self.article_preview_local[article.hash] = article

        with open(index_file, "w") as f:
            json.dump(self.article_preview_local, f, cls=ArticlePreviewEncoder, ensure_ascii=False)

    async def load_index(self):
        index_path = f"{self.save_diretory}/{self.source}/index"
        os.makedirs(index_path, exist_ok=True)

        index_file = f"{index_path}/idx.json"

        if os.path.exists(index_file):
            with open(index_file, "r") as f:
                article_preview_local_dict = json.load(f)
                self.article_preview_local = {k: ArticlePreview.from_dict(v) for k, v in article_preview_local_dict.items()}

    def add_article_preview(
            self,
            title: str,
            url: str,
            publish_at: str
        ):

        # strip title
        title = title.strip()
        title = safe_filename(title)

        # check url
        url = url.strip()

        self.article_preview.append(
            ArticlePreview(
                source=self.source,
                title=title,
                url=url,
                publish_at=publish_at
            )
        )

    async def compare_local_and_return_fresh_articles(self):
        ...


    async def fetch_remote_full_articles(self, preview_articles: List[ArticlePreview]):
        fetch_tasks = []
        for preview_article in preview_articles:
            task = asyncio.create_task(
                self.parallel_fetch_source(
                    preview_article.url,
                    callback=self.parse_and_store_article,
                    preview_article=preview_article
                )
            )
            fetch_tasks.append(task)
        
        return await asyncio.gather(*fetch_tasks)

    async def parse_and_store_article(self, html_content, preview_article: ArticlePreview) -> List[str]:
        article_content_markdown = self.parse_to_md(html_content)

        img_re = re.compile(r'!\[.*?\]\((.*?)\)')
        remote_imgs = img_re.findall(article_content_markdown)

        for url in remote_imgs:
            local_img_url = "img/" + hashlib.sha256(f"{url}".encode()).hexdigest() + "." + url.split(".")[-1]
            article_content_markdown = article_content_markdown.replace(url, local_img_url)

        title = preview_article.title
        await self.save_item(article_content_markdown, f"{title}.md")

        return remote_imgs

    async def parallel_fetch_source(self, uri: str, callback = None, ignore_exception = False, fresh_sem: Union[None, Semaphore] = None, is_bytes=False, **kwargs):
        sem = fresh_sem if fresh_sem is not None else self.fetch_limit_sem
        async with sem:
            try:
                resp = await self.client.get(uri)
                if is_bytes:
                    text = await resp.read()
                else:
                    text = await resp.text()
            except:
                if ignore_exception:
                    logger.error(f"fetch {uri} failed")
                    return
                raise Exception(f"fetch {uri} failed")
        if callback is None:
            return text
        if kwargs:
            return await callback(text, **kwargs)
        return await callback(text)

    async def fetch_and_store_img(self, img: bytes, img_name: str):
        await self.save_item(img, img_name, is_img=True)

    async def close(self):
        await self.client.close()
