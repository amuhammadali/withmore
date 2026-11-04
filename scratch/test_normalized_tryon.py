import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
from PIL import Image, ImageOps
import urllib.request, json

# 1. Open and fix EXIF orientation, resize to 768x1024 standard portrait
raw = Image.open('/var/www/withmore/uploads/tryon/tryon_c9577d3b562866de.jpeg')
fixed = ImageOps.exif_transpose(raw)
fixed.thumbnail((768, 1024), Image.Resampling.LANCZOS)
fixed.convert('RGB').save('/var/www/withmore/uploads/tryon/norm_human.jpg', 'JPEG', quality=90)
print('Normalized human size:', fixed.size)

# 2. Resize garment to 768x1024
garm = Image.open('/var/www/withmore/uploads/tryon/garm_15.jpg')
garm_fixed = ImageOps.exif_transpose(garm)
garm_fixed.thumbnail((768, 1024), Image.Resampling.LANCZOS)
garm_fixed.convert('RGB').save('/var/www/withmore/uploads/tryon/norm_garm.jpg', 'JPEG', quality=90)
print('Normalized garm size:', garm_fixed.size)

# 3. Call HF
human_url = 'https://withmore.uz/uploads/tryon/norm_human.jpg'
garment_url = 'https://withmore.uz/uploads/tryon/norm_garm.jpg'

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
req = urllib.request.Request(call_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
res = urllib.request.urlopen(req, timeout=15)
event_id = json.loads(res.read().decode()).get('event_id')
print('EVENT_ID:', event_id)

poll_url = f'https://yisol-idm-vton.hf.space/call/tryon/{event_id}'
poll_req = urllib.request.Request(poll_url, headers={'User-Agent': 'Mozilla/5.0'})

with urllib.request.urlopen(poll_req, timeout=40) as stream:
    for idx in range(35):
        line = stream.readline().decode('utf-8')
        if line.startswith('event:'):
            print('EVENT:', line.strip())
        if 'file=' in line or 'complete' in line:
            print('SUCCESS LINE:', line[:200])
            break
"""

stdin, stdout, stderr = ssh.exec_command(f'/var/www/withmore/.venv/bin/python3 -c "{remote}"')
print("NORMALIZED TEST:\n", stdout.read().decode())
print("ERR:\n", stderr.read().decode())
ssh.close()

