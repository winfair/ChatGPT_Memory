#!/usr/bin/env python3
import argparse, pathlib, shutil, subprocess, sys

REPO = pathlib.Path(__file__).resolve().parents[1]

def copytree(src: pathlib.Path, dst: pathlib.Path):
    if dst.exists():
        raise SystemExit(f"Destination already exists: {dst}")
    shutil.copytree(src, dst)

def main():
    ap = argparse.ArgumentParser(description="Sync a MemoryBuild folder into this repo")
    ap.add_argument("memorybuild_path", type=str, help="Path to MemoryBuild_<timestamp> folder")
    ap.add_argument("--commit", action="store_true", help="git add/commit/push after sync")
    ap.add_argument("--branch", type=str, default=None, help="git branch to commit to (optional)")
    args = ap.parse_args()

    src = pathlib.Path(args.memorybuild_path).expanduser().resolve()
    if not src.exists():
        raise SystemExit(f"Not found: {src}")

    ts = src.name.replace("MemoryBuild_", "")
    run_dst = REPO / "runs" / ts
    run_dst.mkdir(parents=True, exist_ok=False)

    for sub in ("archives", "parsed", "vectors"):
        s = src / sub
        if not s.exists():
            print(f"[WARN] Missing {sub} in {src}")
            continue
        d = run_dst / sub
        shutil.copytree(s, d)

    upd = REPO / "tools" / "update_index.py"
    if not upd.exists():
        raise SystemExit("Missing tools/update_index.py")
    print("Updating index …")
    subprocess.check_call([sys.executable, str(upd)], cwd=str(REPO))

    if args.commit:
        print("Staging/committing …")
        if args.branch:
            subprocess.check_call(["git", "checkout", args.branch], cwd=str(REPO))
        subprocess.check_call(["git", "add", "."], cwd=str(REPO))
        msg = f"Add run {ts} + rebuild index"
        subprocess.check_call(["git", "commit", "-m", msg], cwd=str(REPO))
        try:
            subprocess.check_call(["git", "push"], cwd=str(REPO))
        except subprocess.CalledProcessError:
            print("[WARN] git push failed—check remote/branch auth.")

    print(f"Done. New run at: {run_dst}")

if __name__ == "__main__":
    main()
