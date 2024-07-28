import black_fish
import black_fish.spiders
import black_fish.spiders.xz

xz_spider = black_fish.spiders.xz.XZSpider("XZ")

xz_spider.fetch_remote_articles()