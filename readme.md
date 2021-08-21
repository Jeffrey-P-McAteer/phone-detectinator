
# Phone Detectinator

This repository holds scripts and config files deployable on
any computer with the following hardware:

 - WiFi chip with AP support
 - Audible Speakers (not headphones)

and the following software:

 - TODO document our hard dependencies (probably `systemd`)

# Setup Guides

Each of the following sections is specific to one tested hardware configuration,
and will likely work fine on similar hardware (eg substitute rpi3 for rpi4 changes nothing).

## Setup for Rasperry Pi 3 model B:


1. Deploy Arch Linux on the Pi: https://archlinuxarm.org/platforms/armv8/broadcom/raspberry-pi-3
    - Alternatively: https://github.com/andrewboring/alarm-images
    - If you use an image remember to increase the root partition to use the entire disk: https://access.redhat.com/articles/1190213
    - Also ensure the `boot` partition has at least 200mb free space for kernel updates.

2. (as root) Update SW and install common tools we expect everywhere:

```bash
pacman-key --init
pacman-key --populate archlinuxarm
pacman -Syu
pacman -S sudo vim python

```

3. (as root) Install `hostapd`: (https://wiki.archlinux.org/title/software_access_point)

```bash
pacman -S hostapd

cat > /etc/hostapd/hostapd.conf <<EOF
interface=wlan0_ap
bridge=br0

# SSID to be used in IEEE 802.11 management frames
ssid=JWAC_Phone_Detectinator
# Driver interface type (hostap/wired/none/nl80211/bsd)
driver=nl80211
# Country code (ISO/IEC 3166-1)
country_code=US

# Operation mode (a = IEEE 802.11a (5 GHz), b = IEEE 802.11b (2.4 GHz)
hw_mode=g
# Channel number
channel=7
# Maximum number of stations allowed
max_num_sta=5

# hostapd event logger configuration
logger_stdout=-1
logger_stdout_level=2

EOF

sudo systemctl enable --now hostapd.service

```

4. Install `pulseaudio`:

```bash
sudo pacman -S pulseaudio

# https://wiki.archlinux.org/title/PulseAudio#Starting_system-wide_on_boot
cat > /etc/systemd/system <<EOF
[Unit]
Description=Sound Service

[Service]
# Note that notify will only work if --daemonize=no
Type=notify
ExecStart=/usr/bin/pulseaudio --daemonize=no --exit-idle-time=-1 --disallow-exit=true
Restart=always

[Install]
WantedBy=default.target
EOF

systemctl enable --now pulseaudio
systemctl --global mask pulseaudio.socket


```







