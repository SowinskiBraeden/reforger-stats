#!/usr/bin/env python
from discord import Intents
import asyncio

from src.ReforgerStatsBot import ReforgerStats
from config import Config

intents = Intents.default()
intents.message_content = True
bot = ReforgerStats(Config(), "!", intents)

async def main() -> None:
  async with bot:
    await bot.start(bot.config.TOKEN)

asyncio.run(main())
