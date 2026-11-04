import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

stdin, stdout, stderr = ssh.exec_command('ls -la /var/www/withmore/data/uploads/tryon /var/www/withmore/data/uploads 2>&1 | head -n 20')
print(stdout.read().decode())
ssh.close()

