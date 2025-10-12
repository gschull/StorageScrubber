"""Core scanning and cleaning logic for Storage Scrubber"""
from dataclasses import dataclass, asdict
import os
import sys
import time
import json
from typing import List, Dict, Any
import hashlib
import fnmatch

try:
    from send2trash import send2trash
except Exception:
    send2trash = None

TEMP_PATTERNS = ["~", ".tmp", ".temp", ".crdownload", ".part", "__pycache__", "thumbs.db", "desktop.ini"]
UPDATE_PATTERNS = [".msi", ".msix", ".exe", ".upd"]
CACHE_DIR_NAMES = ["cache", "tmp", "temp", "logs"]
# Additional common large cache/module directories considered safe-to-clean candidates
AUTO_CLEAN_DIR_NAMES = ["node_modules", ".cache", "cache", "Temp", "tmp"]


@dataclass
class FileInfo:
    path: str
    size: int
    mtime: float
    atime: float
    ctime: float
    ext: str
    hash: str = ""


class StorageScrubber:
    def __init__(self, root: str = '.'):
        self.root = os.path.abspath(root)

    def scan(self, min_size: int = 0, min_age_days: int = 0, exclude_patterns: List[str] = None) -> List[FileInfo]:
        """Scan for files. exclude_patterns may contain substrings or glob patterns matched against the
        path relative to the scan root."""
        results: List[FileInfo] = []
        self._exclude_patterns = exclude_patterns or []
        now = time.time()
        min_age_seconds = min_age_days * 86400

        for dirpath, dirnames, filenames in os.walk(self.root):
            # apply exclude patterns (support substring or glob on relative path)
            rel = os.path.relpath(dirpath, self.root)
            skip_dir = False
            for pat in self._exclude_patterns:
                try:
                    if any(ch in pat for ch in ['*', '?', '[']):
                        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(dirpath, pat):
                            skip_dir = True
                            break
                    else:
                        if pat in dirpath or pat in rel:
                            skip_dir = True
                            break
                except Exception:
                    continue
            if skip_dir:
                continue
            # skip hidden recycle bin and system folders on Windows
            if os.path.basename(dirpath).lower() in ["$recycle.bin", "recycler"]:
                continue
            # lightweight progress
            # print progress every 2000 files to stderr to avoid noisy stdout reports
            # (we count filenames in this directory)
            # NOTE: this is intentionally simple and dependency-free
            scanned_here = len(filenames)
            if scanned_here and scanned_here % 2000 == 0:
                print(f"Scanning {dirpath} ({scanned_here} files)...", file=sys.stderr)
            for name in filenames:
                try:
                    fp = os.path.join(dirpath, name)
                    st = os.stat(fp)
                except Exception:
                    continue
                size = st.st_size
                mtime = st.st_mtime
                atime = st.st_atime
                ctime = st.st_ctime
                ext = os.path.splitext(name)[1].lower()
                if size < min_size:
                    continue
                if (now - mtime) < min_age_seconds:
                    continue
                fi = FileInfo(path=fp, size=size, mtime=mtime, atime=atime, ctime=ctime, ext=ext)
                results.append(fi)
        return results

    def compute_hash(self, fileinfo: FileInfo, chunk_size: int = 8192) -> str:
        h = hashlib.sha256()
        try:
            with open(fileinfo.path, 'rb') as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    h.update(data)
        except Exception:
            return ""
        fileinfo.hash = h.hexdigest()
        return fileinfo.hash

    def find_duplicates(self, files: List[FileInfo]) -> List[List[FileInfo]]:
        # compute hashes for all files (only when size >0)
        by_hash = {}
        for f in files:
            if f.size == 0:
                continue
            if not f.hash:
                self.compute_hash(f)
            if not f.hash:
                continue
            by_hash.setdefault(f.hash, []).append(f)
        groups = [v for v in by_hash.values() if len(v) > 1]
        return groups

    def top_files(self, files: List[FileInfo], n: int = 20) -> List[FileInfo]:
        return sorted(files, key=lambda f: f.size, reverse=True)[:n]

    def classify(self, fileinfo: FileInfo) -> str:
        p = fileinfo.path.lower()
        name = os.path.basename(p)
        if any(p.endswith(pat) for pat in TEMP_PATTERNS):
            return 'temp'
        if any(name.endswith(pat) for pat in TEMP_PATTERNS):
            return 'temp'
        if any(pat in p for pat in CACHE_DIR_NAMES):
            return 'cache'
        if fileinfo.ext in UPDATE_PATTERNS:
            return 'update'
        return 'personal'

    def summary(self, files: List[FileInfo]) -> str:
        total = sum(f.size for f in files)
        counts = {}
        for f in files:
            cls = self.classify(f)
            counts[cls] = counts.get(cls, 0) + 1
        lines = [f"Scanned {len(files)} files, reclaimable size {self._format_size(total)}"]
        for k, v in counts.items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)

    def select_auto_clean(self, files: List[FileInfo]) -> List[FileInfo]:
        candidates = [f for f in files if self.classify(f) in ('temp', 'cache', 'update')]
        # also include files inside common auto-clean directories
        extra = []
        for f in files:
            p = f.path.lower()
            if any(seg.lower() in p for seg in AUTO_CLEAN_DIR_NAMES):
                if f not in candidates:
                    extra.append(f)
        candidates.extend(extra)
        return candidates

    def delete_files(self, files: List[FileInfo], confirm: bool = False, interactive: bool = False, permanent: bool = False):
        """Delete (send to Recycle Bin) files. If interactive=True, prompt per-file."""
        if not files:
            print("No files to delete")
            return
        if not confirm and not interactive:
            ans = input(f"Delete {len(files)} files? [y/N]: ")
            if ans.strip().lower() != 'y':
                print("Aborted")
                return
        if send2trash is None and not permanent:
            print("send2trash is not installed; cannot safely delete to Recycle Bin. Install send2trash or set up permanently deletion carefully.")
            return
        for f in files:
            try:
                if interactive:
                    ans = input(f"Delete {f.path}? [y/N]: ")
                    if ans.strip().lower() != 'y':
                        print(f"Skipped: {f.path}")
                        continue
                if permanent:
                    os.remove(f.path)
                else:
                    send2trash(f.path)
                print(f"Moved to Recycle Bin: {f.path}")
            except Exception as e:
                print(f"Failed to delete {f.path}: {e}")

    def write_json_report(self, files: List[FileInfo], outpath: str):
        arr = [asdict(f) for f in files]
        with open(outpath, 'w', encoding='utf-8') as fh:
            json.dump(arr, fh, indent=2)

    @staticmethod
    def _format_size(n: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if n < 1024:
                return f"{n:.1f}{unit}"
            n /= 1024
        return f"{n:.1f}PB"
