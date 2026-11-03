import os
import tarfile
import paramiko

HOST = "162.35.37.77"
PORT = 22
USER = "root"
PASSWORD = "withmore2026"

print(f"Connecting to {USER}@{HOST}:{PORT}...", flush=True)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=20)
print("SSH Connection Successful!", flush=True)

tar_path = r"C:\Users\muham\OneDrive\Desktop\withmore\dist_update.tar.gz"
if os.path.exists(tar_path):
    os.remove(tar_path)

with tarfile.open(tar_path, "w:gz") as tar:
    tar.add(r"C:\Users\muham\OneDrive\Desktop\withmore\frontend\dist", arcname="dist")

sftp = client.open_sftp()
print("Uploading dist_update.tar.gz...", flush=True)
sftp.put(tar_path, "/var/www/withmore/dist_update.tar.gz")
sftp.close()

if os.path.exists(tar_path):
    os.remove(tar_path)

print("Unpacking dist on VPS...", flush=True)
cmd = """cd /var/www/withmore
rm -rf frontend/dist
tar -xzf dist_update.tar.gz -C frontend/
rm -f dist_update.tar.gz
ls -la frontend/dist
systemctl restart whitmore
systemctl status whitmore --no-pager -n 5
"""
stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("STDERR:", err)

client.close()
print("Deployment completed successfully!", flush=True)

