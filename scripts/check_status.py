import paramiko, sys

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.248.77', username='hibug', password='mug2025', timeout=10)

cmds = [
    ("=== TODO (first 5 lines) ===", "grep -c '^\\[TASK' /home/hibug/lobster/todo.md; head -3 /home/hibug/lobster/todo.md"),
    ("=== DONE LOG ===", "cat /home/hibug/lobster/logs/done.log 2>/dev/null | cut -c1-80"),
    ("=== GIT LOG ===", "cd /home/hibug/FORGE-Bench && git log --oneline -8"),
    ("=== IMAGE COUNT ===", "find /home/hibug/FORGE-Bench/dataset/images -name '*.jpg' | wc -l"),
    ("=== IMAGE LIST ===", "find /home/hibug/FORGE-Bench/dataset/images -name '*.jpg' | sort"),
    ("=== IMAGE SIZES ===", "python3 -c \"from PIL import Image; import glob; imgs=glob.glob('/home/hibug/FORGE-Bench/dataset/images/**/*.jpg',recursive=True); [print(f'{i.split(\\\"/\\\")[-1]}: {Image.open(i).size}') for i in sorted(imgs)[:25]]\""),
]

for label, cmd in cmds:
    print(f"\n{label}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(out.encode('gbk', errors='replace'))
    sys.stdout.flush()

client.close()
