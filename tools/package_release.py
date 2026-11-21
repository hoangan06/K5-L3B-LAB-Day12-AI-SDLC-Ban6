"""Đóng gói bản source chạy GUI bằng Python3; không cần Git trên máy người nhận.

python3 tools/package_release.py --out dist/chonoi-v1.0.0.zip
Chỉ lấy source/docs đã cho phép; bỏ file tạm, symlink, môi trường cá nhân và ZIP cũ.
BUILD-INFO.json ghi hash nội dung và các mục release còn thiếu; không tự công bố Release.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "chonoi-v1.0.0"
TOP = {"README.md", "game.contract.json", "TEAM.md", "AGENTS.md", "CHANGELOG.md", "CREDITS.md", "LICENSE"}
FOLDERS = {"chonoi", "tools", "tests", "docs"}
SUFFIXES = {".py", ".mjs", ".js", ".html", ".css", ".json", ".md", ".txt", ".png", ".svg", ".jpg", ".jpeg", ".woff2", ".wav", ".ogg", ".command", ".sh"}
EXCLUDED = {".git", ".venv", "node_modules", "__pycache__", "dist"}


def source_files(root):
    """Allowlist: không theo symlink (kể cả symlink thư mục)."""
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in EXCLUDED or part.startswith(".") for part in relative.parts):
            continue
        if any(parent.is_symlink() for parent in (path, *path.parents) if parent != root.parent):
            continue
        if path.is_file() and (relative.as_posix() in TOP or
                (relative.parts[0] in FOLDERS and path.suffix.lower() in SUFFIXES)):
            yield relative, path


def build_archive(root, destination):
    root = Path(root).resolve()
    destination = Path(destination).resolve()
    for required in ("README.md", "game.contract.json", "chonoi/live.py", "chonoi/web/index.html"):
        if not (root / required).is_file():
            raise ValueError(f"thiếu file chạy GUI: {required}")
    entries = [(relative.as_posix(), path.read_bytes()) for relative, path in source_files(root)]
    paths = {name for name, _ in entries}
    missing = [name for name in ("LICENSE", "CREDITS.md", "CHANGELOG.md", "tools/bench.mjs",
                                "chonoi/soak.py", "docs/release-notes-v1.0.0.md") if name not in paths]
    try:
        revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
                                  text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        revision = None
    metadata = {"source_commit": revision, "missing_release_inputs": missing,
                "files_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in entries}}
    entries.append(("BUILD-INFO.json", (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8")))
    destination.parent.mkdir(parents=True, exist_ok=True)
    # X = không ghi đè một gói đã tạo; build lại dùng tên mới để giữ bằng chứng cũ.
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries:
            info = zipfile.ZipInfo(f"{PREFIX}/{name}", date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o100755 if Path(name).suffix in (".command", ".sh") else 0o100644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    return metadata


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        metadata = build_archive(ROOT, args.out)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"không đóng gói được: {exc}", file=sys.stderr)
        return 1
    print(f"Đã tạo {args.out}")
    if metadata["missing_release_inputs"]:
        print("Gói ứng viên; còn thiếu đầu vào phát hành: " + ", ".join(metadata["missing_release_inputs"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
