import paramiko, sys, time

API_KEY = "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"

# Fixed loop.sh with correct PATH
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
log "Lobster Agent started | claude: $(which claude 2>/dev/null || echo NOT_FOUND) | workdir: $WORKDIR"

cd "$WORKDIR"

while true; do
    TASK=$(grep -m1 "^[^#[:space:]]" "$LOBSTER/todo.md" 2>/dev/null || true)
    if [ -n "$TASK" ]; then
        log "START: ${{TASK:0:80}}..."
        LOGFILE="$LOBSTER/logs/$(date +%Y%m%d).log"
        echo "=== $(date) ===" >> "$LOGFILE"
        claude --dangerously-skip-permissions -p "$TASK" 2>&1 | tee -a "$LOGFILE"
        EXIT_CODE=${{PIPESTATUS[0]}}
        log "DONE (exit=$EXIT_CODE): ${{TASK:0:80}}..."
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ${{TASK:0:120}}" >> "$LOBSTER/logs/done.log"
        ESCAPED=$(printf '%s' "$TASK" | sed 's/[^^]/[&]/g;s/\\^/\\\\^/g')
        grep -v "^$TASK$" "$LOBSTER/todo.md" > "$LOBSTER/todo.tmp" && mv "$LOBSTER/todo.tmp" "$LOBSTER/todo.md"
    fi
    sleep 30
done
"""

# Updated TODO with user's image preferences and TASK-1 restored
TODO = """\
# FORGE-Bench 龙虾任务列表
# ============================================================

[TASK-1: IMAGE AUDIT & SOURCING] Working directory: /home/hibug/FORGE-Bench. IMPORTANT IMAGE POLICY: (A) Minimize military subjects - for aerospace domain use commercial/civil aircraft (airliners, cargo planes, helicopters, space vehicles) as primary subjects; only keep 1-2 military aircraft if already committed. (B) For vehicle domain: keep max 1-2 tank images (Leopard 2 is acceptable to keep), replace other military vehicles with civilian/industrial vehicles (cargo ships, mining trucks, construction cranes, excavators, container vessels, heavy haul trucks). (C) Robotics, manufacturing, energy, microelectronics domains: no restriction, focus on real industrial equipment. Step 1 - Audit: run python3 to load dataset/annotations/samples.json, check which image_path files do not exist under dataset/images/, print list of (task_id, domain, image_path, prompt excerpt). Step 2 - Also check existing images: list all files in dataset/images/ subdirectories, identify any that are military vehicles that should be replaced per policy above. Step 3 - For each missing or to-be-replaced image: search Wikimedia Commons API: curl 'https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=TERMS&srnamespace=6&srlimit=5&format=json' with appropriate search terms (e.g. "Boeing 747 commercial airliner side view", "offshore oil platform North Sea", "PCB printed circuit board closeup", "industrial robot arm factory", "mining haul truck Caterpillar"). Download best real photograph (not illustration). Image requirements: JPG format, minimum 1280x720 pixels, 16:9 preferred, subject clearly visible, background matches prompt description, no watermarks, CC-licensed. Download to correct dataset/images/{domain}/ path per samples.json image_path field. Step 4 - If you need to update a sample's prompt to match a new non-military image (e.g. change "Sukhoi Su-27" to "Boeing 747-400"), update both the text field and image_path in samples.json consistently. Keep vfa_target and questions scientifically valid for the new subject. Step 5 - Verify images with PIL, confirm dimensions. Step 6 - Commit: git -c http.proxy=http://127.0.0.1:7897 add -A && git -c http.proxy=http://127.0.0.1:7897 commit -m 'dataset: source civilian-focused reference images, replace military vehicles per policy'. Goal: at least 15 new/replaced images, all domains covered.

[TASK-2: SCORING REFORM] Working directory: /home/hibug/FORGE-Bench. Read eval_report context: the current hailuo-2.3 eval shows IKA=94.44, PP=97.22, VF=100 which are all unrealistically high and not discriminating. Make these SPECIFIC code changes: (1) eval/geometric_integrity/surface.py - find where GI score is computed from chamfer distance, add a minimum floor: score = max(0.10, computed_score) so no sample gets GI=0 from Chamfer alone; also add condition: if vfa_value is not None and vfa_value > 0.25, add a note in the result dict 'gi_orbit_angle_caution': True since large orbits cause legitimate perspective changes that inflate Chamfer. (2) eval/geometric_integrity/kinematic.py - fix the dark-background static detection false positive: before computing mean optical flow, check if more than 40% of pixels have value <30 (dark background); if yes, compute flow only on the center 60% ROI of the frame and use threshold 0.5px instead of 0.8px for static detection. (3) eval/physical_plausibility/eval.py - read the current LMM prompt, add this calibration instruction to it: "Apply strict scientific standards. A score of 5 requires zero physically impossible elements. Score 4: minor but physically plausible approximations only. Score 3: one noticeable but not severe physics issue. Score 2: clear violation of known physical laws. Score 1: multiple severe violations. When in doubt between two scores, choose the lower one. Industrial accuracy is paramount." (4) scoring/per_sample.py or scoring/aggregate.py - find where final per-axis scores are assembled, add a minimum floor function: for IKA, TC, PP, VF axes enforce minimum score of 5.0 (on 0-100 scale) so no axis returns exactly 0; for GI enforce minimum 10.0; this prevents zero-score edge cases while maintaining scientific validity. (5) scoring/aggregate.py - add VFA binning to the output: vfa_tier = 'none' if vfa<5 else 'weak' if vfa<20 else 'moderate' if vfa<60 else 'full'. After all changes, run python3 -m py_compile eval/geometric_integrity/surface.py eval/geometric_integrity/kinematic.py eval/physical_plausibility/eval.py scoring/per_sample.py scoring/aggregate.py to check syntax. Commit: git -c http.proxy=http://127.0.0.1:7897 add -A && git -c http.proxy=http://127.0.0.1:7897 commit -m 'scoring: scientific calibration - floor scores, orbit GI caution, dark-bg fix, strict PP'.

