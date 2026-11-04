import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import urllib.request, json

human_url = 'https://withmore.uz/uploads/tryon/tryon_a9d508ff221b7a09.jpeg'
garment_url = 'https://withmore.uz/uploads/products/3f5630dc517d4024ae486c2c21c06294.webp'

print('Testing with user photo:', human_url)
print('Testing with garment:', garment_url)

payload = {
    'data': [
        {'background': {'path': human_url, 'url': human_url}, 'layers': [], 'composite': None},
        {'path': garment_url, 'url': garment_url},
        'A tailored luxury suit',
        True,
        False,
        20,
        42
    ]
}

url = 'https://yisol-idm-vton.hf.space/call/tryon'
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=12) as res:
        data = json.loads(res.read().decode())
        event_id = data.get('event_id')
        print('Event ID:', event_id)
        
        poll_url = f'https://yisol-idm-vton.hf.space/call/tryon/{event_id}'
        poll_req = urllib.request.Request(poll_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(poll_req, timeout=35) as stream:
            for _ in range(40):
                line = stream.readline().decode('utf-8')
                if line.startswith('data:'):
                    raw = line[5:].strip()
                    if raw and raw != 'null':
                        parsed = json.loads(raw)
                        if isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
                            res_url = parsed[0].get('url')
                            print('GENERATED SUCCESS URL:', res_url)
                            break
except Exception as e:
    print('Error:', e)
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("OUT:\n", stdout.read().decode())
print("ERR:\n", stderr.read().decode())
ssh.close()

