import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

stdin, stdout, stderr = ssh.exec_command('cd /var/www/withmore && git fetch origin main && git reset --hard origin/main && git log -1 --oneline')
print("PULL RESULT:\n", stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command('systemctl restart whitmore')
stdout.channel.recv_exit_status()
print("RESTARTED!")
ssh.close()

