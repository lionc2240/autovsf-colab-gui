"""autovsf_gui/components/settings_view.py — Configuration & Credentials Settings Widget."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from autovsf_core.config.settings import settings


class SettingsView(tk.Frame):
    """GUI Frame for managing settings.json, VSF path, and OAuth credentials."""

    def __init__(self, master: tk.Widget):
        super().__init__(master, bg="#222222")

        lbl = tk.Label(
            self, text="⚙️ AutoVSF Settings & Configuration", font=("Helvetica", 12, "bold"), fg="#FFD700", bg="#222222"
        )
        lbl.pack(anchor=tk.W, padx=10, pady=5)

        # Credentials Path
        f1 = tk.Frame(self, bg="#222222")
        f1.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(f1, text="Credentials JSON:", fg="#FFFFFF", bg="#222222", width=18, anchor=tk.W).pack(side=tk.LEFT)
        self.cred_var = tk.StringVar(value=settings.data.get("credentials_file", ""))
        tk.Entry(f1, textvariable=self.cred_var, font=("Consolas", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(f1, text="Browse...", command=self._browse_cred).pack(side=tk.LEFT)

        # VSF Path
        f2 = tk.Frame(self, bg="#222222")
        f2.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(f2, text="VideoSubFinder Binary:", fg="#FFFFFF", bg="#222222", width=18, anchor=tk.W).pack(
            side=tk.LEFT
        )
        self.vsf_var = tk.StringVar(value=settings.data.get("vsf_path", ""))
        tk.Entry(f2, textvariable=self.vsf_var, font=("Consolas", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(f2, text="Browse...", command=self._browse_vsf).pack(side=tk.LEFT)

        # Folder ID
        f3 = tk.Frame(self, bg="#222222")
        f3.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(f3, text="Drive Folder ID (Opt):", fg="#FFFFFF", bg="#222222", width=18, anchor=tk.W).pack(
            side=tk.LEFT
        )
        self.folder_var = tk.StringVar(value=settings.data.get("folder_id", ""))
        tk.Entry(f3, textvariable=self.folder_var, font=("Consolas", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Button(self, text="💾 Save Settings", command=self._save).pack(anchor=tk.E, padx=10, pady=15)

    def _browse_cred(self):
        f = filedialog.askopenfilename(title="Select credentials.json", filetypes=[("JSON Files", "*.json")])
        if f:
            self.cred_var.set(f)

    def _browse_vsf(self):
        f = filedialog.askopenfilename(title="Select VideoSubFinder Executable")
        if f:
            self.vsf_var.set(f)

    def _save(self):
        settings.data["credentials_file"] = self.cred_var.get().strip()
        settings.data["vsf_path"] = self.vsf_var.get().strip()
        settings.data["folder_id"] = self.folder_var.get().strip()
        settings.save()
        messagebox.showinfo("Saved", "Settings saved successfully!")
