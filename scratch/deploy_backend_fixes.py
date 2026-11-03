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

sftp = client.open_sftp()
print("Uploading fixed admin_ops.py and admin_crm.py...", flush=True)
sftp.put(r"C:\Users\muham\OneDrive\Desktop\withmore\backend\app\routers\admin_ops.py", "/var/www/withmore/backend/app/routers/admin_ops.py")
sftp.put(r"C:\Users\muham\OneDrive\Desktop\withmore\backend\app\routers\admin_crm.py", "/var/www/withmore/backend/app/routers/admin_crm.py")
sftp.close()

print("Restarting whitmore service...", flush=True)
stdin, stdout, stderr = client.exec_command("systemctl restart whitmore && systemctl status whitmore --no-pager -n 5")
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print("STDERR:", err)

client.close()
print("Backend fixes deployed successfully!", flush=True)

