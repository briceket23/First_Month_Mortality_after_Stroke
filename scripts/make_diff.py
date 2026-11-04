"""Build a change-marked manuscript (latexdiff) between the June 2026 source and the revision.

Both sources are flattened (\\input files inlined). Macros of the old source are expanded to their values
before diffing, because several macro names were reused with different values in the revision.
Usage: python tools/make_diff.py OLD_DIR NEW_DIR OUT_DIR
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path


def flatten(d: Path, name="main.tex"):
    txt = (d / name).read_text(encoding="utf-8")

    def rep(m):
        f = d / (m.group(1) + ("" if m.group(1).endswith(".tex") else ".tex"))
        return f.read_text(encoding="utf-8") if f.exists() else m.group(0)
    for _ in range(3):
        txt = re.sub(r"\\input\{([^}]*)\}", rep, txt)
    return txt


def expand_macros(txt):
    defs = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{([^\n]*)\}\n", txt))
    txt = re.sub(r"\\newcommand\{\\\w+\}\{[^\n]*\}\n", "", txt)
    for k in sorted(defs, key=len, reverse=True):
        txt = re.sub(r"\\" + k + r"(\{\})?(?![A-Za-z])", lambda _m, v=defs[k]: v, txt)
    return txt


def main(old, new, out):
    old, new, out = Path(old), Path(new), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "old_flat.tex").write_text(expand_macros(flatten(old)), encoding="utf-8")
    (out / "new_flat.tex").write_text(expand_macros(flatten(new)), encoding="utf-8")
    (out / "figures").mkdir(exist_ok=True)
    for d in (old, new):
        for f in (d / "figures").glob("*.png"):
            shutil.copy(f, out / "figures" / f.name)
    shutil.copy(new / "stroke_bib.bib", out / "stroke_bib.bib")
    with open(out / "main_diff.tex", "w", encoding="utf-8") as fh:
        subprocess.run(["latexdiff", "--type=CFONT", "--graphics-markup=none", "--math-markup=coarse",
                        "--exclude-safecmd=cite", "--exclude-textcmd=caption,section,subsection", str(out / "old_flat.tex"), str(out / "new_flat.tex")], stdout=fh, check=True)
    for cmd in (["pdflatex", "-interaction=nonstopmode", "main_diff.tex"], ["bibtex", "main_diff"],
                ["pdflatex", "-interaction=nonstopmode", "main_diff.tex"], ["pdflatex", "-interaction=nonstopmode", "main_diff.tex"]):
        subprocess.run(cmd, cwd=out, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("diff pdf:", (out / "main_diff.pdf").exists())


if __name__ == "__main__":
    main(*sys.argv[1:4])
