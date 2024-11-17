#!/usr/bin/env python
from re import match
from paramiko import SFTPClient
from datetime import datetime
from typing import Tuple

# Regex templates
class Templates:
  Gamertag:    str = r'(?P<time>.*)  DEFAULT      : BattlEye Server: Adding player identity=(?P<_>.*), name=\'(?P<gamertag>.*)\''
  IpAddress:   str = r'(?P<time>.*)  DEFAULT      : BattlEye Server: \'Player #(?P<_>.*) (?P<gamertag>.*) \((?P<ip_addr>.*):(?P<port>.*)\) connected\''
  PlayerID:    str = r'(?P<time>.*)   NETWORK      : ### Updating player: PlayerId=(?P<_>.*), Name=(?P<gamertag>.*), IdentityId=(?P<player_guid>.*)'
  BattlEyeGUI: str = r'(?P<time>.*)  DEFAULT      : BattlEye Server: \'Player #(?P<_>.*) (?P<gamertag>.*) - BE GUID: (?P<battleye_guid>.*)\''
  Admin:       str = r'(?P<time>.*)   NETWORK      : Player \'(?P<gamertag>.*)\' signed in as server admin.'
  Kill:        str = r'(?P<time>.*)   SCRIPT       : ServerAdminTools \| Event serveradmintools_player_killed \| player: (?P<victim_gamertag>.*), instigator: (?P<killer_gamertag>.*), friendly: (?P<friendly>.*)'

# Function to process new logs in an array from a given starting index
def readLogFromIndex(
  startingIndex: int,
  logs:          list[str],
  identities: list[dict],
  gamertags: list[str]
) -> Tuple[list[dict], list[str]]: # Return updated identities
    
  # Check each line for data to extract and load into json
  for i in range(startingIndex, len(logs)):
    gt_data       = match(Templates.Gamertag, logs[i])
    identity_data = match(Templates.PlayerID, logs[i])
    admin_data    = match(Templates.Admin, logs[i])
    kill_data     = match(Templates.Kill, logs[i])

    # Gather in game player GUID    
    if identity_data is not None:
      for identity in identities:
        if identity["gamertag"] == identity_data.group("gamertag"):
          identities[identities.index(identity)]["player_guid"] = identity_data.group("player_guid")
      continue

    # Has player logged into admin/gamemaster
    if admin_data is not None:
      for identity in identities:
        if identity["gamertag"] == admin_data.group("gamertag"):
          identities[identities.index(identity)]["admin"] = True  
      continue

    # Contribute to playerts KDR
    if kill_data is not None:
      if kill_data.group("friendly") == "true": continue # Ignore friendly kills
      if kill_data.group("killer_gamertag") == kill_data.group("victim_gamertag"): continue # Ignore suicide
      for identity in identities:
        if identity["gamertag"] == kill_data.group("killer_gamertag"):
          index = identities.index(identity)
          
          identities[index]["kills"]          += 1
          identities[index]["killstreak"]     += 1
          identities[index]["deathstreak"]    = 0
          identities[index]["bestKillstreak"] = identities[index]["killstreak"] if identities[index]["killstreak"] > identities[index]["bestKillstreak"] else identities[index]["bestKillstreak"]
          identities[index]["KDR"]            = round(identities[index]["kills"] / (1 if identities[index]["deaths"] == 0 else identities[index]["deaths"]), 2)
          pass
        if identity["gamertag"] == kill_data.group("victim_gamertag"):
          index = identities.index(identity)

          identities[index]["deaths"] += 1
          identities[index]["deathstreak"] += 1
          identities[index]["killstreak"] = 0
          identities[index]["worstDeathstreak"] = identities[index]["deathstreak"] if identities[index]["deathstreak"] > identities[index]["worstDeathstreak"] else identities[index]["worstDeathstreak"]
          identities[index]["KDR"] = round(identities[index]["kills"] / (1 if identities[index]["deaths"] == 0 else identities[index]["deaths"]), 2)
          pass

      continue

    # Generate new player data or update connections/IP info
    if gt_data is not None:
      ip_data = match(Templates.IpAddress, logs[i+1])
      if gt_data.group("gamertag") in gamertags:
        for identity in identities:
          if identity["gamertag"] == gt_data.group("gamertag"):
            index = identities.index(identity)
            identities[index]["connections"] += 1 
            identities[index]["ip"]          = ip_data.group("ip_addr")
            identities[index]["port"]        = ip_data.group("port")
      else:
        be_data = match(Templates.BattlEyeGUI, logs[i+3])
        identities.append({
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
        gamertags.append(gt_data.group("gamertag"))
      continue

  return identities, gamertags

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

def scrape(bot) -> None:
  pass
