import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
with open('/var/www/withmore/.env', 'r') as f:
    lines = f.readlines()

new_lines = []
for l in lines:
    if l.startswith('DATABASE_URL='):
        new_lines.append('DATABASE_URL=sqlite:////var/www/withmore/whitmore.db\\n')
    else:
        new_lines.append(l)

with open('/var/www/withmore/.env', 'w') as f:
    f.writelines(new_lines)

print('Updated /var/www/withmore/.env with absolute path!')
"""

stdin, stdout, stderr = ssh.exec_command(f'/var/www/withmore/.venv/bin/python3 -c "{remote}"')
print(stdout.read().decode())
print(stderr.read().decode())

stdin, stdout, stderr = ssh.exec_command('systemctl restart whitmore')
stdout.channel.recv_exit_status()
print("Restarted whitmore!")

ssh.close()

