# AutoVSF Workstation Platform v2.0

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lionc2240/autovsf-colab-gui/blob/main/bootstrap/colab_bootstrap.ipynb)

> **Nền tảng bóc tách và dịch thuật phụ đề phim tự động thế hệ mới**  
> Tối ưu hóa cho môi trường Ubuntu Desktop (XFCE / LXQt + noVNC + Xvfb) chạy trực tiếp trên Google Colab.

---

## Tính năng nổi bật

- **Giải phóng Cell ngầm (Non-blocking Bootstrap)**: Cài đặt môi trường ngầm giải phóng ô Cell 2 trong < 2 giây.
- **Tải ngầm YouTube đa luồng (`yt-dlp Engine`)**: Tự động tải ngầm các video với chất lượng tối thiểu 720p và giữ nguyên tiêu đề video gốc (`%(title)s.%(ext)s`).
- **2 Cổng kết nối trực quan (2 Workspace Portals)**: Xuất 2 đường link trực tiếp trên Colab (`Terminal WebUI - ttyd` và `Desktop GUI - noVNC`).
- **Tích hợp YouTube linh hoạt ở 2 nơi (Dual-Integration)**: Nhập link YouTube trực tiếp trên Cell Notebook (Bước 4) hoặc dán link trên ứng dụng Desktop GUI.
- **Giao diện GUI Workstation trực quan**: Bộ chọn vùng crop phụ đề kéo thả 4 đường kẻ màu trên khung hình video, tua frame theo thời gian thực và quản lý crop profile.
- **Quản lý hàng chờ đa video (Multi-Video Queue)**: `QueueManager` và luồng chạy ngầm `JobWorker` xử lý nhiều video song song hoặc nối tiếp tự động.

---

## Cấu trúc thư mục dự án

```
autovsf-colab-gui/
├── bootstrap/                   # Tầng khởi tạo hệ thống
│   ├── AutoVSF.desktop          # File lối tắt ứng dụng trên Desktop
│   ├── colab_bootstrap.ipynb    # Notebook khởi chạy Colab
│   └── setup_environment.sh     # Script cài đặt môi trường tự động
│
├── autovsf_core/                # Thư viện lõi xử lý độc lập
│   ├── config/                  # Quản lý cài đặt & phát hiện môi trường
│   ├── domain/                  # Models (Job, CropProfile, Status)
│   ├── engine/                  # Động cơ VSF, Drive OCR, AI Translation, YouTube Downloader
│   ├── pipeline/                # Định nghĩa Task và luồng Pipeline
│   └── queue/                   # Hàng chờ QueueManager & Worker Pool
│
├── autovsf_gui/                 # Tầng giao diện đồ họa Desktop
│   ├── app.py                   # Điểm khởi chạy ứng dụng GUI chính
│   └── components/              # Các widget (CropSelector, Dashboard, Settings)
│
├── requirements.txt
└── README.md
```

---

## Hướng dẫn nhanh trên Google Colab

1. Nhấp vào nút **Open in Colab** ở trên hoặc mở file [`bootstrap/colab_bootstrap.ipynb`](https://colab.research.google.com/github/lionc2240/autovsf-colab-gui/blob/main/bootstrap/colab_bootstrap.ipynb) trong Google Colab.
2. Chạy **Bước 1** để kết nối với Google Drive.
3. Chạy **Bước 2** để khởi tạo cài đặt môi trường ngầm (Cell giải phóng ngay trong 2s).
4. Chạy **Bước 3** để bật 2 Cổng kết nối:
   - **LINK 1 [TERMINAL WEBUI (ttyd)]**: Cửa sổ dòng lệnh Linux trên Web.
   - **LINK 2 [DESKTOP GUI (noVNC)]**: Màn hình Ubuntu Desktop với ứng dụng AutoVSF.
5. *(Tùy chọn)* Chạy **Bước 4** nếu muốn dán link YouTube và tự động xử lý ngầm trực tiếp trên Cell.

---

## Mở lại ứng dụng khi lỡ đóng

- **Trường hợp đóng tab trình duyệt noVNC:** Nhấp lại vào đường link `noVNC` ở Bước 3 trong Colab để mở lại giao diện.
- **Trường hợp đóng cửa sổ ứng dụng AutoVSF:** Mở **Terminal** trong màn hình Desktop noVNC và gõ:
  ```bash
  python3 -m autovsf_gui.app
  ```
