"""autovsf_gui/app.py — Main AutoVSF Workstation Desktop Application."""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# Ensure package import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from autovsf_core.domain.crop import CropProfile
from autovsf_core.domain.job import Job
from autovsf_core.config.settings import settings
from autovsf_core.queue.manager import queue_manager

from autovsf_gui.components.crop_selector import CropSelectorWindow
from autovsf_gui.components.job_dashboard import JobDashboardView
from autovsf_gui.components.settings_view import SettingsView


class AutoVSFApp(tk.Tk):
    """AutoVSF Workstation Desktop Application Root Window."""

    def __init__(self):
        super().__init__()
        self.title("AutoVSF Workstation Platform v2.0")
        self.geometry("1100x700")
        self.configure(bg="#111111")

        self.selected_video_path = ""
        self.active_crop_profile = settings.get_crop_profile("default")

        # Top Title Header
        header = tk.Frame(self, bg="#222222", height=40)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="AutoVSF Workstation Platform",
            font=("Helvetica", 14, "bold"),
            fg="#00FFFF",
            bg="#222222",
        ).pack(side=tk.LEFT, padx=15, pady=8)

        # Tab Control
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Video & Crop Selection
        self.tab_process = tk.Frame(self.notebook, bg="#222222")
        self.notebook.add(self.tab_process, text=" Video & Subtitle Crop ")
        self._build_process_tab()

        # Tab 2: Queue Monitor
        self.tab_queue = JobDashboardView(self.notebook)
        self.notebook.add(self.tab_queue, text=" Queue & Worker Monitor ")

        # Tab 3: Settings
        self.tab_settings = SettingsView(self.notebook)
        self.notebook.add(self.tab_settings, text=" Settings ")

    def _build_process_tab(self):
        # Video File Selection
        f_file = tk.Frame(self.tab_process, bg="#222222")
        f_file.pack(fill=tk.X, padx=15, pady=15)

        tk.Label(f_file, text="Select Video File:", fg="#FFFFFF", bg="#222222", font=("Helvetica", 11, "bold")).pack(
            side=tk.LEFT, padx=5
        )
        self.video_var = tk.StringVar()
        tk.Entry(f_file, textvariable=self.video_var, font=("Consolas", 11)).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=8
        )
        ttk.Button(f_file, text="Browse Video...", command=self._browse_video).pack(side=tk.LEFT, padx=5)

        # Crop Profile Status & Launch Selector
        f_crop = tk.LabelFrame(
            self.tab_process, text=" Subtitle Crop Profile ", fg="#FFD700", bg="#222222", font=("Helvetica", 10, "bold")
        )
        f_crop.pack(fill=tk.X, padx=15, pady=10)

        self.crop_lbl = tk.Label(
            f_crop,
            text=f"Active Crop: {self.active_crop_profile.name} (Top: {self.active_crop_profile.top:.4f}, Bottom: {self.active_crop_profile.bottom:.4f})",
            fg="#00FF00",
            bg="#222222",
            font=("Consolas", 10),
        )
        self.crop_lbl.pack(side=tk.LEFT, padx=10, pady=10)

        ttk.Button(f_crop, text="Open Visual Crop Selector...", command=self._open_crop_selector).pack(
            side=tk.RIGHT, padx=10, pady=10
        )

        # Options & Translation
        f_opts = tk.Frame(self.tab_process, bg="#222222")
        f_opts.pack(fill=tk.X, padx=15, pady=10)

        self.trans_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            f_opts,
            text="Enable AI Subtitle Translation",
            variable=self.trans_var,
            fg="#FFFFFF",
            bg="#222222",
            selectcolor="#333333",
            font=("Helvetica", 10),
        ).pack(side=tk.LEFT, padx=5)

        # Enqueue Button
        btn_submit = tk.Button(
            self.tab_process,
            text="ENQUEUE PROCESSING JOB",
            font=("Helvetica", 12, "bold"),
            bg="#00AA00",
            fg="#FFFFFF",
            activebackground="#00DD00",
            command=self._enqueue_job,
        )
        btn_submit.pack(fill=tk.X, padx=15, pady=20)

    def _browse_video(self):
        f = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.mkv *.avi *.mov *.flv *.webm"), ("All Files", "*.*")],
        )
        if f:
            self.video_var.set(f)
            self.selected_video_path = f

    def _open_crop_selector(self):
        video = self.video_var.get().strip()
        if not video or not os.path.isfile(video):
            messagebox.showerror("Error", "Please select a valid video file first.")
            return

        def on_crop_confirm(crop: CropProfile):
            self.active_crop_profile = crop
            self.crop_lbl.config(
                text=f"Active Crop: {crop.name} (Top: {crop.top:.4f}, Bottom: {crop.bottom:.4f}, Left: {crop.left:.4f}, Right: {crop.right:.4f})"
            )

        CropSelectorWindow(self, video, on_crop_confirm)

    def _enqueue_job(self):
        video = self.video_var.get().strip()
        if not video or not os.path.isfile(video):
            messagebox.showerror("Error", "Please select a valid video file.")
            return

        job = Job(
            video_path=video,
            crop_profile=self.active_crop_profile,
            enable_translation=self.trans_var.get(),
        )

        job_id = queue_manager.enqueue_job(job)
        messagebox.showinfo("Success", f"Job {job_id} added to processing queue!")
        self.notebook.select(1)  # Switch to Queue tab


def main():
    app = AutoVSFApp()
    app.mainloop()


if __name__ == "__main__":
    main()
