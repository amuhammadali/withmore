import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

sftp = ssh.open_sftp()
local_miniapp = r"frontend/src/miniapp/MiniApp.tsx"
remote_miniapp = "/var/www/withmore/frontend/src/miniapp/MiniApp.tsx"
print("Uploading MiniApp.tsx to VPS...")
sftp.put(local_miniapp, remote_miniapp)
sftp.close()
print("Uploaded successfully!")

# Run npm run build on VPS
print("Running npm run build on VPS...")
stdin, stdout, stderr = ssh.exec_command("cd /var/www/withmore/frontend && npm run build")
out = stdout.read().decode()
err = stderr.read().decode()
print("OUT:", out)
print("ERR:", err)

# Restart service
print("Restarting whitmore service...")
stdin, stdout, stderr = ssh.exec_command("systemctl restart whitmore && systemctl status whitmore --no-pager -n 5")
print(stdout.read().decode())

ssh.close()
print("Deployment of Step 1 complete!")

