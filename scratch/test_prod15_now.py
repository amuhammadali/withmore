import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import urllib.request, json

url = 'http://127.0.0.1:8000/api/shop/tryon/generate'
payload = {
    'product_id': 15,
    'human_image_url': '/uploads/tryon/tryon_c9577d3b562866de.jpeg'
}
req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    with urllib.request.urlopen(req, timeout=50) as res:
        print('HTTP STATUS:', res.status)
        print('RESPONSE:', res.read().decode())
except urllib.error.HTTPError as e:
    print('HTTP ERROR:', e.code, e.read().decode())
except Exception as e:
    print('ERROR:', e)
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("ENDPOINT TEST RESULT:\n", stdout.read().decode())
print("ERR:\n", stderr.read().decode())
ssh.close()

