#!/usr/bin/env python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
  TOKEN:         str = os.getenv("DISCORD_TOKEN")
  GUILD:         str = os.getenv("DISCORD_GUILD")
  ADMIN:         str = int(os.getenv("ADMIN_ROLE"))
  WEBHOOK:       str = os.getenv("WEBHOOK")

  SFTP_HOST:     str = os.getenv("SFTP_HOST")
  SFTP_PORT:     int = int(os.getenv("SFTP_PORT"))
  SFTP_USERNAME: str = os.getenv("SFTP_USERNAME")
  SFTP_PASSWORD: str = os.getenv("SFTP_PASSWORD")