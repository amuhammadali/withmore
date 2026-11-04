import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

def run_cmd(cmd):
    print(f"\n>>> Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print("OUT:", out)
    if err:
        print("ERR:", err)
    return stdout.channel.recv_exit_status()

# 1. Pull on VPS
run_cmd("cd /var/www/withmore && git reset --hard && git pull origin main")

# 2. Build Frontend on VPS
run_cmd("cd /var/www/withmore/frontend && npm run build")

# 3. Ensure uploads/tryon folder exists on VPS
run_cmd("mkdir -p /var/www/withmore/backend/uploads/tryon")

# 4. Restart whitmore service
run_cmd("systemctl restart whitmore && systemctl status whitmore --no-pager -n 4")

ssh.close()
print("\nDeployment of AI Try-On completed!")
