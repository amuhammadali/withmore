import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import urllib.request, json
from PIL import Image

# Convert the product 15 webp to a clean jpg in uploads/tryon
webp_path = '/var/www/withmore/uploads/products/b3479ffe9aa94a08af1a5ea61e96cdad.webp'
jpg_path = '/var/www/withmore/uploads/tryon/garm_15.jpg'
Image.open(webp_path).convert('RGB').save(jpg_path, 'JPEG', quality=95)

garment_url = 'https://withmore.uz/uploads/tryon/garm_15.jpg'
human_url = 'https://withmore.uz/uploads/tryon/tryon_c9577d3b562866de.jpeg'

payload = {
    'data': [
        {'background': {'path': human_url, 'url': human_url}, 'layers': [], 'composite': None},
        {'path': garment_url, 'url': garment_url},
        'A tailored luxury shirt',
        True,
        False,
        20,
        42
    ]
}
call_url = 'https://yisol-idm-vton.hf.space/call/tryon'
req = urllib.request.Request(call_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json', 'User-Agent': 'Withmore-AI/1.0'})
res = urllib.request.urlopen(req, timeout=15)
event_id = json.loads(res.read().decode()).get('event_id')
print('EVENT_ID:', event_id)

poll_url = f'https://yisol-idm-vton.hf.space/call/tryon/{event_id}'
poll_req = urllib.request.Request(poll_url, headers={'User-Agent': 'Withmore-AI/1.0'})

with urllib.request.urlopen(poll_req, timeout=40) as stream:
    for idx in range(35):
        line = stream.readline().decode('utf-8')
        if line.startswith('event:'):
            print('EVENT:', line.strip())
        if 'file=' in line or 'complete' in line:
            print('RESULT LINE:', line[:200])
            break
"""

stdin, stdout, stderr = ssh.exec_command(f'/var/www/withmore/.venv/bin/python3 -c "{remote}"')
print("JPG TEST:\n", stdout.read().decode())
print("ERR:\n", stderr.read().decode())
ssh.close()

