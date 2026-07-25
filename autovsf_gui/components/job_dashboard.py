"""autovsf_gui/components/job_dashboard.py — Real-time Queue & Worker Progress Dashboard Widget."""

import tkinter as tk
from tkinter import ttk
from typing import Dict

from autovsf_core.domain.job import Job
from autovsf_core.queue.manager import queue_manager


class JobDashboardView(tk.Frame):
    """GUI Frame presenting real-time worker task queue, progress bars, and execution logs."""

    def __init__(self, master: tk.Widget):
        super().__init__(master, bg="#222222")

        lbl = tk.Label(
            self,
            text="📊 Processing Queue & Worker Monitor",
            font=("Helvetica", 12, "bold"),
            fg="#00FFFF",
            bg="#222222",
        )
        lbl.pack(anchor=tk.W, padx=10, pady=5)

        # Job Treeview Table
        columns = ("job_id", "status", "video", "vsf_pct", "ocr_status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=8)
        self.tree.heading("job_id", text="Job ID")
        self.tree.heading("status", text="Status")
        self.tree.heading("video", text="Video File")
        self.tree.heading("vsf_pct", text="VSF %")
        self.tree.heading("ocr_status", text="OCR Progress")

        self.tree.column("job_id", width=80)
        self.tree.column("status", width=120)
        self.tree.column("video", width=350)
        self.tree.column("vsf_pct", width=80)
        self.tree.column("ocr_status", width=120)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Progress Bar & Status Text
        self.progress_bar = ttk.Progressbar(self, mode="determinate")
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        self.status_lbl = tk.Label(self, text="Ready.", fg="#00FF00", bg="#222222", font=("Consolas", 10))
        self.status_lbl.pack(anchor=tk.W, padx=10, pady=5)

        # Subscribe to QueueManager updates
        queue_manager.subscribe(self._on_queue_update)

    def _on_queue_update(self, job: Job, task_name: str, pct: float, msg: str):
        self.after(0, lambda: self._update_ui(job, task_name, pct, msg))

    def _update_ui(self, job: Job, task_name: str, pct: float, msg: str):
        # Update Treeview item
        item_id = job.job_id
        video_name = job.video_path.split("/")[-1]
        ocr_str = f"{job.ocr_done}/{job.ocr_total}" if job.ocr_total > 0 else "--"

        values = (job.job_id, job.status.value, video_name, f"{job.vsf_progress:.1f}%", ocr_str)

        if self.tree.exists(item_id):
            self.tree.item(item_id, values=values)
        else:
            self.tree.insert("", tk.END, iid=item_id, values=values)

        self.progress_bar.config(value=pct)
        self.status_lbl.config(text=f"[{task_name}] {msg}")
