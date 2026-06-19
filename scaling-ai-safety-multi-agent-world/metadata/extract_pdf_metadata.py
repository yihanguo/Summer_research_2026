from __future__ import annotations

import json
import hashlib
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    records = []
    checksums = []
    for path in sorted(ROOT.rglob("*.pdf")):
        try:
            reader = PdfReader(path)
            metadata = reader.metadata or {}
            sample_pages = []
            for page in reader.pages[:3]:
                sample_pages.append((page.extract_text() or "").strip())
            records.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "pages": len(reader.pages),
                    "title": metadata.get("/Title"),
                    "author": metadata.get("/Author"),
                    "sample_text": "\n\n".join(sample_pages)[:16000],
                }
            )
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            checksums.append(f"{digest}  {path.relative_to(ROOT)}")
        except Exception as exc:
            records.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    output = ROOT / "metadata" / "pdf_extracts.json"
    output.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    (ROOT / "SHA256SUMS.txt").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} records to {output}")


if __name__ == "__main__":
    main()
