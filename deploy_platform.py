import paramiko
import sys

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect("162.35.37.77", port=22, username="root", password="withmore2026", timeout=15)
    print("Connected to VPS")
except Exception as e:
    print(f"Failed to connect: {e}")
    sys.exit(1)

def run(cmd):
    print(f"\n>>> Running: {cmd}", flush=True)
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    print("STDOUT:\n", out)
    if err:
        print("STDERR:\n", err)

run("cd /var/www/withmore && git fetch origin main && git reset --hard origin/main")
run("cd /var/www/withmore && npm run build --prefix frontend")
run("systemctl restart whitmore && systemctl status whitmore --no-pager")

client.close()
print("Platform deployment completed successfully!")
