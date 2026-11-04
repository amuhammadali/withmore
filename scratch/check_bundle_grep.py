import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

stdin, stdout, stderr = ssh.exec_command('grep -o "AIVirtualFittingModal" /var/www/withmore/frontend/dist/assets/*.js | wc -l')
print("Occurrences of AIVirtualFittingModal in dist:", stdout.read().decode().strip())
ssh.close()

