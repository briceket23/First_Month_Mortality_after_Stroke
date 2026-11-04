import os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("STROKE_SYNTHETIC", "1")   # tests never need registry data
os.environ.setdefault("PYTHONUTF8", "1")         # Windows: subprocesses read/write UTF-8
if not (ROOT / "data" / "synthetic_fixtures" / "synthetic_registry.xlsx").exists():
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "scripts" / "make_synthetic_fixture.py")], check=True)
