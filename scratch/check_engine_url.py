import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import sys
sys.path.insert(0, '/var/www/withmore/backend')
from app.config import get_settings
from app.db import engine
print('DATABASE_URL:', get_settings().DATABASE_URL)
print('ENGINE URL:', engine.url)
"""

stdin, stdout, stderr = ssh.exec_command(f'/var/www/withmore/.venv/bin/python3 -c "{remote}"')
print("OUT:\n", stdout.read().decode())
print("ERR:\n", stderr.read().decode())
ssh.close()

