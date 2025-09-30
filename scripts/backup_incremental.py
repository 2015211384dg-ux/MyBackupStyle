import os, shutil, time, json, zipfile
from pathlib import Path
from datetime import datetime, timedelta

HERE = Path(__file__).resolve().parent
cfg = json.load(open(HERE / "config.json", "r", encoding="utf-8"))

src = Path(cfg["source"])
dst = Path(cfg["dest"])
arc = Path(cfg["archive_root"])
logd = Path(cfg["log_dir"])

for p in [dst, arc, logd]:
    p.mkdir(parents=True, exist_ok=True)

stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logp = logd / f"incremental_{stamp}.log"

def log(msg: str):
    with open(logp, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def should_skip(path: Path) -> bool:
    if any(part in cfg["excludes"] for part in path.parts):
        return True
    if path.suffix.lower() in [e.lower() for e in cfg["exclude_ext"]]:
        return True
    return False

def copy_incremental():
    copied = 0
    for root, dirs, files in os.walk(src):
        # exclude dirs in-place
        dirs[:] = [d for d in dirs if not should_skip(Path(root) / d)]
        for name in files:
            sp = Path(root) / name
            if should_skip(sp):
                continue
            rel = sp.relative_to(src)
            dp = dst / rel
            dp.parent.mkdir(parents=True, exist_ok=True)
            try:
                if (not dp.exists()
                    or sp.stat().st_size != dp.stat().st_size
                    or int(sp.stat().st_mtime) != int(dp.stat().st_mtime)):
                    shutil.copy2(sp, dp)
                    copied += 1
            except Exception as e:
                log(f"ERROR copy: {sp} -> {dp} ({e})")
    log(f"Incremental copied: {copied} files")

def archive_old(ret_days=30):
    cutoff = datetime.now() - timedelta(days=ret_days)
    daydir = arc / datetime.now().strftime("%Y-%m-%d")
    daydir.mkdir(parents=True, exist_ok=True)
    zpath = daydir / f"archive_{stamp}.zip"
    removed = 0
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, _, files in os.walk(dst):
            for name in files:
                fp = Path(root) / name
                try:
                    if datetime.fromtimestamp(fp.stat().st_mtime) < cutoff:
                        zf.write(fp, fp.relative_to(dst).as_posix())
                        fp.unlink(missing_ok=True)
                        removed += 1
                except FileNotFoundError:
                    pass
    log(f"Archived & removed: {removed} files -> {zpath}")

def cleanup_archives(older_days=90):
    cutoff = datetime.now() - timedelta(days=older_days)
    deleted = 0
    for root, _, files in os.walk(arc):
        for name in files:
            if name.lower().endswith(".zip"):
                fp = Path(root) / name
                try:
                    if datetime.fromtimestamp(fp.stat().st_mtime) < cutoff:
                        fp.unlink(missing_ok=True)
                        deleted += 1
                except FileNotFoundError:
                    pass
    log(f"Removed old archives: {deleted}")

if __name__ == "__main__":
    start = time.time()
    try:
        copy_incremental()
        archive_old(cfg["retention_days"])
        cleanup_archives(cfg["cleanup_archive_older_days"])
        log(f"Done in {time.time()-start:.1f}s")
        raise SystemExit(0)
    except Exception as e:
        log(f"FATAL: {e}")
        raise SystemExit(1)
