"""autovsf_core/engine/translate/chunker.py — Chunks SRT files into batches."""

import os
import re
from pathlib import Path
from typing import List


def chunk_srt(input_srt_path: str, output_dir: str, batch_size: int = 50) -> List[str]:
    """Splits an SRT file into small batches of batch_size entries each. Returns list of batch file paths."""
    if not os.path.exists(input_srt_path):
        raise FileNotFoundError(f"SRT file not found: {input_srt_path}")

    os.makedirs(output_dir, exist_ok=True)

    with open(input_srt_path, "r", encoding="utf-8-sig", errors="ignore") as f:
        content = f.read()

    # Split blocks by double newlines
    raw_blocks = [b.strip() for b in re.split(r"\n\s*\n", content) if b.strip()]

    batch_files = []
    current_batch = []
    batch_num = 1

    for block in raw_blocks:
        current_batch.append(block)
        if len(current_batch) >= batch_size:
            out_file = os.path.join(output_dir, f"batch_{batch_num}.srt")
            with open(out_file, "w", encoding="utf-8") as f_out:
                f_out.write("\n\n".join(current_batch) + "\n\n")
            batch_files.append(out_file)
            batch_num += 1
            current_batch = []

    if current_batch:
        out_file = os.path.join(output_dir, f"batch_{batch_num}.srt")
        with open(out_file, "w", encoding="utf-8") as f_out:
            f_out.write("\n\n".join(current_batch) + "\n\n")
        batch_files.append(out_file)

    return batch_files
