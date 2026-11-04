import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import urllib.request, json, time

url = 'https://yisol-idm-vton.hf.space/call/tryon'
human_test = 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600'
garment_test = 'https://withmore.uz/uploads/sample.jpg'

payload = {
    'data': [
        {'background': {'path': human_test, 'url': human_test}, 'layers': [], 'composite': None},
        {'path': human_test, 'url': human_test},
        'A tailored suit',
        True,
        False,
        20,
        42
    ]
}

try:
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as res:
        data = json.loads(res.read().decode())
        event_id = data.get('event_id')
        print('Event ID received:', event_id)
except Exception as e:
    print('Error initiating call:', e)
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("OUT:", stdout.read().decode())
print("ERR:", stderr.read().decode())
ssh.close()
