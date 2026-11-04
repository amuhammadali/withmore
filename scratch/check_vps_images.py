import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import os
from PIL import Image

# Check if product 2 image exists on VPS
upload_dir = '/var/www/withmore/backend/uploads'
for root, dirs, files in os.walk(upload_dir):
    for f in files:
        if f.endswith(('.jpg', '.png', '.webp')):
            print('Sample product image:', os.path.join(root, f))
            break
    if files:
        break
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("OUT:", stdout.read().decode())
print("ERR:", stderr.read().decode())
ssh.close()

