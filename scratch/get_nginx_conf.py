import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

stdin, stdout, stderr = ssh.exec_command('cat /etc/nginx/sites-enabled/*')
print("NGINX CONF:\n", stdout.read().decode())
ssh.close()

