import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

print("Starting npm run build on VPS...")
stdin, stdout, stderr = ssh.exec_command('cd /var/www/withmore/frontend && npm run build')
print("BUILD OUT:\n", stdout.read().decode())
print("BUILD ERR:\n", stderr.read().decode())

print("Restarting whitmore service...")
stdin, stdout, stderr = ssh.exec_command('systemctl restart whitmore && systemctl status whitmore --no-pager -n 3')
print("SERVICE STATUS:\n", stdout.read().decode())

ssh.close()
print("Done!")

