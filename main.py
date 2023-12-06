from src.spider import Spider
import asyncio


s = Spider(max_rate=150)
asyncio.run(s.run())