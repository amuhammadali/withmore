import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import sqlite3, urllib.request, json, traceback

# Let's see product 15 image
conn = sqlite3.connect('/var/www/withmore/whitmore.db')
cur = conn.cursor()
cur.execute('SELECT path FROM product_images WHERE product_id = 15')
rows = cur.fetchall()
print('Product 15 images:', rows)

garment_url = f'https://withmore.uz/uploads/{rows[0][0]}' if rows else ''
human_url = 'https://withmore.uz/uploads/tryon/tryon_c9577d3b562866de.jpeg'
print('garment_url:', garment_url)
print('human_url:', human_url)

# Test HF call directly
try:
    payload = {
        'data': [
            {'background': {'path': human_url, 'url': human_url}, 'layers': [], 'composite': None},
            {'path': garment_url, 'url': garment_url},
            'A tailored shirt',
            True,
            False,
            20,
            42
        ]
    }
    call_url = 'https://yisol-idm-vton.hf.space/call/tryon'
    req = urllib.request.Request(call_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json', 'User-Agent': 'Withmore-AI/1.0'})
    with urllib.request.urlopen(req, timeout=15) as res:
        res_data = json.loads(res.read().decode())
        event_id = res_data.get('event_id')
        print('event_id:', event_id)
        
    poll_url = f'https://yisol-idm-vton.hf.space/call/tryon/{event_id}'
    poll_req = urllib.request.Request(poll_url, headers={'User-Agent': 'Withmore-AI/1.0'})
    with urllib.request.urlopen(poll_req, timeout=30) as stream:
        for _ in range(30):
            line = stream.readline().decode('utf-8')
            if line.startswith('data:'):
                raw = line[5:].strip()
                if raw and raw != 'null':
                    print('SSE DATA:', raw[:200])
                    break
except Exception as e:
    print('EXCEPTION CAUGHT:')
    traceback.print_exc()
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("DEBUG RESULT:\n", stdout.read().decode())
print("ERR:\n", stderr.read().decode())
ssh.close()

