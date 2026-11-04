import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

stdin, stdout, stderr = ssh.exec_command('curl -I -s https://withmore.uz/uploads/products/3f5630dc517d4024ae486c2c21c06294.webp')
print(stdout.read().decode())
ssh.close()

