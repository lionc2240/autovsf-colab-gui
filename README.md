# AutoVSF Workstation Platform v2.0

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lionc2240/autovsf-colab-gui/blob/main/bootstrap/colab_bootstrap.ipynb)

> **Next-Generation Subtitle Extraction & AI Translation Platform**  
> Optimized for Ubuntu Desktop (XFCE / LXQt + noVNC + Xvfb) inside Google Colab.

---

## Key Features

- **GUI-First Workstation Experience**: Interactive video crop selector with visual draggable overlay lines, frame timeline seeking, and crop profile management.
- **Decoupled Architecture**: `autovsf_core` python library handles pipeline execution, VSF runner, Drive OCR, and AI subtitle translation independently from UI.
- **Multi-Video Queue & Worker Pool**: Thread-safe `QueueManager` & background `JobWorker` pool process multiple queued video jobs asynchronously.
- **Real-time Monitoring**: Frame-by-frame progress, Watchdog image count tracker, and ETA calculations.
- **Minimal Notebook Bootstrap**: Clean 3-cell Colab notebook (`bootstrap/colab_bootstrap.ipynb`) that initializes XFCE/LXQt/noVNC and launches the workstation app.

---

## Project Architecture

```
autovsf-colab-gui/
├── bootstrap/                   # Bootstrap Layer
│   ├── AutoVSF.desktop          # Desktop shortcut launcher
│   ├── colab_bootstrap.ipynb    # Launcher notebook
│   └── setup_environment.sh     # Dependencies installer
│
├── autovsf_core/                # Independent Core Engine Library
│   ├── config/                  # Settings & environment detection
│   ├── domain/                  # Job, CropProfile, Status models
│   ├── engine/                  # VSF, OCR, Translation engines
│   ├── pipeline/                # Task definitions & pipeline runner
│   └── queue/                   # QueueManager & Worker pool
│
├── autovsf_gui/                 # Desktop Application Layer
│   ├── app.py                   # Main Desktop Application Entry Point
│   └── components/              # Interactive CropSelector, Dashboard, Settings UI
│
├── requirements.txt
└── README.md
```

---

## Quick Start on Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lionc2240/autovsf-colab-gui/blob/main/bootstrap/colab_bootstrap.ipynb)

1. Click the Colab logo above to open `bootstrap/colab_bootstrap.ipynb` in Google Colab.
2. Run **Step 1** to mount Google Drive.
3. Run **Step 2** to install system dependencies.
4. Run **Step 3** to launch the Ubuntu Workstation. Open the printed `noVNC` URL to access the AutoVSF Desktop Application!
