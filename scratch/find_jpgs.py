import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

stdin, stdout, stderr = ssh.exec_command('find /var/www/withmore -name "*.jpg" | head -n 10')
print("FOUND JPGS:\n", stdout.read().decode())
ssh.close()