[TASK-3: CODE AUDIT & FIXES] Working directory: /home/hibug/FORGE-Bench. Do a systematic audit of the evaluation pipeline. (1) Read every .py file in eval/ and scoring/ directories. For each file note: (a) any bare except clauses that silently swallow errors - replace with specific exception types and proper logging, (b) any TODO/FIXME/NotImplemented that represents unfinished functionality - implement it or raise NotImplementedError with a clear message, (c) any hardcoded thresholds that should be configurable - extract to a config dict at the top of the file with comments explaining the value, (d) any function that can return None unexpectedly when downstream code doesn't handle None - add explicit None checks. (2) Specifically check eval/vfa/eval.py: does it handle missing vfa_target field gracefully? Does it handle videos shorter than 8 frames? Does it handle grayscale video input? Fix any gaps. (3) Check scoring/report.py: does it produce valid JSON? Does it handle NaN/Infinity values from CV algorithms (replace with None)? Does it generate the eval_report.json format shown in the existing results/hailuo-2.3/eval_report.json? (4) Check eval/geometric_integrity/lattice.py: the SIFT inlier ratio method - does it handle the case where too few keypoints are detected (<10 keypoints)? Add a fallback. (5) After all fixes, run: python3 -c "import eval.geometric_integrity.surface, eval.geometric_integrity.kinematic, eval.geometric_integrity.lattice, eval.physical_plausibility.eval, scoring.per_sample, scoring.aggregate, scoring.report; print('All imports OK')" and fix any import errors. Commit: git -c http.proxy=http://127.0.0.1:7897 add -A && git -c http.proxy=http://127.0.0.1:7897 commit -m 'eval: systematic audit - fix bare excepts, None handling, missing vfa_target, keypoint fallback'.

[TASK-4: EXPAND TEST SAMPLES] Working directory: /home/hibug/FORGE-Bench. Expand dataset/annotations/samples.json with new samples. IMAGE POLICY: prefer civilian/industrial subjects (commercial aircraft, cargo vessels, mining equipment, industrial robots, energy infrastructure) over military. Add exactly 10 new samples covering underrepresented motion types: 2 tilt/rise camera motion samples (commercial airliner takeoff, offshore wind farm rise shot), 2 manufacturing kinematic samples (conveyor belt, industrial robotic arm assembly line), 2 dolly-zoom samples (PCB component zoom-in, vehicle engine bay dolly-in), 2 vehicle domain samples (cargo container ship, Caterpillar mining haul truck), 1 energy kinematic sample (wind turbine blade rotation from static), 1 robotics surface sample (industrial robotic arm structure 45-deg orbit). For each sample: task_id follows pattern {domain_abbrev}_{topology}_{NNN} incrementing from existing max, failure_target describes a specific scientifically plausible I2V failure mode, vfa_target follows naming convention (tilt_up_Xdeg, dolly_in_Xx, rise_vertical_Xdeg, orbit_cw_Xdeg), questions array has 3-4 IKA questions testing geometric/physical constraints, image_path set to dataset/images/{domain}/{task_id}.jpg, reverse=false, extra_frame=1. After adding 10 samples, create spec files at dataset/images/{domain}/{task_id}_NEEDS_IMAGE.txt describing exact photograph needed. Verify with python3 -c "import json; s=json.load(open('dataset/annotations/samples.json')); print(f'Total: {len(s)} samples')" . Commit: git -c http.proxy=http://127.0.0.1:7897 add -A && git -c http.proxy=http://127.0.0.1:7897 commit -m 'dataset: add 10 new civilian-focused samples covering tilt/rise/dolly/vehicle diversity'.
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

sftp = client.open_sftp()
# Write fixed loop.sh
with sftp.open('/home/hibug/lobster/loop.sh', 'w') as f:
    f.write(LOOP_SH)
# Write updated todo.md
with sftp.open('/home/hibug/lobster/todo.md', 'w') as f:
    f.write(TODO)
sftp.close()
print("Files written. Restarting agent...")

stream(client, "chmod +x /home/hibug/lobster/loop.sh && systemctl --user restart lobster && sleep 3 && tail -5 /home/hibug/lobster/logs/agent.log")
print("\nDone. Agent restarted with fixed PATH and updated tasks.")
client.close()
