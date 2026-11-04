import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote_script = """
import urllib.request
import json

api_key = 'fal_sk_7d4c5e61648e4a44b008e6e43277ab44:2293c94fad72cbea160fd37f4bea5c89'

# Test 1: Check IDM-VTON model availability on fal.ai
# Usually fal-ai/idm-vton endpoint is https://fal.run/fal-ai/idm-vton
req = urllib.request.Request(
    'https://fal.run/fal-ai/idm-vton',
    headers={
        'Authorization': f'Key {api_key}',
        'Content-Type': 'application/json'
    },
    data=b'{}'
)

try:
    with urllib.request.urlopen(req) as res:
        print('Status:', res.status)
        print(res.read().decode()[:200])
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code, e.read().decode())
except Exception as e:
    print('Error:', e)
"""

stdin, stdout, stderr = ssh.exec_command(f"python3 -c \"{remote_script}\"")
print("OUT:", stdout.read().decode())
print("ERR:", stderr.read().decode())
ssh.close()

