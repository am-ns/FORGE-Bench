import paramiko, sys, time

API_KEY = "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"

# Fixed loop.sh: use Python for task removal to avoid shell regex issues
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

WORKDIR="/home/hibug/FORGE-Bench"
LOBSTER="/home/hibug/lobster"
mkdir -p "$LOBSTER/logs"

log() {{ echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOBSTER/logs/agent.log"; }}
log "Lobster started | claude=$(which claude) | node=$(node -v)"

cd "$WORKDIR"

while true; do
    # Use Python to safely read first non-comment task (avoids shell regex issues)
    TASK=$(python3 - <<'PYEOF'
import sys
try:
    lines = open("/home/hibug/lobster/todo.md").readlines()
    for line in lines:
        s = line.rstrip("\\n")
        if s and not s.startswith("#") and not s.startswith(" "):
            print(s)
            sys.exit(0)
except:
    pass
PYEOF
)

    if [ -n "$TASK" ]; then
        log "START: ${{TASK:0:100}}..."
        LOGFILE="$LOBSTER/logs/$(date +%Y%m%d).log"
        echo "" >> "$LOGFILE"
        echo "=== $(date) ===" >> "$LOGFILE"
        claude --dangerously-skip-permissions -p "$TASK" 2>&1 | tee -a "$LOGFILE"
        EXIT=${{PIPESTATUS[0]}}
        log "DONE exit=$EXIT: ${{TASK:0:100}}..."
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] exit=$EXIT ${{TASK:0:120}}" >> "$LOBSTER/logs/done.log"

        # Use Python to remove the completed task line (safe, no regex)
        python3 /home/hibug/lobster/remove_task.py "$TASK"
    fi
    sleep 30
done
"""

# Clean todo.md: only keep TASK-2, 3, 4 (TASK-1 already done)
TODO = """\
# FORGE-Bench 龙虾任务列表
# TASK-1 (image sourcing) completed. Continuing with remaining tasks.
# ============================================================

[TASK-2: SCORING REFORM] Working directory: /home/hibug/FORGE-Bench. The current hailuo-2.3 eval shows IKA=94.44, PP=97.22, VF=100 which are unrealistically high. Make these SPECIFIC changes: (1) eval/geometric_integrity/surface.py - find where chamfer distance score is computed, add floor: result_score = max(0.10, raw_score); also add key 'gi_orbit_angle_caution': True to result dict when the vfa value passed in (if any) exceeds 0.25, since large orbits cause legitimate perspective changes that inflate Chamfer Distance. (2) eval/geometric_integrity/kinematic.py - fix dark-background static detection false positive: add function is_dark_background(frame, threshold=30, ratio=0.40) that checks if >40% pixels are below threshold; if dark background detected, compute optical flow only on center 60% ROI and lower static threshold to 0.5 px/frame instead of 0.8. (3) eval/physical_plausibility/eval.py - find the LMM prompt string, append this calibration text: 'CALIBRATION: Apply strict scientific standards. Score 5 = zero physically impossible elements. Score 4 = minor physically plausible approximations only. Score 3 = one noticeable but not severe physics issue. Score 2 = clear violation of known physical laws. Score 1 = multiple severe violations. When uncertain between scores, choose the lower one. Industrial accuracy is paramount.' (4) scoring/aggregate.py - after computing axis means, add floor enforcement: for axis in [ika, tc, pp, vf]: score = max(5.0, score); for gi: score = max(10.0, score). Also add vfa_tier field: 'none' if vfa<5 else 'weak' if vfa<20 else 'moderate' if vfa<60 else 'full'. (5) Run python3 -m py_compile on all modified files to verify no syntax errors. Then commit: git -c http.proxy=http://127.0.0.1:7897 add -A && git -c http.proxy=http://127.0.0.1:7897 commit -m 'scoring: scientific calibration - floor scores, orbit GI caution, dark-bg kinematic fix, strict PP prompt'.

[TASK-3: CODE AUDIT] Working directory: /home/hibug/FORGE-Bench. Systematically audit eval/ and scoring/ Python files. For each .py file: (a) replace bare except clauses with specific exception types plus logging to stderr, (b) implement or raise NotImplementedError for any TODO/FIXME/pass placeholders, (c) extract hardcoded numeric thresholds into a CONFIG dict at top of file with explanatory comments, (d) add None-safety checks wherever a function may return None but callers do not check. Specific fixes required: eval/vfa/eval.py must handle: missing vfa_target field (default to None gracefully), video shorter than 8 frames (compute on available frames), grayscale video (convert to BGR before optical flow). scoring/report.py must: sanitize float values by replacing math.nan and math.inf with None before json.dumps. eval/geometric_integrity/lattice.py: if fewer than 10 SIFT keypoints detected, return a fallback score of 0.30 with a note field 'insufficient_keypoints': True instead of crashing. After fixes run: python3 -c "import eval.geometric_integrity.surface, eval.geometric_integrity.kinematic, eval.geometric_integrity.lattice, eval.physical_plausibility.eval, scoring.per_sample, scoring.aggregate, scoring.report; print('All imports OK')" and fix any errors. Commit: git -c http.proxy=http://127.0.0.1:7897 add -A && git -c http.proxy=http://127.0.0.1:7897 commit -m 'eval: audit - fix bare excepts, None safety, vfa edge cases, lattice keypoint fallback, nan sanitization'.

[TASK-4: EXPAND SAMPLES + VERIFY IMAGES] Working directory: /home/hibug/FORGE-Bench. Do two things: PART A - Image verification: load dataset/annotations/samples.json, for each sample open its image_path with PIL, print (task_id, image size, image mode, dominant color check). Flag any image where: the entire image is a single solid color (placeholder), or width<1280, or height<720. For flagged images, attempt to re-download from a different source: try searching https://www.pexels.com/api/ or https://pixabay.com/api/ for the subject keyword, or use wget with a direct Wikimedia Commons URL for the specific subject (e.g. for PCB: https://commons.wikimedia.org/wiki/File:PCB_...). PART B - Add 8 new samples to samples.json covering: 2 tilt/rise samples (Boeing 747 nose-up climb tilt shot, offshore wind farm vertical rise), 2 manufacturing kinematic (conveyor belt side view kinematic, assembly line robotic arm kinematic), 2 dolly samples (PCB component dolly-in zoom, heavy truck engine bay dolly-in), 1 energy kinematic (wind turbine spinning blades), 1 robotics surface (FANUC robotic arm 45-degree orbit). Each new sample must have: task_id following existing pattern, domain/topology_type matching subject, failure_target describing specific plausible I2V failure, vfa_target using correct naming convention, 3-4 scientifically grounded IKA questions, image_path=dataset/images/{domain}/{task_id}.jpg, reverse=false, extra_frame=1. Create _NEEDS_IMAGE.txt spec files for new samples. Run python3 -c "import json; s=json.load(open('dataset/annotations/samples.json')); print(len(s), 'samples')" to verify count. Commit: git -c http.proxy=http://127.0.0.1:7897 add -A && git -c http.proxy=http://127.0.0.1:7897 commit -m 'dataset: verify images + add 8 new samples (tilt/dolly/kinematic coverage)'.
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

# Stop agent first
stream(client, "systemctl --user stop lobster 2>&1; sleep 1; tmux kill-session -t lobster 2>/dev/null; echo stopped")

sftp = client.open_sftp()
with sftp.open('/home/hibug/lobster/loop.sh', 'w') as f:
    f.write(LOOP_SH)
with sftp.open('/home/hibug/lobster/todo.md', 'w') as f:
    f.write(TODO)
sftp.close()
print("Fixed loop.sh and reset todo.md (3 tasks: TASK-2, 3, 4-merged)")

stream(client, "chmod +x /home/hibug/lobster/loop.sh && systemctl --user start lobster && sleep 3 && tail -3 /home/hibug/lobster/logs/agent.log")
client.close()
