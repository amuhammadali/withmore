import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8000/miniapp/product/2 | grep -o "index-BGsHVbEy.js"')
print("CHECK BUNDLE IN INDEX.HTML:", stdout.read().decode().strip())
ssh.close()

