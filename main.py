#!/usr/bin/env python
from discord import Intents
import asyncio

from src.ReforgerStatsBot import ReforgerStats
from config import Config

async def main() -> None:
  intents = Intents.default()
  intents.message_content = True
  bot = ReforgerStats(Config(), "!", intents)

  async with bot:
    await bot.start(bot.config.TOKEN)

if __name__ == "__main__":
  asyncio.run(main())
