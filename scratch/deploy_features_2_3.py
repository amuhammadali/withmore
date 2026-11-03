import os
import sys
import time
import tarfile
import paramiko

HOST = "162.35.37.77"
PORT = 22
USER = "root"
PASSWORD = "withmore2026"

print(f"Connecting to {USER}@{HOST}:{PORT}...", flush=True)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=15)
print("SSH Connection Successful!", flush=True)

def run(cmd, timeout=30):
    print(f"\n>>> Running: {cmd}", flush=True)
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    while not stdout.channel.exit_status_ready():
        line = stdout.readline()
        if line:
            print(line, end="", flush=True)
        time.sleep(0.05)
    for line in stdout:
        print(line, end="", flush=True)
    err = stderr.read().decode("utf-8", errors="replace")
    status = stdout.channel.recv_exit_status()
    if err and status != 0:
        print(f"STDERR: {err}", flush=True)
    return status

sftp = client.open_sftp()

# 1. Upload updated backend files
print("\n>>> Uploading backend routers...", flush=True)
sftp.put(r"C:\Users\muham\OneDrive\Desktop\withmore\backend\app\routers\admin_crm.py", "/var/www/withmore/backend/app/routers/admin_crm.py")
sftp.put(r"C:\Users\muham\OneDrive\Desktop\withmore\backend\app\routers\admin_ops.py", "/var/www/withmore/backend/app/routers/admin_ops.py")
print("Backend routers uploaded successfully!", flush=True)

# 2. Pack and upload frontend/dist
print("\n>>> Packing and uploading frontend/dist...", flush=True)
tar_path = r"C:\Users\muham\OneDrive\Desktop\withmore\dist_bundle.tar.gz"
if os.path.exists(tar_path):
    os.remove(tar_path)

with tarfile.open(tar_path, "w:gz") as tar:
    tar.add(r"C:\Users\muham\OneDrive\Desktop\withmore\frontend\dist", arcname="dist")

sftp.put(tar_path, "/var/www/withmore/dist_bundle.tar.gz")
sftp.close()
if os.path.exists(tar_path):
    os.remove(tar_path)

# 3. Unpack dist and restart service
run("""cd /var/www/withmore
rm -rf frontend/dist
tar -xzf dist_bundle.tar.gz -C frontend/
rm -f dist_bundle.tar.gz
ls -la frontend/dist
""")

run("systemctl restart whitmore && systemctl status whitmore --no-pager -n 7")

client.close()
print("\n🎉 Features 2 & 3 successfully deployed to VPS!", flush=True)

