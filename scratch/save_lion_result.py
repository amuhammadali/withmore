import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import urllib.request

src_url = 'https://yisol-idm-vton.hf.space/file=/tmp/gradio/7902b403177e87f04568a390853bdb69dda54c33/image.png'
dest = '/var/www/withmore/uploads/tryon/lion_koylek_result.png'
req = urllib.request.Request(src_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as res:
    data = res.read()
    with open(dest, 'wb') as fp:
        fp.write(data)
    print('Saved successfully! Size:', len(data))
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("SAVE OUT:\n", stdout.read().decode())
print("ERR:\n", stderr.read().decode())
ssh.close()

