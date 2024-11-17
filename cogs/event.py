#!/usr/bin/env python
from discord.ext import commands
from discord import app_commands
from discord import Interaction
from discord import Member

class Event(app_commands.Group):
  def __init__(self, bot: commands.Bot, name: str, description: str):
    super().__init__(name=name, description=description)
    self.bot = bot

  def hasPermission(self, user: Member) -> bool:
    for role in user.roles:
      if role.id == self.bot.config.ADMIN:
        return True
    return False

  @app_commands.command(name="start", description="Start an event leaderboard")
  async def start(self, interaction: Interaction) -> None:
    if not self.hasPermission(interaction.user): await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
    if self.bot._running: await interaction.response.send_message("Event already started")    
    self.bot.scrape_file.start()
    self.bot._running = True
    await interaction.response.send_message("Starting new event leaderboard...", ephemeral=True)

  @app_commands.command(name="stop", description="Stop an event leaderboard")
  async def stop(self, interaction: Interaction) -> None:
    if not self.hasPermission(interaction.user): await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
    if not self.bot._running: await interaction.response.send_message("Event already stopped", ephemeral=True)
    self.bot.scrape_file.stop()

    # Reset trackers
    self.bot._running   = False
    self.bot.log_file   = ""
    self.bot.log_index  = -1
    self.bot.players    = []
    self.bot.gamertags  = []
    self.bot.message_id = ""
    
    await interaction.response.send_message("Stopping event leaderboard...", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
  bot.tree.add_command(Event(bot, name="event", description="start or stop an event leaderboard"))
