"""autovsf_core/engine/translate/merger.py — Merges translated batch SRT files back together."""

import os
import re
from typing import List


def merge_batches(output_srt_path: str, batches_dir: str) -> str:
    """Merges all translated batch_X_translated.srt or batch_X.srt files into output_srt_path."""
    if not os.path.exists(batches_dir):
        raise FileNotFoundError(f"Batches directory not found: {batches_dir}")

    files = sorted(
        [f for f in os.listdir(batches_dir) if f.endswith(".srt")],
        key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", x)],
    )

    all_blocks = []
    block_index = 1

    for fname in files:
        fpath = os.path.join(batches_dir, fname)
        with open(fpath, "r", encoding="utf-8-sig", errors="ignore") as f:
            content = f.read()

        blocks = [b.strip() for b in re.split(r"\n\s*\n", content) if b.strip()]
        for b in blocks:
            lines = b.split("\n")
            if len(lines) >= 2:
                # Re-number block sequentially
                lines[0] = str(block_index)
                all_blocks.append("\n".join(lines))
                block_index += 1

    os.makedirs(os.path.dirname(os.path.abspath(output_srt_path)), exist_ok=True)
    with open(output_srt_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_blocks) + "\n\n")

    return output_srt_path
