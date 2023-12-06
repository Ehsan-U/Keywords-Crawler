import asyncio
import os.path
from playwright.async_api import async_playwright, TimeoutError
from aiolimiter import AsyncLimiter

from src.logger import logger
from src.config import SHEET_ID, NAVIGATION_TIMEOUT, WAIT_TIMEOUT
from src.utils import GoogleSheet


class Spider:


    def __init__(self, max_rate):
        self.google_sheet = GoogleSheet(SHEET_ID)
        self.rate_limit = AsyncLimiter(max_rate)


    async def handle_route(self, route):
        if route.request.resource_type in ['image']:
            await route.abort()
        else:
            await route.continue_()


    @staticmethod
    def add_scheme_to_url(url: str, default_scheme='http://'):
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = default_scheme + url
        return url


    async def check_website(self, browser, website):
        if not website:
            return ''

        website = self.add_scheme_to_url(website)
        async with self.rate_limit:
            page = await browser.new_page()
            try:
                logger.info(f"Getting: {website}")
                await page.goto(website, timeout=NAVIGATION_TIMEOUT)
                await page.wait_for_timeout(timeout=WAIT_TIMEOUT)
                content = await page.content()
            except TimeoutError:
                content = ''
            except Exception as e:
                logger.error(e)
                content = ''
            finally:
                await page.close()
                for keyword in self.keywords:
                    if keyword.lower() in content.lower():
                        return 'Yes'
                return "No"


    def load_keywords(self):
        if not os.path.exists("data/keywords.txt"):
            raise "Keywords file not exist"
        with open("data/keywords.txt", 'r') as f:
            keywords = f.read().split('\n')
        return keywords


    async def run(self):
        self.keywords = self.load_keywords()
        websites = self.google_sheet.get_col_values("Website")

        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)

            tasks = []
            for website in websites[1:50]:
                task = asyncio.create_task(self.check_website(browser, website))
                tasks.append(task)

            answers = await asyncio.gather(*tasks)

        self.google_sheet.create_col(col_name="Answers", col_idx=12)
        self.google_sheet.insert(col_name="Answers", values=answers)



