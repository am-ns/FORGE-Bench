"""Run GI + VFA + RIF (pure CV, no API key) for a given model.

Usage:
    python run_cv_eval.py <model>            # e.g. hailuo-2.3
    python run_cv_eval.py --all              # run every model folder that has videos
"""
import sys, os, json

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
os.chdir(_HERE)

SAMPLES_FILE = 'dataset/annotations/samples.json'
VIDEO_BASE   = 'dataset/videos'
RESULT_BASE  = 'results'

with open(SAMPLES_FILE, encoding='utf-8') as f:
    all_samples = json.load(f)

sample_by_id = {s['task_id']: s for s in all_samples}

from eval.geometric_integrity import eval_geometric_integrity
from eval.vfa import eval_vfa, save_vfa_result
from eval.reference_fidelity import eval_rif
from eval.reference_fidelity.eval import save_rif_result


def run_model(model: str) -> None:
    video_dir  = os.path.join(VIDEO_BASE, model)
    result_dir = os.path.join(RESULT_BASE, model)

    if not os.path.isdir(video_dir):
        print(f'[{model}] video folder not found: {video_dir}'); return

    videos = sorted(f for f in os.listdir(video_dir) if f.endswith('.mp4'))
    if not videos:
        print(f'[{model}] no .mp4 files'); return

    for sub in ['gi_result', 'vfa_result', 'rif_result']:
        os.makedirs(os.path.join(result_dir, sub), exist_ok=True)

    print(f'\n{"="*60}')
    print(f'Model: {model}  ({len(videos)} videos)')

    for fname in videos:
        tid = os.path.splitext(fname)[0]
        vp  = os.path.join(video_dir, fname)
        s   = sample_by_id.get(tid)
        if s is None:
            print(f'  [{tid}] not in samples.json — skipped'); continue

        s = dict(s, video_path=vp)
        print(f'\n  [{tid}]')

        gi = eval_geometric_integrity(s)
        with open(os.path.join(result_dir, 'gi_result', f'{tid}.json'), 'w') as f:
            json.dump({'task_id': tid, **gi}, f, indent=2)
        print(f'    GI  = {gi.get("score")}  method={gi.get("method","?")}')

        vfa = eval_vfa(s)
        save_vfa_result(vfa, os.path.join(result_dir, 'vfa_result'))
        print(f'    VFA = {vfa["vfa"]}  motion={vfa["motion_detected"]}  type={vfa["motion_type"]}')

        rif = eval_rif(s)
        save_rif_result(rif, os.path.join(result_dir, 'rif_result'))
        print(f'    RIF = {rif["score"]}  ssim={rif["ssim"]}  hist={rif["hist_corr"]}')


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print('Usage: python run_cv_eval.py <model> | --all'); sys.exit(1)

    if args[0] == '--all':
        models = [d for d in os.listdir(VIDEO_BASE)
                  if os.path.isdir(os.path.join(VIDEO_BASE, d))]
    else:
        models = args

    for m in sorted(models):
        run_model(m)

    print(f'\nDone. Results at: {RESULT_BASE}/')
