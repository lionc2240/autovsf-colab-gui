"""autovsf_core/engine/ocr/drive_ocr.py — Google Drive OCR Engine Implementation."""

import io
import re
import os
import time
import shutil
import datetime
import threading
from pathlib import Path
import concurrent.futures
from typing import Callable, Optional, Dict, List

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from autovsf_core.engine.ocr.ocr_base import BaseOCREngine
from autovsf_core.config.settings import settings
from autovsf_core.config.environment import env

SCOPES = ["https://www.googleapis.com/auth/drive"]


class GoogleDriveAuth:
    """Handles Google Drive API OAuth credentials token refresh and flow."""

    @staticmethod
    def get_credentials() -> Credentials:
        cred_file = settings.data.get("credentials_file", str(env.work_dir / "credentials.json"))
        tok_file = settings.data.get("token_file", str(env.work_dir / "token.json"))

        if not os.path.exists(cred_file):
            raise FileNotFoundError(f"Google Drive credentials file missing at: {cred_file}")

        creds = None
        if os.path.exists(tok_file):
            try:
                creds = Credentials.from_authorized_user_file(tok_file, SCOPES)
            except Exception:
                creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
                flow = InstalledAppFlow.from_client_secrets_file(
                    cred_file, scopes=SCOPES, redirect_uri="http://localhost:8080/"
                )
                auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
                print(f"Auth URL: {auth_url}")
                response_url = input("Paste OAuth Redirect URL here: ").strip()
                flow.fetch_token(authorization_response=response_url)
                creds = flow.credentials

            os.makedirs(os.path.dirname(tok_file), exist_ok=True)
            with open(tok_file, "w") as token:
                token.write(creds.to_json())

        return creds


class GoogleDriveOCREngine(BaseOCREngine):
    """Google Drive Document OCR Implementation."""

    def __init__(self, threads: int = 20):
        self.threads = threads
        self._local = threading.local()
        self.creds = None

    def _get_service(self):
        if not hasattr(self._local, "svc"):
            if not self.creds:
                self.creds = GoogleDriveAuth.get_credentials()
            self._local.svc = build("drive", "v3", credentials=self.creds)
        return self._local.svc

    def _ocr_single_image(self, img_path: str, img_name: str, folder_id: str) -> str:
        svc = self._get_service()
        mime = "application/vnd.google-apps.document"
        body = {"name": img_name, "mimeType": mime}
        if folder_id:
            body["parents"] = [folder_id]

        f = svc.files().create(
            body=body, media_body=MediaFileUpload(img_path, mimetype="image/jpeg", resumable=False)
        ).execute()

        file_id = f["id"]

        try:
            req = svc.files().export_media(fileId=file_id, mimeType="text/plain")
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, req)
            done = False
            while not done:
                _, done = downloader.next_chunk()

            content = fh.getvalue().decode("utf-8-sig", errors="ignore").strip()
        finally:
            svc.files().delete(fileId=file_id).execute()

        return content

    def run_ocr(
        self,
        images_dir: str,
        output_srt_path: str,
        progress_cb: Optional[Callable[[int, int, str], None]] = None,
    ) -> str:
        if not os.path.exists(images_dir):
            raise FileNotFoundError(f"RGBImages directory not found: {images_dir}")

        image_files = sorted(
            [f for f in os.listdir(images_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))]
        )

        total_images = len(image_files)
        if total_images == 0:
            raise ValueError(f"No subtitle images found in {images_dir}")

        folder_id = settings.data.get("folder_id", "").strip()

        entries: Dict[int, list] = {}
        entries_lock = threading.Lock()
        done_counter = 0

        # Pattern for timestamp filenames: HH_MM_SS_MS__HH_MM_SS_MS
        fn_pattern = re.compile(
            r"^(\d{1,2})_(\d{2})_(\d{2})_(\d+)__(\d{1,2})_(\d{2})_(\d{2})_(\d+)"
        )

        def worker(idx: int, fname: str):
            nonlocal done_counter
            full_path = os.path.join(images_dir, fname)
            m = fn_pattern.match(fname)
            if not m:
                return

            start_str = f"{int(m[1]):02d}:{int(m[2]):02d}:{int(m[3]):02d},{int(m[4][:3]):03d}"
            end_str = f"{int(m[5]):02d}:{int(m[6]):02d}:{int(m[7]):02d},{int(m[8][:3]):03d}"

            text = self._ocr_single_image(full_path, fname, folder_id)

            with entries_lock:
                entries[idx] = [start_str, end_str, text]
                done_counter += 1
                if progress_cb:
                    progress_cb(done_counter, total_images, f"OCR: {done_counter}/{total_images}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(worker, i, fname) for i, fname in enumerate(image_files)]
            concurrent.futures.wait(futures)

        # Reassemble into SRT format
        os.makedirs(os.path.dirname(os.path.abspath(output_srt_path)), exist_ok=True)
        with open(output_srt_path, "w", encoding="utf-8") as f:
            srt_index = 1
            for idx in sorted(entries.keys()):
                start_time, end_time, text = entries[idx]
                if text:
                    f.write(f"{srt_index}\n{start_time} --> {end_time}\n{text}\n\n")
                    srt_index += 1

        return output_srt_path
