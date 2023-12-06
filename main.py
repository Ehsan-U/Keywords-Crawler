from src.spider import Spider
import asyncio


s = Spider(max_rate=100)
asyncio.run(s.run())