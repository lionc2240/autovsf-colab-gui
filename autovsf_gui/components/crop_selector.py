"""autovsf_gui/components/crop_selector.py — Interactive Video Crop Selector Component."""

import os
import cv2
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from typing import Callable, Optional

from autovsf_core.domain.crop import CropProfile
from autovsf_core.config.settings import settings


class CropSelectorWindow:
    """Interactive Tkinter window allowing visual line dragging over video frames to generate CropProfile."""

    SNAP_DISTANCE = 10  # Canvas pixel threshold for line dragging

    def __init__(self, master: tk.Tk, video_path: str, on_confirm_callback: Callable[[CropProfile], None]):
        self.video_path = video_path
        self.on_confirm = on_confirm_callback

        self.cap: Optional[cv2.VideoCapture] = None
        self.photo: Optional[ImageTk.PhotoImage] = None
        self.current_frame = 0
        self.total_frames = 0
        self.vw = self.vh = 0
        self.dw = self.dh = 0
        self.ox = self.oy = 0

        # Subtitle crop lines (in video pixel coordinates)
        self.top_y = 0
        self.bottom_y = 0
        self.left_x = 0
        self.right_x = 0
        self.dragging = None

        self.win = tk.Toplevel(master)
        self.win.title("✨ AutoVSF — Interactive Crop Selector")
        self.win.geometry("1000x760")

        # Main Canvas
        self.canvas = tk.Canvas(self.win, bg="#111111", cursor="arrow")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Motion>", self._on_hover)
        self.canvas.bind("<Configure>", lambda e: self._show_frame())

        # Parameters & Profile Save Bar
        pbar = tk.Frame(self.win, bg="#222222")
        pbar.pack(fill=tk.X, pady=2)

        self.top_var = tk.StringVar()
        self.bottom_var = tk.StringVar()
        self.left_var = tk.StringVar()
        self.right_var = tk.StringVar()

        for label, var, color in (
            ("Top", self.top_var, "#FFD700"),
            ("Bottom", self.bottom_var, "#00FFFF"),
            ("Left", self.left_var, "#00FF00"),
            ("Right", self.right_var, "#00FF00"),
        ):
            tk.Label(pbar, text=f"{label}:", fg=color, bg="#222222", font=("Consolas", 10, "bold")).pack(
                side=tk.LEFT, padx=4
            )
            tk.Entry(
                pbar,
                textvariable=var,
                width=8,
                state="readonly",
                font=("Consolas", 10, "bold"),
                bg="#333333",
                fg=color,
            ).pack(side=tk.LEFT, padx=1)

        ttk.Button(pbar, text="✅ Confirm & Save Crop", command=self._confirm).pack(side=tk.LEFT, padx=14)

        # Profile Saving Input
        tk.Label(pbar, text="Profile Name:", fg="#AAAAAA", bg="#222222", font=("Helvetica", 9)).pack(
            side=tk.LEFT, padx=(4, 2)
        )
        self.profile_name_var = tk.StringVar(value="custom")
        tk.Entry(pbar, textvariable=self.profile_name_var, width=12, font=("Consolas", 10)).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(pbar, text="💾 Save Profile", command=self._save_profile).pack(side=tk.LEFT, padx=4)

        # Video Frame Timeline Control Bar
        tbar = tk.Frame(self.win)
        tbar.pack(fill=tk.X, pady=2)
        self.slider = ttk.Scale(tbar, orient="horizontal", command=self._on_seek)
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.time_lbl = tk.Label(tbar, text="00:00:00.000", font=("Consolas", 10))
        self.time_lbl.pack(side=tk.LEFT, padx=4)
        ttk.Button(tbar, text="▶▶ +1s", width=7, command=self._seek_plus_1s).pack(side=tk.LEFT, padx=4)

        self.win.after(50, self._load_video)

    def _load_video(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            messagebox.showerror("Error", f"Failed to open video:\n{self.video_path}")
            self.win.destroy()
            return

        self.vw = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.vh = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.slider.config(to=max(1, self.total_frames - 1))

        # Default initial crop (bottom 25% of frame)
        prof = settings.get_crop_profile("default")
        self.top_y = int((1.0 - prof.top) * self.vh)
        self.bottom_y = int((1.0 - prof.bottom) * self.vh)
        self.left_x = int(prof.left * self.vw)
        self.right_x = int(prof.right * self.vw)

        self._show_frame()

    def _show_frame(self):
        if not self.cap or not self.cap.isOpened() or not self.vw:
            return
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()
        if not ret:
            return

        self.win.update_idletasks()
        cw = max(self.canvas.winfo_width(), 400)
        ch = max(self.canvas.winfo_height(), 300)

        scale = min(cw / self.vw, ch / self.vh)
        self.dw = int(self.vw * scale)
        self.dh = int(self.vh * scale)
        self.ox = (cw - self.dw) // 2
        self.oy = (ch - self.dh) // 2

        resized = cv2.resize(frame, (self.dw, self.dh))
        img = Image.fromarray(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
        bg = Image.new("RGB", (cw, ch), (17, 17, 17))
        bg.paste(img, (self.ox, self.oy))
        self.photo = ImageTk.PhotoImage(bg)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self._draw_overlay()
        self._update_labels()

    def _draw_overlay(self):
        if not self.dw or not self.vw:
            return
        sx = self.dw / self.vw
        sy = self.dh / self.vh

        cy_top = self.oy + int(self.top_y * sy)
        cy_bot = self.oy + int(self.bottom_y * sy)
        cx_left = self.ox + int(self.left_x * sx)
        cx_right = self.ox + int(self.right_x * sx)

        x0, x1 = self.ox, self.ox + self.dw
        y0, y1 = self.oy, self.oy + self.dh

        # Dimmed area outside subtitle region
        mask_color = "#1A1A3A"
        kw = dict(tags="overlay")
        self.canvas.create_rectangle(x0, y0, x1, cy_top, fill=mask_color, outline="", **kw)
        self.canvas.create_rectangle(x0, cy_bot, x1, y1, fill=mask_color, outline="", **kw)
        self.canvas.create_rectangle(x0, cy_top, cx_left, cy_bot, fill=mask_color, outline="", **kw)
        self.canvas.create_rectangle(cx_right, cy_top, x1, cy_bot, fill=mask_color, outline="", **kw)

        # 4 Draggable Lines
        self.canvas.create_line(x0, cy_top, x1, cy_top, fill="#FFD700", width=2, **kw)
        self.canvas.create_line(x0, cy_bot, x1, cy_bot, fill="#00FFFF", width=2, **kw)
        self.canvas.create_line(cx_left, y0, cx_left, y1, fill="#00FF00", width=2, **kw)
        self.canvas.create_line(cx_right, y0, cx_right, y1, fill="#00FF00", width=2, **kw)

    def _update_labels(self):
        prof = CropProfile.from_pixel_box(
            self.left_x, self.top_y, self.right_x, self.bottom_y, self.vw, self.vh
        )
        self.top_var.set(f"{prof.top:.4f}")
        self.bottom_var.set(f"{prof.bottom:.4f}")
        self.left_var.set(f"{prof.left:.4f}")
        self.right_var.set(f"{prof.right:.4f}")

    def _on_press(self, event):
        if not self.dw:
            return
        sy = self.dh / self.vh
        sx = self.dw / self.vw

        cy_top = self.oy + int(self.top_y * sy)
        cy_bot = self.oy + int(self.bottom_y * sy)
        cx_left = self.ox + int(self.left_x * sx)
        cx_right = self.ox + int(self.right_x * sx)

        t = self.SNAP_DISTANCE
        if abs(event.y - cy_top) < t:
            self.dragging = "top"
        elif abs(event.y - cy_bot) < t:
            self.dragging = "bottom"
        elif abs(event.x - cx_left) < t:
            self.dragging = "left"
        elif abs(event.x - cx_right) < t:
            self.dragging = "right"

    def _on_drag(self, event):
        if not self.dragging or not self.dh:
            return
        vy = int((event.y - self.oy) * self.vh / self.dh)
        vx = int((event.x - self.ox) * self.vw / self.dw)

        if self.dragging == "top":
            self.top_y = max(0, min(vy, self.bottom_y - 10))
        elif self.dragging == "bottom":
            self.bottom_y = min(self.vh, max(vy, self.top_y + 10))
        elif self.dragging == "left":
            self.left_x = max(0, min(vx, self.right_x - 10))
        elif self.dragging == "right":
            self.right_x = min(self.vw, max(vx, self.left_x + 10))

        self._show_frame()

    def _on_release(self, event):
        self.dragging = None

    def _on_hover(self, event):
        pass

    def _on_seek(self, val):
        self.current_frame = int(float(val))
        self._show_frame()

    def _seek_plus_1s(self):
        fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
        self.current_frame = min(self.total_frames - 1, self.current_frame + int(fps))
        self.slider.set(self.current_frame)
        self._show_frame()

    def _confirm(self):
        prof = CropProfile.from_pixel_box(
            self.left_x, self.top_y, self.right_x, self.bottom_y, self.vw, self.vh, name=self.profile_name_var.get()
        )
        if self.on_confirm:
            self.on_confirm(prof)
        self.win.destroy()

    def _save_profile(self):
        prof = CropProfile.from_pixel_box(
            self.left_x, self.top_y, self.right_x, self.bottom_y, self.vw, self.vh, name=self.profile_name_var.get()
        )
        settings.save_crop_profile(prof)
        messagebox.showinfo("Saved", f"Profile '{prof.name}' saved successfully!")
