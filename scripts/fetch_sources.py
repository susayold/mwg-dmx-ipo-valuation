"""Download official filings declared in the source registry.

The downloader is intentionally conservative: only HTTPS URLs are accepted,
every destination must remain under ``data/raw``, and a file is published only
after its SHA-256 matches the registry. Raw filings stay git-ignored and their
owners' terms continue to apply.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "data" / "source_registry.csv"
RAW_ROOT = (ROOT / "data" / "raw").resolve()
CHUNK_SIZE = 1024 * 1024
DEFAULT_MAX_BYTES = 100 * 1024 * 1024


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_target(local_path: str) -> Path:
    target = (ROOT / local_path).resolve()
    if not target.is_relative_to(RAW_ROOT):
        raise ValueError(f"registry path escapes data/raw: {local_path}")
    return target


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"only absolute HTTPS source URLs are accepted: {url}")


def download_verified(
    url: str,
    target: Path,
    expected_sha256: str,
    *,
    timeout: int,
    max_bytes: int,
    force: bool,
) -> str:
    validate_url(url)
    expected_sha256 = expected_sha256.strip().lower()
    if len(expected_sha256) != 64:
        raise ValueError("missing or invalid registry SHA-256")

    if target.exists():
        actual = file_sha256(target)
        if actual == expected_sha256:
            return "already verified"
        if not force:
            raise ValueError(
                f"existing file hash mismatch ({actual}); use --force to replace it"
            )

    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(f"{target.name}.part")
    request = Request(
        url,
        headers={
            "User-Agent": "MWG-DMX-portfolio-research/1.0 (+local source verification)",
            "Accept": "application/pdf, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, */*",
        },
    )

    digest = hashlib.sha256()
    total = 0
    try:
        with urlopen(request, timeout=timeout) as response, partial.open("wb") as output:
            declared_size = response.headers.get("Content-Length")
            if declared_size and int(declared_size) > max_bytes:
                raise ValueError(
                    f"source declares {int(declared_size):,} bytes, above limit {max_bytes:,}"
                )
            while chunk := response.read(CHUNK_SIZE):
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError(f"download exceeded size limit of {max_bytes:,} bytes")
                digest.update(chunk)
                output.write(chunk)

        actual = digest.hexdigest()
        if actual != expected_sha256:
            raise ValueError(f"download hash mismatch: expected {expected_sha256}, got {actual}")
        os.replace(partial, target)
        return f"downloaded and verified ({total:,} bytes)"
    finally:
        if partial.exists():
            partial.unlink()


def select_rows(
    registry: Path, issuers: set[str], source_ids: set[str]
) -> list[dict[str, str]]:
    with registry.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    selected = []
    for row in rows:
        if issuers and row.get("issuer", "").upper() not in issuers:
            continue
        if source_ids and row.get("source_id", "") not in source_ids:
            continue
        if not row.get("direct_url") or not row.get("local_path"):
            continue
        selected.append(row)
    return selected


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download and SHA-256 verify official files in data/source_registry.csv"
    )
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--issuer", action="append", default=[], help="DMX or MWG; repeatable")
    parser.add_argument("--source-id", action="append", default=[], help="exact source ID; repeatable")
    parser.add_argument("--dry-run", action="store_true", help="validate and print without network access")
    parser.add_argument("--force", action="store_true", help="replace an existing hash-mismatched file")
    parser.add_argument("--max-files", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--max-mib", type=int, default=100)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    issuers = {issuer.upper() for issuer in args.issuer}
    source_ids = set(args.source_id)
    rows = select_rows(args.registry, issuers, source_ids)
    if args.max_files is not None:
        if args.max_files < 1:
            raise SystemExit("--max-files must be positive")
        rows = rows[: args.max_files]
    if not rows:
        raise SystemExit("No downloadable registry rows matched the filters")

    failures = 0
    for row in rows:
        source_id = row["source_id"]
        try:
            target = safe_target(row["local_path"])
            validate_url(row["direct_url"])
            if args.dry_run:
                print(f"DRY-RUN {source_id}: {target.relative_to(ROOT)}")
                continue
            result = download_verified(
                row["direct_url"],
                target,
                row["sha256"],
                timeout=args.timeout,
                max_bytes=args.max_mib * 1024 * 1024,
                force=args.force,
            )
            print(f"OK {source_id}: {result}")
        except (ValueError, OSError, HTTPError, URLError) as exc:
            failures += 1
            print(f"ERROR {source_id}: {exc}", file=sys.stderr)

    print(f"Processed {len(rows)} source(s); failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
