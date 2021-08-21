
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

3. (as root) Set a static IP on the wireless device (`wlan0` in this case):

```bash
cat > /etc/systemd/network/20-wired.network <<EOF
[Match]
Name=wlan0

[Network]
Address=10.0.0.1/16
#Gateway=0.0.0.0
#DNS=0.0.0.0
EOF

systemctl restart systemd-networkd

```

3. (as root) Install `hostapd`: (https://wiki.archlinux.org/title/software_access_point)

```bash
pacman -S hostapd

cat > /etc/hostapd/hostapd.conf <<EOF
interface=wlan0

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
cat > /etc/systemd/system/pulseaudio.service <<EOF
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


4. Install `dnsmasq`:

```bash
pacman -S dnsmasq

# edit /etc/systemd/resolved.conf and change DNSStubListener=no
vim /etc/systemd/resolved.conf

cat > /etc/dnsmasq.conf <<EOF
interface=wlan0
dhcp-range=10.0.0.10,10.0.10.250,5m
# Set default gateway
dhcp-option=3,10.0.0.1
# Set DNS servers to announce
dhcp-option=6,10.0.0.1
log-queries
except-interface=lo
# Resolve every FQDN to ourselves
address=/#/10.0.0.1
EOF

# By default Arch uses systemd-resolved on :53 for DNS caching

systemctl enable --now dnsmasq.service

# Leases issued get stored in /var/lib/misc/dnsmasq.leases

```

5. Copy over script and service files:

`phone_detectinator.py` goes in `/opt/phone_detectinator.py`

`alarm.mp3` goes in `/opt/alarm.mp3`

`phone_detectinator.service` goes in `/etc/systemd/system/phone_detectinator.service`


```bash
# Start the code at boot and right now
systemctl enable --now phone_detectinator.service

```



# Getting regular LAN internet back

```bash
sudo systemctl stop dnsmasq.service ; sudo systemctl start systemd-resolved
# To reverse w/o a reboot
sudo systemctl stop systemd-resolved ; sudo systemctl start dnsmasq.service

```


