"""End-to-end audit mode on the synthetic fixture, executed in a temporary copy so the project's outputs are never touched (~1 min)."""
import os, shutil, subprocess, sys
from conftest import ROOT


def test_audit_mode_runs_on_synthetic_fixture(tmp_path):
    proj = tmp_path / "proj"
    for d in ["src", "scripts", "config", "dictionary", "data/synthetic_fixtures", "tests"]:
        shutil.copytree(ROOT / d, proj / d, ignore=shutil.ignore_patterns("__pycache__"))
    for f in ["run_all.py", "CITATION.cff"]:
        shutil.copy(ROOT / f, proj / f)
    (proj / "docs").mkdir(); (proj / "manuscript").mkdir()
    shutil.copy(ROOT / "docs" / "tickets.json", proj / "docs" / "tickets.json")
    shutil.copy(ROOT / "manuscript" / "main.tex", proj / "manuscript" / "main.tex")
    env = dict(os.environ, STROKE_SYNTHETIC="1"); env.pop("STROKE_DATA_PATH", None)
    r = subprocess.run([sys.executable, str(proj / "run_all.py"), "--mode", "audit", "--skip-tests"], env=env, capture_output=True, text=True, cwd=proj)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    assert (proj / "outputs" / "manifests" / "run_manifest.json").exists() and (proj / "docs" / "data_quality_report.md").exists()
    assert not (ROOT / "outputs" / "SYNTHETIC_DATA_RUN.txt").exists()
