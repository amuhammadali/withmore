import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import os

assets = '/var/www/withmore/frontend/dist/assets'
found = []
for f in os.listdir(assets):
    if f.endswith('.js'):
        with open(os.path.join(assets, f), 'r', encoding='utf-8') as fp:
            content = fp.read()
            for s in ['AI VIRTUAL FITTING', 'WITHMORE ATELIER', 'Mato qomatingizga', 'showTryOnModal', 'AI VIRTUAL STILIST']:
                if s in content:
                    found.append(s)
print('Found strings in dist JS:', found)
"""
stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("OUT:", stdout.read().decode())
print("ERR:", stderr.read().decode())
ssh.close()

