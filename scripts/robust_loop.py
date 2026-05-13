import paramiko, sys, time

API_KEY = "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"

# Robust remove_task.py - uses index-based removal as fallback
REMOVE_TASK_PY = '''\
#!/usr/bin/env python3
"""Remove a specific task line from todo.md. Falls back to removing first non-comment line."""
import sys, os

TODO = "/home/hibug/lobster/todo.md"
task = sys.argv[1] if len(sys.argv) > 1 else ""

try:
    lines = open(TODO).readlines()
    # Primary: exact string match removal
    new_lines = [l for l in lines if l.rstrip("\\n") != task]
    if len(new_lines) == len(lines):
        # Fallback: task not found by exact match, remove first non-comment line
        new_lines = []
        removed = False
        for l in lines:
            stripped = l.rstrip("\\n")
            if not removed and stripped and not stripped.startswith("#") and not stripped.startswith(" "):
                removed = True  # skip this line (remove it)
                continue
            new_lines.append(l)
    open(TODO, "w").writelines(new_lines)
    sys.exit(0)
except Exception as e:
    print(f"remove_task error: {e}", file=sys.stderr)
    sys.exit(1)
'''

# Robust loop.sh with:
# 1. Rate-limit detection -> sleep and retry (don't remove task)
# 2. Max 3 retries per task -> move to failed.log after 3 failures
# 3. 2-hour timeout per task -> no infinite hang
# 4. Double-safety task removal (Python + shell fallback)
LOOP_SH = f"""#!/bin/bash
export PATH="/home/hibug/.local/node/bin:$PATH"
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
export ANTHROPIC_API_KEY="{API_KEY}"
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897
export HTTP_PROXY=http://127.0.0.1:7897
export HTTPS_PROXY=http://127.0.0.1:7897
export NO_PROXY=localhost,127.0.0.1

LOBSTER="/home/hibug/lobster"
WORKDIR="/home/hibug/FORGE-Bench"
RETRY_FILE="$LOBSTER/retry_count.tmp"
mkdir -p "$LOBSTER/logs"

log() {{ echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOBSTER/logs/agent.log"; }}

log "=== Lobster started | claude=$(which claude 2>/dev/null || echo MISSING) | node=$(node -v 2>/dev/null) ==="

cd "$WORKDIR"

while true; do
    # Read first non-comment, non-empty task using Python (safe, no regex)
    TASK=$(python3 -c "
import sys
try:
    for line in open('$LOBSTER/todo.md'):
        s = line.rstrip()
        if s and not s.startswith('#') and not s.startswith(' '):
            print(s); sys.exit(0)
except: pass
" 2>/dev/null)

    if [ -z "$TASK" ]; then
        # No tasks - idle
        sleep 30
        continue
    fi

    # Read retry count for this task
    TASK_HASH=$(echo "$TASK" | md5sum | cut -c1-8)
    RETRIES=$(cat "$RETRY_FILE.$TASK_HASH" 2>/dev/null || echo 0)

    if [ "$RETRIES" -ge 3 ]; then
        log "GIVE_UP after 3 retries: ${{TASK:0:80}}..."
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] FAILED(3x): ${{TASK:0:120}}" >> "$LOBSTER/logs/failed.log"
        python3 "$LOBSTER/remove_task.py" "$TASK" || python3 -c "
lines=open('$LOBSTER/todo.md').readlines()
new=[l for i,l in enumerate(lines) if not (l.strip() and not l.startswith('#') and i==next((j for j,x in enumerate(lines) if x.strip() and not x.startswith('#')),None))]
open('$LOBSTER/todo.md','w').writelines(new)
"
        rm -f "$RETRY_FILE.$TASK_HASH"
        continue
    fi

    log "START (attempt $((RETRIES+1))/3): ${{TASK:0:80}}..."
    LOGFILE="$LOBSTER/logs/$(date +%Y%m%d).log"
    echo "" >> "$LOGFILE"
    echo "=== $(date) | attempt $((RETRIES+1)) ===" >> "$LOGFILE"

    # Run claude with 2-hour timeout, capture output for error detection
    TMPOUT=$(mktemp)
    timeout 7200 claude --dangerously-skip-permissions -p "$TASK" 2>&1 | tee -a "$LOGFILE" | tee "$TMPOUT"
    EXIT=${{PIPESTATUS[0]}}

    # Check for rate limit / token exhaustion signals
    if grep -qiE "rate.?limit|429|overloaded|too.many.request|usage.limit|credit|quota" "$TMPOUT" 2>/dev/null; then
        log "RATE_LIMIT detected (exit=$EXIT) - sleeping 5 min then retrying same task"
        echo $((RETRIES+1)) > "$RETRY_FILE.$TASK_HASH"
        rm -f "$TMPOUT"
        sleep 300
        continue
    fi

    # Check for timeout (exit code 124 from `timeout`)
    if [ "$EXIT" -eq 124 ]; then
        log "TIMEOUT (2h) on task, counting as retry"
        echo $((RETRIES+1)) > "$RETRY_FILE.$TASK_HASH"
        rm -f "$TMPOUT"
        sleep 60
        continue
    fi

    # Task finished (success or non-rate-limit error) - remove from queue
    rm -f "$TMPOUT"
    log "DONE exit=$EXIT: ${{TASK:0:80}}..."
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] exit=$EXIT ${{TASK:0:120}}" >> "$LOBSTER/logs/done.log"

    # Remove task - Python primary, shell fallback
    python3 "$LOBSTER/remove_task.py" "$TASK"
    if grep -qF "${{TASK:0:40}}" "$LOBSTER/todo.md" 2>/dev/null; then
        # Still there - force remove first non-comment line
        log "WARNING: remove_task.py may have failed, using fallback removal"
        python3 -c "
lines=open('$LOBSTER/todo.md').readlines()
new=[]; skip=False
for l in lines:
    if not skip and l.strip() and not l.strip().startswith('#'):
        skip=True; continue
    new.append(l)
open('$LOBSTER/todo.md','w').writelines(new)
"
    fi
    rm -f "$RETRY_FILE.$TASK_HASH"
    sleep 5
done
"""

def stream(client, cmd, timeout=30):
    chan = client.get_transport().open_session()
    chan.exec_command(cmd)
    chan.settimeout(timeout)
    while True:
        if chan.recv_ready():
            d = chan.recv(4096).decode("utf-8", errors="replace")
            sys.stdout.buffer.write(d.encode("gbk", errors="replace"))
            sys.stdout.flush()
        if chan.exit_status_ready():
            time.sleep(0.2)
            while chan.recv_ready():
                d = chan.recv(4096).decode("utf-8", errors="replace")
                sys.stdout.buffer.write(d.encode("gbk", errors="replace"))
                sys.stdout.flush()
            break
        time.sleep(0.05)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.248.77', username='hibug', password='mug2025', timeout=10)

# Stop agent, write new files, restart
stream(client, "systemctl --user stop lobster; sleep 1; echo stopped")

sftp = client.open_sftp()
with sftp.open('/home/hibug/lobster/loop.sh', 'w') as f:
    f.write(LOOP_SH)
with sftp.open('/home/hibug/lobster/remove_task.py', 'w') as f:
    f.write(REMOVE_TASK_PY)
sftp.close()
print("Files written.")

stream(client, "chmod +x /home/hibug/lobster/loop.sh /home/hibug/lobster/remove_task.py && systemctl --user start lobster && sleep 3 && tail -4 /home/hibug/lobster/logs/agent.log")
client.close()
print("\nDone. Robust loop deployed.")
