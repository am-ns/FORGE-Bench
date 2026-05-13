import paramiko, time

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.248.77', username='hibug', password='mug2025', timeout=15)

cmd = """
echo "=== kill old modelscope process ==="
kill 454795 2>/dev/null && echo "killed 454795" || echo "already gone"
sleep 2

echo "=== remaining processes ==="
ps aux | grep -E "python.*snapshot|hf_final" | grep -v grep | awk '{print $1,$2,$3,$11}' | head -5

echo
echo "=== log (last 5 lines) ==="
tail -5 /data_sdc/setup_wan.log

echo
echo "=== data_sdc model files ==="
find /data_sdc/models/Wan2.2-I2V-A14B -name "*.safetensors*" 2>/dev/null | head -10
du -sh /data_sdc/models/Wan2.2-I2V-A14B/

echo
echo "=== disk ==="
df -h / /data_sdc | tail -2
"""

_, out, _ = c.exec_command(cmd, timeout=25)
print(out.read().decode())
c.close()
