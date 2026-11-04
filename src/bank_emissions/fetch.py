"""Download helpers: polite HTTP fetch, PDF validation and SHA-256 hashing."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/130.0 Safari/537.36 research-script"
    )
}


@dataclass
class FetchResult:
    url: str
    local_path: str = ""
    http_status: int | None = None
    content_type: str = ""
    file_size_bytes: int | None = None
    sha256: str = ""
    is_pdf: bool = False
    error: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def _describe(path: Path, res: FetchResult) -> FetchResult:
    res.local_path = str(path)
    res.file_size_bytes = path.stat().st_size
    res.sha256 = sha256_file(path)
    with open(path, "rb") as f:
        res.is_pdf = f.read(5) == b"%PDF-"
    return res


def download(url: str, dest: Path, timeout: int = 300, retries: int = 1,
             pause: float = 1.0) -> FetchResult:
    """Download ``url`` to ``dest`` unless it already exists as a valid PDF."""
    res = FetchResult(url=url)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        res.http_status = 0  # 0 = cached copy from an earlier run
        return _describe(dest, res)
    tmp = dest.with_suffix(dest.suffix + ".part")
    for attempt in range(retries + 1):
        try:
            with requests.get(url, headers=UA, stream=True, timeout=timeout,
                              allow_redirects=True) as r:
                res.http_status = r.status_code
                res.content_type = r.headers.get("Content-Type", "")
                if r.status_code != 200:
                    res.error = f"HTTP {r.status_code}"
                    break
                with open(tmp, "wb") as f:
                    for block in r.iter_content(1 << 20):
                        f.write(block)
            with open(tmp, "rb") as f:
                head = f.read(5)
            if head != b"%PDF-":
                res.error = f"not a PDF (starts {head!r}, content-type {res.content_type})"
                tmp.unlink(missing_ok=True)
                break
            tmp.replace(dest)
            res.error = ""
            time.sleep(pause)
            return _describe(dest, res)
        except requests.RequestException as exc:
            res.error = f"{type(exc).__name__}: {exc}"[:300]
            tmp.unlink(missing_ok=True)
            time.sleep(3 * (attempt + 1))
    return res
