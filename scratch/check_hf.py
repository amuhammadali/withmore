import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import urllib.request, json
spaces = [
    'https://huggingface.co/api/spaces/yisol/IDM-VTON',
    'https://huggingface.co/api/spaces/Nymbo/Virtual-Try-On',
    'https://huggingface.co/api/spaces/Kwai-Kolors/Kolors-Virtual-Try-On'
]
for s in spaces:
    name = s.split('/')[-1]
    try:
        req = urllib.request.Request(s, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            stage = data.get('runtime', {}).get('stage')
            print(f'{name}: {stage}')
    except Exception as e:
        print(f'{name} ERR: {e}')
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("OUT:", stdout.read().decode())
print("ERR:", stderr.read().decode())
ssh.close()

