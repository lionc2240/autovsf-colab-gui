#!/bin/bash
# setup_environment.sh — AutoVSF Workstation System & Environment Installer
export DEBIAN_FRONTEND=noninteractive
export TZ=Etc/UTC

# Pre-select English (US) keyboard layout for debconf
echo "keyboard-configuration keyboard-configuration/layoutcode string us" | sudo debconf-set-selections 2>/dev/null || true
echo "keyboard-configuration keyboard-configuration/modelcode string pc105" | sudo debconf-set-selections 2>/dev/null || true

echo -e "${CYAN}[1/5] Updating package list & installing XFCE / ttyd / tmux / xclip / noVNC desktop dependencies...${NC}"
sudo apt-get update -qq -y || true
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -q -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
    xvfb xfce4 xfce4-goodies x11vnc novnc net-tools ttyd tmux xclip \
    ffmpeg libxss1 libnss3 libxtst6 libxrender1 libxcomposite1 \
    libasound2 libdbus-glib-1-2 libnuma1 libgtk-3-0 python3-tk python3-pip

echo -e "${CYAN}[2/5] Setting up Python dependencies & yt-dlp...${NC}"
pip install --quiet --no-cache-dir \
    watchdog google-api-python-client google-auth-oauthlib google-auth \
    httplib2 opencv-python psutil Pillow gradio requests yt-dlp ipywidgets

echo -e "${CYAN}[3/5] Setting up VideoSubFinder & Legacy Libraries...${NC}"
WORKDIR="/content/drive/MyDrive/AutoVSF"
if [ ! -d "$WORKDIR" ]; then
    WORKDIR="$HOME/AutoVSF"
fi
mkdir -p "$WORKDIR/VideoSubFinder/legacy_libs"

VSF_DIR="$WORKDIR/VideoSubFinder"
LIBS_DIR="$VSF_DIR/legacy_libs"

if [ ! -f "$LIBS_DIR/.libs_ready" ]; then
    echo -e "${YELLOW}[DOWNLOAD] Downloading Ubuntu legacy compatibility libraries...${NC}"
    cd "$LIBS_DIR"
    declare -A DEBS=(
        ["libaom0"]="https://archive.ubuntu.com/ubuntu/pool/universe/a/aom/libaom0_1.0.0.errata1-3build1_amd64.deb"
        ["libvpx6"]="http://azure.archive.ubuntu.com/ubuntu/pool/main/libv/libvpx/libvpx6_1.8.2-1ubuntu0.4_amd64.deb"
        ["libx264-155"]="https://old-releases.ubuntu.com/ubuntu/pool/universe/x/x264/libx264-155_0.155.2917+git0a84d98-2_amd64.deb"
        ["libx265-179"]="http://ftp.ubuntu.com/ubuntu/ubuntu/pool/universe/x/x265/libx265-179_3.2.1-1build1_amd64.deb"
    )
    for pkg in "${!DEBS[@]}"; do
        curl -sL -o "$pkg.deb" "${DEBS[$pkg]}" || true
        dpkg -x "$pkg.deb" . || true
        find usr/lib/x86_64-linux-gnu/ -name "*.so*" -exec mv {} . \; 2>/dev/null || true
        rm -rf usr/ "$pkg.deb"
    done
    touch .libs_ready
fi

VSF_LINK="https://github.com/lionc2240/autovsf-codespaces/releases/download/VideoSubFinder_6.10_ubu20.04.tar.xz/VideoSubFinder_6.10_ubu20.04.tar.xz"
if [ ! -f "$VSF_DIR/VideoSubFinderWXW" ]; then
    echo -e "${YELLOW}[DOWNLOAD] Downloading VideoSubFinder binary...${NC}"
    curl -sL -o "$WORKDIR/vsf.tar.xz" "$VSF_LINK"
    tar -xf "$WORKDIR/vsf.tar.xz" -C "$WORKDIR/"
    rm -f "$WORKDIR/vsf.tar.xz"
fi

cat <<EOF > "$VSF_DIR/VideoSubFinderWXW.run"
#!/bin/bash
export LD_LIBRARY_PATH="$LIBS_DIR:\$PWD:\$LD_LIBRARY_PATH"
if [ -z "\$DISPLAY" ]; then
    xvfb-run -a ./VideoSubFinderWXW "\$@"
else
    ./VideoSubFinderWXW "\$@"
fi
EOF

chmod +x "$VSF_DIR/VideoSubFinderWXW" "$VSF_DIR/VideoSubFinderWXW.run" 2>/dev/null || true

echo -e "${CYAN}[4/5] Installing AutoVSF Desktop Shortcut...${NC}"
mkdir -p "$HOME/Desktop" /usr/share/applications/ 2>/dev/null || true
if [ -f "bootstrap/AutoVSF.desktop" ]; then
    cp "bootstrap/AutoVSF.desktop" "$HOME/Desktop/AutoVSF.desktop"
    sudo cp "bootstrap/AutoVSF.desktop" "/usr/share/applications/AutoVSF.desktop" 2>/dev/null || true
    chmod +x "$HOME/Desktop/AutoVSF.desktop" 2>/dev/null || true
fi

echo -e "${GREEN}==========================================================="
echo -e "[SUCCESS] AutoVSF Workstation Environment Setup Complete!"
echo -e "===========================================================${NC}"
