import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import urllib.request, json

# Test connecting to yisol-idm-vton space info
url = 'https://yisol-idm-vton.hf.space/info'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as res:
        data = json.loads(res.read().decode())
        print('Endpoints in space:', list(data.get('named_endpoints', {}).keys()))
except Exception as e:
    print('Error:', e)
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("OUT:", stdout.read().decode())
print("ERR:", stderr.read().decode())
ssh.close()
