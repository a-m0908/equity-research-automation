"""Fetch EDINET document index (Japan FSA). Requires a personal subscription key.

The API ``type`` query parameter selects the response shape for the documents list
(e.g. metadata fields returned), per the FSA EDINET API v2 specification. It does **not**
narrow results to a single filing category such as annual securities reports only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
LIST_URL = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"


def fetch_edinet_document_list(date: str, doc_type: int = 2) -> dict:
    """``doc_type`` is the API ``type`` parameter (list format / metadata), not a filing-type filter."""
    key = os.environ.get("EDINET_SUBSCRIPTION_KEY")
    if not key:
        raise RuntimeError(
            "Set EDINET_SUBSCRIPTION_KEY to your FSA EDINET API v2 subscription key."
        )
    r = requests.get(
        LIST_URL,
        params={"date": date, "type": doc_type},
        headers={"Subscription-Key": key},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def save_document_list(date: str, doc_type: int = 2) -> Path:
    payload = fetch_edinet_document_list(date, doc_type)
    out_dir = ROOT / "data" / "edinet"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"documents_{date}_type{doc_type}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> None:
    p = argparse.ArgumentParser(description="Save EDINET daily document list as JSON.")
    p.add_argument("--date", required=True, help="Disclosure date YYYY-MM-DD")
    p.add_argument(
        "--type",
        type=int,
        default=2,
        help=(
            "EDINET API `type` query value (see FSA EDINET API v2 spec). "
            "Controls list/metadata columns for that date, not a single filing-kind filter."
        ),
    )
    args = p.parse_args()
    try:
        out = save_document_list(args.date, args.type)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    print(out)


if __name__ == "__main__":
    main()
