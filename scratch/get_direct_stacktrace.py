import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import sys
sys.path.insert(0, '/var/www/withmore/backend')

from app.db import get_db
from app.routers.shop import generate_tryon, TryOnIn
import asyncio

db = next(get_db())
body = TryOnIn(product_id=15, human_image_url='/uploads/tryon/tryon_c9577d3b562866de.jpeg')

try:
    res = asyncio.run(generate_tryon(body, db))
    print('SUCCESS:', res)
except Exception as e:
    import traceback
    traceback.print_exc()
"""

stdin, stdout, stderr = ssh.exec_command(f'/var/www/withmore/.venv/bin/python3 -c "{remote}"')
print("DIRECT STACKTRACE:\n", stdout.read().decode())
print("STDERR:\n", stderr.read().decode())
ssh.close()

