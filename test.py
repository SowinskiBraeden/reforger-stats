import requests
import time

webhook = "https://discord.com/api/webhooks/1307501649119543398/N-SWGPSTuvaPEk_u9v7WdMJqKASmk0o8EzvjTFDC_1mqDjqWGybSOVGU1iVDZ-LmBsNJ"

identities = [
  {"gamertag": "what", "kills": 19, "deaths": 6},
  {"gamertag": "mcdazzzled", "kills": 52, "deaths": 11},
  {"gamertag": "erebus", "kills": 24, "deaths": 14}
]  

def createEmbed(players: list[dict]) -> dict:
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

def send(content: dict) -> str | None:
  params = { "wait": True }
  resp = requests.post(f"{webhook}", json=content, params=params)
  return None if resp.status_code != 200 else resp.json()["id"]

def delete(id: str) -> int:
  return requests.delete(f"{webhook}/messages/{id}")

def update(content: dict, id: str) -> int:
  resp = requests.patch(f"{webhook}/messages/{id}", json=content)
  return resp.status_code

content = createEmbed(identities)
message_id = send(content)
if message_id is None:
  print("failed")
  exit()
print(identities[2])
identities[0]["kills"] = 30
time.sleep(4)
content = createEmbed(identities)
code = update(content, message_id)
print(code)
