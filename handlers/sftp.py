#!/usr/bin/env python
from paramiko import SSHClient, AutoAddPolicy, SFTPClient
from typing import Tuple
from config import Config

def createSSHClient(config: Config) -> Tuple[SFTPClient, SSHClient]:
  # Create SSH client
  ssh_client = SSHClient()
  ssh_client.set_missing_host_key_policy(AutoAddPolicy)

  # Connect to SFTP server && create SFTP session
  ssh_client.connect(
    hostname            = config.SFTP_HOST,
    port                = config.SFTP_PORT,
    username            = config.SFTP_USERNAME,
    password            = config.SFTP_PASSWORD,
    allow_agent         = False,
    look_for_keys       = False,
    disabled_algorithms = { 'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512'] }
  )
  sftp = ssh_client.open_sftp()
  return sftp, ssh_client
