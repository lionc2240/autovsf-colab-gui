# AutoVSF Workstation Platform v2.0

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lionc2240/autovsf-colab-gui/blob/main/bootstrap/colab_bootstrap.ipynb)

> **Nền tảng bóc tách và dịch thuật phụ đề phim tự động thế hệ mới**  
> Tối ưu hóa cho môi trường Ubuntu Desktop (XFCE / LXQt + noVNC + Xvfb) chạy trực tiếp trên Google Colab.

---

## Tính năng nổi bật

- **Giao diện GUI Workstation trực quan**: Bộ chọn vùng crop phụ đề cho phép kéo thả 4 đường kẻ trực tiếp trên khung hình video, tua frame theo thời gian thực và quản lý hồ sơ (profile) crop.
- **Kiến trúc mô-đun hóa độc lập**: Thư viện Python `autovsf_core` xử lý tiến trình VideoSubFinder, Google Drive OCR và dịch phụ đề AI độc lập hoàn toàn với giao diện đồ họa.
- **Quản lý hàng chờ đa video (Multi-Video Queue)**: Trình quản lý `QueueManager` và luồng chạy ngầm `JobWorker` cho phép đưa nhiều video vào hàng chờ xử lý liên hoàn.
- **Theo dõi tiến độ thời gian thực**: Đếm số lượng ảnh trích xuất (`Watchdog`), cập nhật tiến độ theo %, hiển thị chi tiết thời gian hoàn thành dự kiến (ETA).
- **Bootstrap tinh gọn & tự động 100%**: Notebook Colab 3 cell (`bootstrap/colab_bootstrap.ipynb`) tự động cài đặt môi trường và mở Web Desktop mà không yêu cầu tương tác thủ công.

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
│   ├── engine/                  # Động cơ VSF, Drive OCR, AI Translation
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
3. Chạy **Bước 2** để cài đặt môi trường Ubuntu Desktop & phụ thuộc.
4. Chạy **Bước 3** để khởi chạy Web Desktop. Mở đường link `noVNC` được in ra ở cuối cell để truy cập ứng dụng AutoVSF!

---

## Mở lại ứng dụng khi lỡ đóng

- **Trường hợp đóng tab trình duyệt noVNC:** Nhấp lại vào đường link `noVNC` ở Bước 3 trong Colab để mở lại giao diện.
- **Trường hợp đóng cửa sổ ứng dụng AutoVSF:** Mở **Terminal** trong màn hình Desktop noVNC và gõ:
  ```bash
  python3 -m autovsf_gui.app
  ```
