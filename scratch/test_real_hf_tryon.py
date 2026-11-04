import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import urllib.request, json, time

# Let's test yisol-idm-vton with REAL images
human_url = 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=600&q=80'
garment_url = 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?auto=format&fit=crop&w=600&q=80'

payload = {
    'data': [
        {'background': {'path': human_url, 'url': human_url}, 'layers': [], 'composite': None},
        {'path': garment_url, 'url': garment_url},
        'A casual shirt',
        True,
        False,
        20,
        42
    ]
}

url = 'https://yisol-idm-vton.hf.space/call/tryon'
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as res:
        data = json.loads(res.read().decode())
        event_id = data.get('event_id')
        print('Event ID received:', event_id)
        
        # Read SSE
        poll_url = f'https://yisol-idm-vton.hf.space/call/tryon/{event_id}'
        poll_req = urllib.request.Request(poll_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(poll_req, timeout=40) as stream:
            for _ in range(30):
                line = stream.readline().decode('utf-8')
                if line.startswith('event:'):
                    print('SSE:', line.strip())
                if line.startswith('data:'):
                    print('SSE DATA:', line[:120].strip())
                    if 'complete' in line or 'url' in line:
                        break
except Exception as e:
    print('Error:', e)
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("OUT:\n", stdout.read().decode())
print("ERR:\n", stderr.read().decode())
ssh.close()

