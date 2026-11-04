"""SHA-256 run manifest: inputs, configs, code, software versions, seed, outcome-definition version/approval state, duplicate policy, outputs."""
import hashlib, json, platform, time
from pathlib import Path


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for ch in iter(lambda: f.read(1 << 20), b''):
            h.update(ch)
    return h.hexdigest()


def versions():
    import importlib
    out = {}
    for m in ['pandas', 'numpy', 'scipy', 'sklearn', 'xgboost', 'shap', 'statsmodels', 'openpyxl', 'matplotlib', 'yaml']:
        try:
            out[m] = importlib.import_module(m).__version__
        except Exception:
            out[m] = 'not installed'
    return out


def write_manifest(root, out_dir, mode_label, status, started, data_path, extra=None):
    root, out_dir = Path(root), Path(out_dir)
    code = {str(p.relative_to(root)): sha256(p) for p in sorted((root / 'src').rglob('*.py')) if '__pycache__' not in str(p)}
    code.update({str(p.relative_to(root)): sha256(p) for p in sorted((root / 'scripts').glob('*.py'))})
    code['run_all.py'] = sha256(root / 'run_all.py')
    cfg = {p.name: sha256(p) for p in sorted((root / 'config').iterdir()) if p.is_file()}
    outs = {str(p.relative_to(root)): sha256(p) for p in sorted(out_dir.rglob('*'))
            if p.is_file() and p.suffix != '.pkl' and 'manifests' not in str(p) and 'logs' not in str(p)}
    m = {'project': 'stroke_reproducibility_rebuilt', 'manuscript': 'NEURI-D-26-00184', 'analysis_mode': mode_label, 'run_status': status,
         'started': started, 'finished': time.strftime('%Y-%m-%d %H:%M:%S'), 'python': platform.python_version(), 'platform': platform.platform(),
         'software_versions': versions(), 'random_seed': 20261016,
         'source_workbook': {'path': str(data_path), 'sha256': sha256(data_path) if Path(data_path).exists() else None},
         'config_sha256': cfg, 'code_sha256': code, 'output_sha256': outs, 'git_commit': None}
    m.update(extra or {})
    (out_dir / 'manifests').mkdir(parents=True, exist_ok=True)
    (out_dir / 'manifests' / 'run_manifest.json').write_text(json.dumps(m, indent=1), encoding="utf-8")
    return m
