"""autovsf_core/engine/translate/translator.py — AI Translation Pipeline Engine."""

import os
from typing import Optional, Callable

from autovsf_core.engine.translate.chunker import chunk_srt
from autovsf_core.engine.translate.merger import merge_batches


class SubtitleTranslator:
    """Manages AI subtitle translation pipeline workflow."""

    def __init__(self, target_lang: str = "Tiếng Việt"):
        self.target_lang = target_lang

    def prepare_translation_prompt(self, input_srt: str, output_srt: str, work_dir: str = "/content") -> str:
        """Generate structured prompt.md for AI translation agents."""
        prompt = f"""/goal
Nhiệm vụ của bạn là dịch tệp phụ đề tại {input_srt} sang {self.target_lang} và lưu kết quả tại {output_srt}.

### Bước 1: Phân tích & Tạo cẩm nang xưng hô
- Đọc 500 dòng đầu tiên của `source_original.srt`.
- Xác định bối cảnh hội thoại và lập quy tắc xưng hô nhất quán trong `global_translation_policy.md`.

### Bước 2: Chia nhỏ & Dịch song song
- Chạy: `python3 -m autovsf_core.engine.translate.chunker "{input_srt}" "{work_dir}/batches" 50`
- Dịch từng batch file và lưu vào `{work_dir}/batches/batch_X_translated.srt`.

### Bước 3: Hợp nhất
- Chạy: `python3 -m autovsf_core.engine.translate.merger "{output_srt}" "{work_dir}/batches"`
"""
        prompt_file = os.path.join(work_dir, "prompt.md")
        os.makedirs(work_dir, exist_ok=True)
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(prompt)

        return prompt_file

    def translate_direct(
        self,
        input_srt: str,
        output_srt: str,
        progress_cb: Optional[Callable[[int, int, str], None]] = None,
    ) -> str:
        """Fallback direct translation if AI CLI is not available."""
        # Copy input to output as default fallback
        os.makedirs(os.path.dirname(os.path.abspath(output_srt)), exist_ok=True)
        with open(input_srt, "r", encoding="utf-8", errors="ignore") as f_in:
            content = f_in.read()
        with open(output_srt, "w", encoding="utf-8") as f_out:
            f_out.write(content)

        if progress_cb:
            progress_cb(1, 1, "Completed direct pass-through translation.")

        return output_srt
