import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import urllib.request

req = urllib.request.Request('http://127.0.0.1:8000/miniapp/product/2', headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as res:
        content = res.read().decode('utf-8')
        print('HTTP Status:', res.status)
        print('Content length:', len(content))
        print('Snippet:\n', content[:400])
except Exception as e:
    print('Error:', e)
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("OUT:", stdout.read().decode())
print("ERR:", stderr.read().decode())
ssh.close()

