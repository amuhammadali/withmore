import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
from gradio_client import Client, handle_file

print('Connecting to Nymbo/Virtual-Try-On...')
client = Client('Nymbo/Virtual-Try-On')

human_path = '/var/www/withmore/uploads/tryon/tryon_c9577d3b562866de.jpeg'
garm_path = '/var/www/withmore/uploads/tryon/garm_15.jpg'

result = client.predict(
    dict={'background': handle_file(human_path), 'layers': [], 'composite': None},
    garm_img=handle_file(garm_path),
    garment_des='A luxury shirt',
    is_checked=True,
    is_checked_crop=False,
    denoise_steps=20,
    seed=42,
    api_name='/tryon'
)

print('GRADIO SUCCESS RESULT:', result)
"""

sftp = ssh.open_sftp()
with sftp.file('/tmp/test_gc.py', 'w') as f:
    f.write(remote)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/var/www/withmore/.venv/bin/python3 /tmp/test_gc.py')
print("OUT:\n", stdout.read().decode())
print("ERR:\n", stderr.read().decode())
ssh.close()

