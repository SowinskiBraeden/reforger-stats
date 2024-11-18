#!/usr/bin/env python
from re import match
from paramiko import SFTPClient
from datetime import datetime
from typing import Tuple
from discord.ext import commands

# Regex templates
class Templates:
  Gamertag:    str = r'(?P<time>.*)  DEFAULT      : BattlEye Server: Adding player identity=(?P<_>.*), name=\'(?P<gamertag>.*)\''
  IpAddress:   str = r'(?P<time>.*)  DEFAULT      : BattlEye Server: \'Player #(?P<_>.*) (?P<gamertag>.*) \((?P<ip_addr>.*):(?P<port>.*)\) connected\''
  PlayerID:    str = r'(?P<time>.*)   NETWORK      : ### Updating player: PlayerId=(?P<_>.*), Name=(?P<gamertag>.*), IdentityId=(?P<player_guid>.*)'
  BattlEyeGUI: str = r'(?P<time>.*)  DEFAULT      : BattlEye Server: \'Player #(?P<_>.*) (?P<gamertag>.*) - BE GUID: (?P<battleye_guid>.*)\''
  Admin:       str = r'(?P<time>.*)   NETWORK      : Player \'(?P<gamertag>.*)\' signed in as server admin.'
  Kill:        str = r'(?P<time>.*)   SCRIPT       : ServerAdminTools \| Event serveradmintools_player_killed \| player: (?P<victim_gamertag>.*), instigator: (?P<killer_gamertag>.*), friendly: (?P<friendly>.*)'

# Get initial players data
def getPlayers(bot: commands.Bot, logs: list[str]) -> None:
  gt_data = match(Templates.Gamertag, logs[i])
  for i in range(0, len(logs)):
    # Generate new player data or update connections/IP info
    if gt_data is not None:
      ip_data = match(Templates.IpAddress, logs[i+1])
      if gt_data.group("gamertag") in bot.gamertags:
        for identity in bot.players:
          if identity["gamertag"] == gt_data.group("gamertag"):
            index = bot.players.index(identity)
            bot.players[index]["connections"] += 1 
            bot.players[index]["ip"]          = ip_data.group("ip_addr")
            bot.players[index]["port"]        = ip_data.group("port")
      else:
        be_data = match(Templates.BattlEyeGUI, logs[i+3])
        bot.players.append({
          "gamertag":         gt_data.group("gamertag"),
          "ip":               ip_data.group("ip_addr"),
          "port":             ip_data.group("port"),
          "player_guid":      None,
          "battleye_guid":    be_data.group("battleye_guid"),
          "connections":      1,
          "kills":            0,
          "deaths":           0,
          "KDR":              0,
          "killstreak":       0,
          "bestKillstreak":   0,
          "deathstreak":      0,
          "worstDeathstreak": 0,
          "admin":            False
        })
        bot.gamertags.append(gt_data.group("gamertag"))

# Function to process new logs in an array from a given starting index
def readLogFromIndex(
  bot: commands.Bot,
  logs: list[str]
) -> None:

  # Check each line for data to extract and load into json
  for i in range(bot.log_index, len(logs)):
    gt_data       = match(Templates.Gamertag, logs[i])
    identity_data = match(Templates.PlayerID, logs[i])
    admin_data    = match(Templates.Admin, logs[i])
    kill_data     = match(Templates.Kill, logs[i])

    # Gather in game player GUID    
    if identity_data is not None:
      for identity in bot.players:
        if identity["gamertag"] == identity_data.group("gamertag"):
          bot.players[bot.players.index(identity)]["player_guid"] = identity_data.group("player_guid")
      continue

    # Has player logged into admin/gamemaster
    if admin_data is not None:
      for identity in bot.players:
        if identity["gamertag"] == admin_data.group("gamertag"):
          bot.players[bot.players.index(identity)]["admin"] = True  
      continue

    # Contribute to playerts KDR
    if kill_data is not None:
      if kill_data.group("friendly") == "true": continue # Ignore friendly kills
      if kill_data.group("killer_gamertag") == kill_data.group("victim_gamertag"): continue # Ignore suicide
      for identity in bot.players:
        if identity["gamertag"] == kill_data.group("killer_gamertag"):
          index = bot.players.index(identity)          
          bot.players[index]["kills"]          += 1
          bot.players[index]["killstreak"]     += 1
          bot.players[index]["deathstreak"]    = 0
          bot.players[index]["bestKillstreak"] = bot.players[index]["killstreak"] if bot.players[index]["killstreak"] > bot.players[index]["bestKillstreak"] else bot.players[index]["bestKillstreak"]
          bot.players[index]["KDR"]            = round(bot.players[index]["kills"] / (1 if bot.players[index]["deaths"] == 0 else bot.players[index]["deaths"]), 2)

        if identity["gamertag"] == kill_data.group("victim_gamertag"):
          index = bot.players.index(identity)
          bot.players[index]["deaths"] += 1
          bot.players[index]["deathstreak"] += 1
          bot.players[index]["killstreak"] = 0
          bot.players[index]["worstDeathstreak"] = bot.players[index]["deathstreak"] if bot.players[index]["deathstreak"] > bot.players[index]["worstDeathstreak"] else bot.players[index]["worstDeathstreak"]
          bot.players[index]["KDR"] = round(bot.players[index]["kills"] / (1 if bot.players[index]["deaths"] == 0 else bot.players[index]["deaths"]), 2)

      continue

    # Generate new player data or update connections/IP info
    if gt_data is not None:
      ip_data = match(Templates.IpAddress, logs[i+1])
      if gt_data.group("gamertag") in bot.gamertags:
        for identity in bot.players:
          if identity["gamertag"] == gt_data.group("gamertag"):
            index = bot.players.index(identity)
            bot.players[index]["connections"] += 1 
            bot.players[index]["ip"]          = ip_data.group("ip_addr")
            bot.players[index]["port"]        = ip_data.group("port")
      else:
        be_data = match(Templates.BattlEyeGUI, logs[i+3])
        bot.players.append({
          "gamertag":         gt_data.group("gamertag"),
          "ip":               ip_data.group("ip_addr"),
          "port":             ip_data.group("port"),
          "player_guid":      None,
          "battleye_guid":    be_data.group("battleye_guid"),
          "connections":      1,
          "kills":            0,
          "deaths":           0,
          "KDR":              0,
          "killstreak":       0,
          "bestKillstreak":   0,
          "deathstreak":      0,
          "worstDeathstreak": 0,
          "admin":            False
        })
        bot.gamertags.append(gt_data.group("gamertag"))
      continue

  print("done reading logs...")
  return

def getLatestDir(sftp: SFTPClient, remote_path: str) -> str:
  log_directory:    str       = ""
  sub_directories:  list[str] = sftp.listdir(remote_path)
  base_datetime:    datetime  = datetime(2000, 1, 1)
  
  # Read sub-directories to get latest modified directory
  for directory in sub_directories:
    date_time_modified = str(sftp.lstat(f"{remote_path}/{directory}"))
    date_time_modified = date_time_modified[len(date_time_modified) - 14:][:-2]
    file_datetime = datetime.strptime(date_time_modified, '%y %b %H:%M')
    
    if file_datetime > base_datetime:
      base_datetime = file_datetime
      log_directory = directory

  return log_directory
