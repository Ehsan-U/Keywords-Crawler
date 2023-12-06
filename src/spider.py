import asyncio
import os.path
from playwright.async_api import async_playwright
from aiolimiter import AsyncLimiter

from src.logger import logger
from src.config import SHEET_ID
from src.utils import GoogleSheet


class Spider:
    NAVIGATION_TIMEOUT: int = 60*1000
    WAIT_TIMEOUT: int = 5*1000


    def __init__(self):
        self.google_sheet = GoogleSheet(SHEET_ID)


    async def handle_route(self, route):
        if route.request.resource_type in ['image']:
            await route.abort()
        else:
            await route.continue_()


    async def init_playwright(self):
        self.play = await async_playwright().start()
        self.browser = await self.play.firefox.launch(headless=True)
        self.page = await self.browser.new_page()
        await self.page.route("**/*", self.handle_route)


    async def check_website(self, website):
        try:
            await self.page.goto(website, timeout=self.NAVIGATION_TIMEOUT)
            await self.page.wait_for_timeout(timeout=self.WAIT_TIMEOUT)
            content = await self.page.content()

            for keyword in self.keywords:
                if keyword.lower() in content.lower():
                    return 'Yes'

        except Exception as e:
            logger.error(e)


    def load_keywords(self):
        if not os.path.exists("data/keywords.txt"):
            raise "Keywords file not exist"
        with open("data/keywords.txt", 'r') as f:
            keywords = f.read().split('\n')
        return keywords

    async def run(self):
        answers = []
        self.keywords = self.load_keywords()



        await self.init_playwright()

        websites = []
        for website in websites:
            answer = self.check_website(website)
            answers.append(answer)

        await self.close_playwright()


    async def close_playwright(self):
        await self.browser.close()
        await self.play.stop()


s = Spider()
asyncio.run(s.run())