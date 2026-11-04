import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

stdin, stdout, stderr = ssh.exec_command('/var/www/withmore/.venv/bin/pip install gradio_client')
print("PIP INSTALL:\n", stdout.read().decode())
print("ERR:\n", stderr.read().decode())
ssh.close()

