"""Step logger used by run_all.py."""
import time


def step_log(log_path, label, cmd, returncode, seconds):
    with open(log_path, 'a') as fh:
        fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {label}: {' '.join(map(str, cmd))} -> exit {returncode} in {seconds:.0f}s\n")
