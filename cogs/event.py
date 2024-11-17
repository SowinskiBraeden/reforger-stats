#!/usr/bin/env python
from discord.ext import commands
from discord import app_commands
from discord import Interaction

class Event(app_commands.Group):
  def __init__(self, bot: commands.Bot, name: str, description: str):
    super().__init__(name=name, description=description)
    self.bot = bot

  @app_commands.command(name="start", description="Start an event leaderboard")
  async def start(self, interaction: Interaction) -> None:
    if self.bot._running: await interaction.response.send_message("Event already started")    
    self.bot.scrape_file.start()
    self.bot._running = True
    await interaction.response.send_message("Starting new event leaderboard...")

  @app_commands.command(name="stop", description="Stop an event leaderboard")
  async def stop(self, interaction: Interaction) -> None:
    if not self.bot._running: await interaction.response.send_message("Event already stopped")
    self.bot.scrape_file.stop()

    # Reset trackers
    self.bot._running   = False
    self.bot.log_file   = ""
    self.bot.log_index  = -1
    self.bot.players    = []
    self.bot.gamertags  = []
    self.bot.message_id = ""
    
    await interaction.response.send_message("Stopping event leaderboard...")

async def setup(bot: commands.Bot) -> None:
  bot.tree.add_command(Event(bot, name="event", description="start or stop an event leaderboard"))
