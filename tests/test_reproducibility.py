"""Fail-safe gate, manifest and privacy check."""
import json, os, subprocess, sys
from conftest import ROOT


def test_reconstructed_mode_refuses_without_acceptance(tmp_path):
    env = dict(os.environ, STROKE_SYNTHETIC="1")
    r = subprocess.run([sys.executable, str(ROOT / "run_all.py"), "--mode", "reconstructed"], env=env, capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode != 0 and "REFUSED" in (r.stdout + r.stderr)


def test_privacy_check_detects_identifier_column(tmp_path):
    (tmp_path / "a.csv").write_text("unique_code,x\nAB2015-01-01,1\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "privacy_check.py"), str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 1


def test_manifest_writer():
    import shutil
    from stroke_repro.provenance import write_manifest
    d = ROOT / "outputs" / "_manifest_test"; d.mkdir(parents=True, exist_ok=True); (d / "x.csv").write_text("a\n1\n", encoding="utf-8")
    try:
        m = write_manifest(ROOT, d, "test", "OK", "now", ROOT / "data" / "synthetic_fixtures" / "synthetic_registry.xlsx")
        assert "run_all.py" in m["code_sha256"] and any("x.csv" in k for k in m["output_sha256"]) and (d / "manifests" / "run_manifest.json").exists()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_synthetic_fixture_has_no_real_identifier_pattern():
    import pandas as pd
    x = pd.read_excel(ROOT / "data" / "synthetic_fixtures" / "synthetic_registry.xlsx", nrows=50)
    assert x["unique_code"].astype(str).str.startswith("S").all()
