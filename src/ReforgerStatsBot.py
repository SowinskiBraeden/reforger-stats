#!/usr/bin/env python
from paramiko import SSHClient, SFTPClient, SFTPFile
from discord import Intents
from discord.ext import commands
from discord.ext import tasks
from discord import Object
from os import listdir, getcwd
import requests

from handlers.sftp import createSSHClient
from handlers.logs import getLatestDir, readLogFromIndex
from config import Config

class ReforgerStats(commands.Bot):
  def __init__(self, config: Config, prefix: str, intents: Intents):
    super().__init__(command_prefix=prefix, intents=intents)
    self.config:     Config     = config
    self._running:   bool       = False
    self.log_dir:    str        = ""
    self.log_index:  int        = -1
    self.message_id: str        = ""
    self.players:    list[dict] = []
    self.gamertags:  list[str]  = []
    self.ssh:        SSHClient  = None
    self.sftp:       SFTPClient = None

  async def on_ready(self: commands.Bot) -> None:
    print(f"Logged in as {self.user}")
    await self.load_cogs()
    # self.scrape_file.start()

  async def load_cogs(self: commands.Bot):
    for filename in listdir(f"{getcwd()}/cogs"):
      if filename.endswith('.py'):
        cog = filename[:-3]
        try:
          await self.load_extension(f"cogs.{cog}")
        except Exception as e:
          exception = f"{type(e).__name__}: {e}"
          print(exception)

    try:
      guild = Object(id=self.config.GUILD)
      self.tree.copy_global_to(guild=guild)
      synced = await self.tree.sync(guild=guild)
      print(f"[{guild.id}] Synced {len(synced)} command(s)")
    except Exception as e:
      exception = f"{type(e).__name__}: {e}"
      print(exception)

  async def createLeaderboardEmbed(self, players: list[dict]) -> dict:
    sorted_players = sorted(players, key=lambda a: a["kills"], reverse=True)
    description = ""
    rank = 1
    for player in sorted_players:
      description += f"> **{rank}.** {player['gamertag']}\n> ***Kills*** {player['kills']}\n> ***Deaths*** {player['deaths']}\n\n"
      rank += 1
    
    return {
      "embeds": [{
        "title": "Leaderboard",
        "description": description
      }]
    }

  async def webhookSend(self: commands.Bot, content: dict) -> str | None:
    params = { "wait": True }
    resp = await requests.post(f"{self.config.WEBHOOK}", json=content, params=params)
    return None if resp.status_code != 200 else resp.json()["id"]

  async def webhookDeleteMessage(self) -> None:
    if self.message_id == "": return
    requests.delete(f"{self.config.WEBHOOK}/messages/{self.message_id}")

  async def webhookUpdateMessage(self, content: dict) -> None:
    if self.message_id == "": return
    requests.patch(f"{self.config.WEBHOOK}/messages/{self.message_id}", json=content).status_code

  @tasks.loop(seconds=60)
  async def scrape_file(self) -> None:
    # Create SSH && SFTP sessions if needed
    if self.ssh is None or self.sftp is None: self.sftp, self.ssh = createSSHClient(self.config)

    remote_path = "/profile/logs"
    if self.log_dir == "": self.log_dir = getLatestDir(self.sftp, remote_path)

    # Read data
    file:  SFTPFile  = self.sftp.open(f"{remote_path}/{self.log_dir}/console.log")
    lines: list[str] = file.readlines()
    if self.log_index == -1: self.log_index = len(lines) - 1
    self.players, self.gamertags = readLogFromIndex(self.log_index, lines, self.players, self.gamertags)
    self.log_index = len(lines) - 1
    file.close()

    # Send leaderboard embeds via webhook
    content: dict = await self.createLeaderboardEmbed(self.players)
    if self.message_id == "": await self.webhookSend(content)
    else: await self.webhookUpdateMessage(content)

    # Close SSH && SFTP sessions and file
    self.sftp.close()
    self.ssh.close()
