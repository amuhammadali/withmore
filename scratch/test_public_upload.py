import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

stdin, stdout, stderr = ssh.exec_command('curl -I -s https://withmore.uz/uploads/tryon/tryon_a9d508ff221b7a09.jpeg')
print(stdout.read().decode())
ssh.close()

