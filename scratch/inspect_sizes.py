import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
from PIL import Image

im = Image.open('/var/www/withmore/uploads/tryon/tryon_c9577d3b562866de.jpeg')
print('User photo size:', im.size, 'mode:', im.mode, 'format:', im.format)

im2 = Image.open('/var/www/withmore/uploads/tryon/tryon_a9d508ff221b7a09.jpeg')
print('First photo size:', im2.size, 'mode:', im2.mode)

garm = Image.open('/var/www/withmore/uploads/tryon/garm_15.jpg')
print('Garment size:', garm.size, 'mode:', garm.mode)
"""

stdin, stdout, stderr = ssh.exec_command(f'/var/www/withmore/.venv/bin/python3 -c "{remote}"')
print(stdout.read().decode())
print(stderr.read().decode())
ssh.close()

