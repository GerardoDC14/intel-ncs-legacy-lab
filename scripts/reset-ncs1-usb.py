#!/usr/bin/env python3
"""Reset only an idle Movidius NCS1 USB device; does not power-cycle VBUS."""
import fcntl
import os
import stat
import time
from pathlib import Path

if os.geteuid() != 0:
    raise SystemExit('Run with sudo; close the viewer and any inference process first.')
devices=[];vpu_count=0
for entry in Path('/sys/bus/usb/devices').iterdir():
    try:
        if (entry/'idVendor').read_text().strip() != '03e7':continue
        vpu_count+=1
        product=(entry/'idProduct').read_text().strip()
        if product not in ('2150','f63b'):continue
        node=Path('/dev/bus/usb/%03d/%03d' % (int((entry/'busnum').read_text()),int((entry/'devnum').read_text())))
        devices.append((entry,node))
    except (FileNotFoundError,ValueError):continue
if len(devices)!=1 or vpu_count!=1:raise SystemExit('Expected exactly one NCS1 (2150/f63b); found %d. Booted f63b IDs can also belong to other Movidius products; disconnect other VPUs first.' % len(devices))
entry,node=devices[0]
# Refuse reset while another process has this USB node open.
device_id=node.stat().st_rdev
for proc in Path('/proc').iterdir():
    if not proc.name.isdigit() or int(proc.name)==os.getpid():continue
    try:
        for fd in (proc/'fd').iterdir():
            try:
                info=fd.stat()
                if stat.S_ISCHR(info.st_mode) and info.st_rdev==device_id:
                    raise SystemExit('USB device is in use by PID %s. Close the inference process first.' % proc.name)
            except (FileNotFoundError,PermissionError):pass
    except (FileNotFoundError,PermissionError,ProcessLookupError):pass
print('USB bus reset:',entry.name,str(node),flush=True)
with node.open('wb',buffering=0) as handle:fcntl.ioctl(handle,0x5514,0)  # USBDEVFS_RESET, Linux usbdevice_fs.h
time.sleep(2)
print('Reset requested. This does not cut USB power; inference must be checked separately.')
