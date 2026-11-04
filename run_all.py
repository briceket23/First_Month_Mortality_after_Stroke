"""Single documented runner for the NEURI-D-26-00184 reproducibility project.

Real data (secure environment):
    export STROKE_DATA_PATH=/secure/database_stroke_copy.xlsx        # or place it in data/raw/ (git-ignored)
    python run_all.py --mode audit
    python run_all.py --mode all --accept-provisional --clean          # ~45 min on 2 cores

Online / no data (Binder, Colab, CI):
    python scripts/make_synthetic_fixture.py
    STROKE_SYNTHETIC=1 python run_all.py --mode all --accept-provisional --quick --clean   # ~8 min

Modes: audit | observed | reconstructed | sensitivity | all (see config/project.yaml).  The `reconstructed`
mode refuses to run unless config/outcome_definition.yaml -> approval_state is VERIFIED, or it is
DICTIONARY_SUPPORTED_NOT_CUSTODIAN_VERIFIED and --accept-provisional is given (outputs are then stamped
PROVISIONAL).  There is no silent fallback.  Every run writes outputs/logs/execution_log.txt and
outputs/manifests/run_manifest.json (SHA-256 of inputs, configs, code and outputs).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "outputs"
LOG = OUT / "logs" / "execution_log.txt"
PY = [sys.executable, "-W", "ignore"]
sys.path.insert(0, str(SRC))


def run(label, cmd, cwd=ROOT, check=True, env=None):
    t = time.time()
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} START {label}: {' '.join(map(str, cmd))}\n"); fh.flush()
        r = subprocess.run(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT, env=env)
        fh.write(f"=== END {label}: exit {r.returncode} in {time.time() - t:.0f}s\n")
    print(f"{label:<46} exit {r.returncode} {time.time() - t:6.0f}s", flush=True)
    if check and r.returncode != 0:
        tail = LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-40:]
        print("\n".join("  | " + l for l in tail))
        sys.exit(f"step failed: {label} (full log: {LOG})")
    return r.returncode


def gate(mode, accept):
    st = yaml.safe_load((ROOT / "config" / "outcome_definition.yaml").read_text(encoding="utf-8"))["approval_state"]
    if mode in ("audit", "observed"):
        return mode
    if st == "VERIFIED":
        return "reconstructed"
    if st == "DICTIONARY_SUPPORTED_NOT_CUSTODIAN_VERIFIED" and accept:
        return "reconstructed_provisional"
    sys.exit(f"REFUSED: mode '{mode}' requires outcome_definition approval_state VERIFIED (current: {st}). "
             "Pass --accept-provisional to run under the dictionary-supported definition with every output stamped PROVISIONAL.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=["audit", "observed", "reconstructed", "sensitivity", "all"], default="all")
    ap.add_argument("--accept-provisional", action="store_true")
    ap.add_argument("--quick", action="store_true", help="nested CV with 2 outer repeats (demonstration / CI)")
    ap.add_argument("--clean", action="store_true")
    ap.add_argument("--skip-tests", action="store_true")
    a = ap.parse_args()
    env = dict(os.environ, PYTHONPATH=str(SRC) + os.pathsep + os.environ.get("PYTHONPATH", ""), PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    synthetic = env.get("STROKE_SYNTHETIC") == "1"
    if synthetic and not (ROOT / "data" / "synthetic_fixtures" / "synthetic_registry.xlsx").exists():
        subprocess.run(PY + ["scripts/make_synthetic_fixture.py"], cwd=ROOT, env=env, check=True)
    from stroke_repro import config as C  # noqa: E402  (resolves the data path or exits with instructions)
    from stroke_repro.provenance import write_manifest  # noqa: E402
    label = gate(a.mode, a.accept_provisional) + ("_synthetic" if synthetic else "")
    if a.clean:
        for d in ["outputs", "data/processed", "data/interim"]:
            shutil.rmtree(ROOT / d, ignore_errors=True)
        for d in ["tables", "figures"]:
            shutil.rmtree(ROOT / "manuscript" / d, ignore_errors=True)
    for d in ["figures", "tables", "reports", "logs", "manifests", "audit", "cohort", "analysis"]:
        (OUT / d).mkdir(parents=True, exist_ok=True)
    (ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    started = time.strftime("%Y-%m-%d %H:%M:%S")
    LOG.write_text(f"Execution log, started {started}; mode={a.mode}; label={label}; data={C.RAW_XLSX}\n", encoding="utf-8")
    if label.startswith("reconstructed_provisional"):
        (OUT / "PROVISIONAL_OUTCOME_DEFINITION.txt").write_text(
            "Outputs produced under outcome definition " + str(C.YAML["outcome_definition"]["definition_version"]) +
            " with approval_state DICTIONARY_SUPPORTED_NOT_CUSTODIAN_VERIFIED, accepted for this run (--accept-provisional).\n")
    if synthetic:
        (OUT / "SYNTHETIC_DATA_RUN.txt").write_text("These outputs come from the synthetic fixture (no registry data) and demonstrate the pipeline only.\n", encoding="utf-8")
    status = "FAILED"
    try:
        if not a.skip_tests:
            run("tests", PY + ["-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"], env=env)
        run("stage 1 integrity/duplicates/endpoint/cohorts", PY + ["-m", "stroke_repro.stage1_data"], env=env)
        run("stage 1b duplicate field audit", PY + ["-m", "stroke_repro.stage1b_duplicate_fields"], env=env)
        run("stage 1c restricted annex (row-level; data/processed only)", PY + ["-m", "stroke_repro.stage1c_restricted_annex"], env=env)
        run("stage 1d preliminary-audit count reconciliation + stay tables", PY + ["-m", "stroke_repro.stage1d_tracker_reconciliation"], env=env)
        run("stage 1e data dictionary audit", PY + ["-m", "stroke_repro.stage1e_dictionary_audit"], env=env)
        run("date/LOS parser reconciliation", PY + ["scripts/date_parser_reconciliation.py", str(OUT / "audit" / "date_los_parser_reconciliation.json")], env=env)
        run("data quality report", PY + ["scripts/generate_data_audit.py"], env=env)
        if a.mode == "audit":
            status = "OK"; return
        run("stage 2 ascertainment/IPW/delta", PY + ["-m", "stroke_repro.stage2_ascertainment"], env=env)
        if a.mode == "observed":
            run("observed-only summary", PY + ["scripts/observed_only_summary.py", str(OUT / "analysis" / "observed_only_summary.json")], env=env)
            status = "OK"; return
        run("stage 3 models (nested CV, temporal, sensitivity)", PY + ["-m", "stroke_repro.stage3_models"] + (["--quick"] if a.quick else []), env=env)
        run("stage 3b baseline/subgroups", PY + ["-m", "stroke_repro.stage3b_descriptive"], env=env)
        run("post hoc Riley sample size", PY + ["scripts/riley_samplesize.py", str(OUT / "analysis" / "model_results.json"), str(OUT / "analysis" / "riley_samplesize_posthoc.json")], env=env)
        run("observed-only summary", PY + ["scripts/observed_only_summary.py", str(OUT / "analysis" / "observed_only_summary.json")], env=env)
        if a.mode == "sensitivity":
            status = "OK"; return
        run("manuscript tables/figures/macros", PY + ["scripts/generate_manuscript_tables.py"], env=env)
        ms = ROOT / "manuscript"
        if shutil.which("pdflatex"):
            jn = "main_SYNTHETIC_DEMO" if synthetic else "main"   # a synthetic run never overwrites the real manuscript PDF
            for i, cmd in enumerate([["pdflatex", "-interaction=nonstopmode", f"-jobname={jn}", "main.tex"], ["bibtex", jn],
                                     ["pdflatex", "-interaction=nonstopmode", f"-jobname={jn}", "main.tex"], ["pdflatex", "-interaction=nonstopmode", f"-jobname={jn}", "main.tex"]]):
                run(f"latex pass {i + 1}", cmd, cwd=ms, check=False)
            if not synthetic:
                run("response letter", PY + ["-m", "stroke_repro.stage5_response_letter", str(ms / "main.aux"), str(OUT / "reports" / "response_to_reviewers_NEURI-D-26-00184.docx")], env=env)
                run("TRIPOD+AI / RECORD reporting map", PY + ["scripts/tripod_map.py", str(ms / "main.aux"), str(ROOT / "docs" / "TRIPOD_AI_reporting_map.md")], env=env)
        else:
            with open(LOG, "a", encoding="utf-8") as fh:
                fh.write("pdflatex not available: manuscript compilation skipped (tables/figures/macros were generated)\n")
        if not synthetic:
            run("field availability", PY + ["scripts/field_availability.py", str(OUT / "audit" / "field_availability_for_new_questions.csv")], env=env)
            run("verification (99 checks)", PY + ["scripts/verify.py"], env=env)
            run("execution tracker", PY + ["scripts/build_tracker.py", str(ROOT / "docs" / "tracker_original.xlsx"), str(OUT / "reports" / "Stroke_Registry_Revision_Execution_Tracker_updated.xlsx")], env=env)
        run("ticket self-check", PY + ["scripts/ticket_self_check.py"] + (["--synthetic"] if synthetic else []), env=env, check=not synthetic)
        run("aggregate-only output check", PY + ["scripts/privacy_check.py", str(OUT)], env=env)
        status = "OK"
    finally:
        od = C.YAML["outcome_definition"]
        write_manifest(ROOT, OUT, label, status, started, C.RAW_XLSX,
                       extra={"dictionary_sha256": __import__("stroke_repro.provenance", fromlist=["sha256"]).sha256(C.DICT_XLSX),
                              "outcome_definition_version": od["definition_version"], "outcome_approval_state": od["approval_state"],
                              "duplicate_policy": od["duplicate_policy"], "quick": a.quick, "synthetic": synthetic})
        print("manifest written;", status)


if __name__ == "__main__":
    main()
