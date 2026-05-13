"""
Mock full 5-axis eval on the 3 Veo videos.
GPT axes (IKA/TC/PP/VF) use placeholder scores so we can validate
the end-to-end scoring pipeline without an API key.
GI / VFA / RIF run for real.
"""
import sys, os, json, random
sys.path.insert(0, 'C:/Users/assd/S_I_Eval')
os.chdir('C:/Users/assd/S_I_Eval')

SAMPLES_FILE = 'dataset/annotations/samples.json'
VIDEO_ROOT   = 'dataset/videos/veo-3.1'
RESULT_ROOT  = 'results/veo-3.1'
MODEL_TAG    = 'veo-3.1'

with open(SAMPLES_FILE, encoding='utf-8') as f:
    all_samples = json.load(f)

TARGET = {'aero_surf_001', 'ener_lat_001', 'def_surf_001'}
samples = [s for s in all_samples if s['task_id'] in TARGET]

for s in samples:
    tid = s['task_id']
    vp  = os.path.join(VIDEO_ROOT, f'{tid}.mp4')
    s['video_path'] = vp if os.path.isfile(vp) else None

# make all result dirs
for sub in ['ika_score','ika_result','tc_result','pp_result','vf_result',
            'gi_result','vfa_result','rif_result']:
    os.makedirs(os.path.join(RESULT_ROOT, sub), exist_ok=True)

from eval.geometric_integrity import eval_geometric_integrity
from eval.vfa import eval_vfa, save_vfa_result
from eval.reference_fidelity import eval_rif
from eval.reference_fidelity.eval import save_rif_result

random.seed(42)

for s in samples:
    tid = s['task_id']
    print(f'\n{"="*50}')
    print(f'[{tid}]  video={os.path.basename(s["video_path"] or "MISSING")}')

    if not s['video_path']:
        print('  no video, skipping'); continue

    # ── Real CV axes ──────────────────────────────────────────────────────────
    gi = eval_geometric_integrity(s)
    with open(os.path.join(RESULT_ROOT, 'gi_result', f'{tid}.json'), 'w') as f:
        json.dump({'task_id': tid, **gi}, f, indent=2)
    print(f'  GI  = {gi.get("score")}')

    vfa = eval_vfa(s)
    save_vfa_result(vfa, os.path.join(RESULT_ROOT, 'vfa_result'))
    print(f'  VFA = {vfa["vfa"]}  motion={vfa["motion_detected"]}')

    rif = eval_rif(s)
    save_rif_result(rif, os.path.join(RESULT_ROOT, 'rif_result'))
    print(f'  RIF = {rif["score"]}')

    # ── Mock GPT axes (placeholder scores for pipeline testing) ───────────────
    # IKA: random accuracy between 0.5-1.0 (fraction of questions correct)
    n_q   = len(s.get('questions', []))
    n_ok  = random.randint(n_q // 2, n_q)
    ika   = round(n_ok / max(n_q, 1), 4)
    ika_results = [
        {"task_id": tid, "question": q['q'], "answer": q['answer'],
         "reason": "[MOCK] placeholder"}
        for q in s.get('questions', [])
    ]
    with open(os.path.join(RESULT_ROOT, 'ika_result', f'{tid}.json'), 'w') as f:
        json.dump(ika_results, f, indent=2)
    with open(os.path.join(RESULT_ROOT, 'ika_score', f'{tid}.json'), 'w') as f:
        json.dump({'task_id': tid, 'score': ika}, f, indent=2)
    print(f'  IKA = {ika}  [MOCK: {n_ok}/{n_q} questions]')

    # TC: random 1-5 score
    tc_raw = random.randint(2, 5)
    with open(os.path.join(RESULT_ROOT, 'tc_result', f'{tid}.json'), 'w') as f:
        json.dump({'task_id': tid, 'score': tc_raw,
                   'reason': '[MOCK] placeholder'}, f, indent=2)
    print(f'  TC  = {tc_raw}  [MOCK]')

    # PP: random 1-5 score
    pp_raw = random.randint(2, 5)
    with open(os.path.join(RESULT_ROOT, 'pp_result', f'{tid}.json'), 'w') as f:
        json.dump({'task_id': tid, 'score': pp_raw, 'domain': s['domain'],
                   'reason': '[MOCK] placeholder'}, f, indent=2)
    print(f'  PP  = {pp_raw}  [MOCK]')

    # VF: random 1-3 score
    vf_raw = random.randint(1, 3)
    with open(os.path.join(RESULT_ROOT, 'vf_result', f'{tid}.json'), 'w') as f:
        json.dump({'task_id': tid, 'score': vf_raw,
                   'justification': '[MOCK] placeholder'}, f, indent=2)
    print(f'  VF  = {vf_raw}  [MOCK]')

# ── Full scoring ──────────────────────────────────────────────────────────────
print(f'\n{"="*50}')
print('Running full scoring pipeline...')

from scoring.aggregate import compute_full, compute_gated

result = compute_full(RESULT_ROOT, save_dir=RESULT_ROOT)
gated  = compute_gated(RESULT_ROOT, save_path=os.path.join(RESULT_ROOT, 'gated.json'))

fs = result['relax']['full_set']
print(f'\nFORGE-Relax   = {fs["relax_score"]}')
print(f'Axis means    = {fs["axis_means"]}')
print(f'Strict score  = {result["strict"]["full_set"].get("strict_score")}')
print(f'FORGE-Gated   = {gated["full_set"].get("gated_score")}')
print(f'VFA uncalc    = {gated["full_set"].get("uncalculable", 0)} samples')

print('\nPer-sample:')
for s in result['per_sample']:
    if s['task_id'] in TARGET:
        print(f'  {s["task_id"]:20s}  relax={s["relax"]}  '
              f'ika={s["ika"]}  tc={s["tc"]}  pp={s["pp"]}  '
              f'vf={s["vf"]}  gi={s["gi"]}  rif={s["rif"]}')

print(f'\nOutputs saved to: {RESULT_ROOT}/')
print('NOTE: IKA/TC/PP/VF scores are MOCK placeholders.')
print('      Replace by running eval.run with a real GPT key.')
