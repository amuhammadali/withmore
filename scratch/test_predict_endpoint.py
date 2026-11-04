import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import urllib.request, json

url = 'https://yisol-idm-vton.hf.space/api/predict'
payload = {
    'data': [
        {'background': {'path': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600', 'url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600'}, 'layers': [], 'composite': None},
        {'path': 'https://withmore.uz/uploads/sample.jpg', 'url': 'https://withmore.uz/uploads/sample.jpg'},
        'A suit',
        True,
        False,
        20,
        42
    ]
}

try:
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as res:
        print('predict status:', res.status)
        print('predict out:', res.read().decode()[:300])
except urllib.error.HTTPError as e:
    print('predict HTTP error:', e.code, e.read().decode()[:300])
except Exception as e:
    print('predict err:', e)
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("OUT:", stdout.read().decode())
print("ERR:", stderr.read().decode())
ssh.close()

