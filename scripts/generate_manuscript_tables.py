"""Regenerate every manuscript table, figure and macro from fresh aggregate outputs (stage 4)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from stroke_repro.stage4_report import main
if __name__ == "__main__":
    main()
