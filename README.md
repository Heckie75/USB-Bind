# USB-Bind
A tool that makes binding of USB devices easy and prints details in json format.

## Command
```
A tool that makes binding of USB devices easy.
Version: 0.1.0 (2022-10-09)

usage: usbbind.py [-h] [--json] [--version] [--bind BIND] [--unbind UNBIND] [--rebind REBIND] [--device DEVICE] [--sleep SLEEP]

options:
  -h, --help       show this help message and exit
  --json           prints usb details in json format
  --version        print version
  --bind BIND      bind usb device given as path, e.g. 1-2.3
  --unbind UNBIND  unbind usb device given as path, e.g. 1-2.3, or vendorID:productID, e.g. 0ccd:0077
  --rebind REBIND  rebind usb device given as path, e.g. 1-2.3, or vendorID:productID, e.g. 0ccd:0077
  --device DEVICE  prints details of usb device given as path, e.g. 1-2.3, or vendorID:productID, e.g. 0ccd:0077, in json format
```

## Examples

### Dump your USB devices in JSON format

```
$ ./usbbind.py
[
  {
    "bus": 4,
    "device": 1,
    "vendor": "1d6b",
    "product": "0003",
    "name": "Linux Foundation 3.0 root hub",
    "path": "4",
    "port": 1,
    "class": "root_hub",
    "driver": "xhci_hcd/2p",
    "speed": 10000
  },
  {
    "bus": 3,
    "device": 1,
    "vendor": "1d6b",
    "product": "0002",
    "name": "Linux Foundation 2.0 root hub",
    "path": "3",
    "port": 1,
    "class": "root_hub",
    "driver": "xhci_hcd/2p",
    "speed": 480
  },
// ...
  {
    "bus": 1,
    "device": 51,
    "vendor": "0ccd",
    "product": "0077",
    "name": "TerraTec Electronic GmbH Aureon Dual USB",
    "path": "1-4.1.3",
    "port": 3,
    "class": "Audio",
    "driver": "snd-usb-audio",
    "speed": 12,
    "interface": 1
  }
]
```

### Request device information

By vendorID and productID
```
$ ./usbbind.py --device 0ccd:0077
[
  {
    "bus": 1,
    "device": 51,
    "vendor": "0ccd",
    "product": "0077",
    "name": "TerraTec Electronic GmbH Aureon Dual USB",
    "path": "1-4.1.3",
    "port": 3,
    "class": "Audio",
    "driver": "snd-usb-audio",
    "speed": 12,
    "interface": 1
  }
]
```

By path
```
$ ./usbbind.py --device 1-4.1
[
  {
    "bus": 1,
    "device": 46,
    "vendor": "2109",
    "product": "2812",
    "name": "VIA Labs, Inc. VL812 Hub",
    "path": "1-4.1",
    "port": 1,
    "class": "Hub",
    "driver": "hub/4p",
    "speed": 480,
    "interface": 0
  }
]
```

### Unbind USB device

**NOTE** This requires root permission

By vendorID and productID
```
$ sudo ./usbbind.py --unbind 0ccd:0077
unbind 1-4.1.3
```

**WARNING** In case that you have multiple simular devices all of them will be unbound

By path
```
$ sudo ./usbbind.py --unbind 1-4.1.3
unbind 1-4.1.3
```

**WARNING** Afterwards device doesn't have a path anymore since it is unbound. You must remember what the path was in order to bind it again!

### Bind USB device

**NOTE** This requires root permission

```
$ sudo ./usbbind.py --bind 1-4.1.3
bind 1-4.1.3
```

**NOTE** This is only possible by path! You must remember it before you have unbound the device.

### Rebind USB device

**NOTE** This requires root permission

By vendorID and productID
```
$ sudo ./usbbind.py --rebind 0ccd:0077
unbind 1-4.1.3
bind 1-4.1.3
```

**WARNING** In case that you have multiple simular devices all of them will be rebound

By path
```
$ sudo ./usbbind.py --rebind 1-4.1.3
unbind 1-4.1.3
bind 1-4.1.3
```

## Pre-conditions
1. The script needs _root_ permission
2. The service utilizes
   1. Python 3
   2. The command ```lsusb```
