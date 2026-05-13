import paramiko, time

TOKEN = ""  # set via environment variable: export GITHUB_TOKEN=...
REMOTE_URL = f"https://am-ns:{TOKEN}@github.com/am-ns/FORGE-Bench.git"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.248.77', username='hibug', password='mug2025', timeout=10)

def run(cmd, timeout=20):
    chan = client.get_transport().open_session()
    chan.exec_command(cmd)
    out = []
    deadline = time.time() + timeout
    while time.time() < deadline:
        if chan.recv_ready(): out.append(chan.recv(8192).decode('utf-8', errors='replace'))
        if chan.recv_stderr_ready(): out.append(chan.recv_stderr(4096).decode('utf-8', errors='replace'))
        if chan.exit_status_ready():
            time.sleep(0.1)
            while chan.recv_ready(): out.append(chan.recv(8192).decode('utf-8', errors='replace'))
            break
        time.sleep(0.05)
    return ''.join(out)

# Configure git on server
print(run('cd ~/FORGE-Bench && git config user.email "woyinyuebofangqi@gmail.com"'))
print(run('cd ~/FORGE-Bench && git config user.name "AI_Explorer"'))
print(run(f'cd ~/FORGE-Bench && git remote set-url origin "{REMOTE_URL}"'))
print(run('cd ~/FORGE-Bench && git remote -v'))

# Test fetch
print("Testing fetch...")
print(run('cd ~/FORGE-Bench && git fetch origin 2>&1 | head -5', timeout=30))

# Add final task to queue: restructure taxonomy then push
TASK_RESTRUCTURE = (
    "[TASK-REORG: Restructure domain names to 10-domain ISIC taxonomy] "
    "Working directory: /home/hibug/FORGE-Bench. "
    "Load dataset/annotations/samples.json. Apply these domain renames IN-PLACE to all samples: "
    "(1) domain=='microelectronics' -> domain='electronics', update image_path replace /microelectronics/ with /electronics/; "
    "(2) For domain=='energy': check prompt/image_path — if contains wind/solar/tidal/geothermal/renewable -> domain='energy_renewable', image_path /energy_renewable/; "
    "if contains oil/gas/platform/drilling/LNG/refinery/FPSO/offshore -> domain='oil_gas', image_path /oil_gas/; "
    "else (power plant/turbine/nuclear/hydro/boiler/grid) -> domain='energy_power', image_path /energy_power/; "
    "(3) domain=='robotics' -> domain='manufacturing', image_path /robotics/ -> /manufacturing/; "
    "(4) domain=='vehicle': for each sample inspect image_path filename — "
    "if contains t90/m1a1/m2_bradley/leopard2/abrams/bradley -> REMOVE this sample entirely (military); "
    "if contains truck/haul/dump/mining_truck -> domain='mining', image_path /mining/; "
    "else (loader/bulldozer/crane/excavator/paver/dozer) -> domain='construction', image_path /construction/. "
    "After JSON edits, physically move image files to match new paths: "
    "mkdir -p dataset/images/{electronics,energy_renewable,energy_power,oil_gas}; "
    "mv files from old paths to new paths (use os.rename or shutil.move in a helper script). "
    "Verify: 10 domains exist (aerospace, energy_power, energy_renewable, oil_gas, chemical, mining, construction, manufacturing, electronics, maritime), no military samples remain. "
    "Print domain distribution. Run python3 dataset/validate.py. "
    "git add -A && git commit -m 'dataset: restructure to 10-domain ISIC taxonomy, remove military samples, rename image dirs'"
)

TASK_PUSH = (
    "[TASK-SYNC: Push all commits to GitHub origin] "
    "Working directory: /home/hibug/FORGE-Bench. "
    "Run: git fetch origin. "
    "Then: git rebase origin/master (if needed to handle any divergence). "
    "Then: git push origin master. "
    "Report the final git log --oneline -8 and confirm push succeeded."
)

sftp = client.open_sftp()

# Read current todo.md
with sftp.open('/home/hibug/lobster/todo.md', 'r') as f:
    current = f.read().decode('utf-8')

# Append new tasks AFTER existing ones
new_content = current.rstrip() + "\n" + TASK_RESTRUCTURE + "\n" + TASK_PUSH + "\n"

with sftp.open('/home/hibug/lobster/todo.md', 'w') as f:
    f.write(new_content)
sftp.close()

count = run('grep -c "^\\[TASK" ~/lobster/todo.md 2>/dev/null || echo 0')
print(f"\nTotal tasks in queue: {count.strip()}")
print("\nLast 2 log lines:")
print(run('tail -2 ~/lobster/logs/agent.log'))
client.close()
print("DONE")
