import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

stdin, stdout, stderr = ssh.exec_command('cd /var/www/withmore && git reset --hard origin/main && git pull origin main')
print("GIT PULL:\n", stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command('systemctl restart whitmore && systemctl status whitmore --no-pager -n 3')
print("SERVICE:\n", stdout.read().decode())

ssh.close()
print("Backend real AI successfully restarted!")

