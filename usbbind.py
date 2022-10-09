#!/usr/bin/python3
import argparse
from ast import Pass
import json
import re
import subprocess
import sys
import time

VERSION = "0.1.0 (2022-10-09)"


class Usb():

    id_pattern = r"([\da-f]{4}):([\da-f]{4})"
    path_pattern = r"^(\d+|\d+\-\d+|\d+\-\d+(\.\d+)+)$"

    devices = list()

    def __init__(self) -> None:

        self.scan()

    def scan(self) -> None:

        def _collect_details(bus: int, port: int, deviceId: int, path: 'list', class_: str, driver: str, speed: int, interface=None) -> bool:

            device = next(filter(
                lambda d: d["bus"] == bus and d["device"] == deviceId, self.devices), None)

            if device:
                device["path"] = str(path[0])
                if len(path) > 1:
                    device["path"] += "-%s" % ".".join([str(i)
                                                       for i in path[1:]])
                device["port"] = port
                device["class"] = class_
                device["driver"] = driver
                device["speed"] = speed
                if interface is not None:
                    device["interface"] = interface

                return True

            return False

        self.devices = list()
        lines = subprocess.getoutput("lsusb").splitlines()
        for l in lines:
            m = re.match(
                "^Bus (\d+) Device (\d+): ID ([\da-f]{4}):([\da-df]+) (.+)$", l)

            if m:
                self.devices.append(
                    {
                        "bus": int(m.groups()[0]),
                        "device": int(m.groups()[1]),
                        "vendor": m.groups()[2],
                        "product": m.groups()[3],
                        "name": m.groups()[4]
                    }
                )

        re_bus = r"/:  Bus (\d+)\.Port (\d+): Dev (\d+), Class=([^,]+), Driver=([^,]+), (\d+)M$"
        re_node = r"^( +)\|__ Port (\d+): Dev (\d+), If (\d+), Class=([^,]+), Driver=([^,]*), (\d+)M$"

        path = []
        depth = 0

        lines = subprocess.getoutput("lsusb -t").splitlines()
        for l in lines:
            m = re.match(re_bus, l)
            if m:
                depth = 0
                path = [int(m.groups()[0])]
                _collect_details(bus=int(m.groups()[0]), port=int(m.groups()[1]), deviceId=int(m.groups()[
                    2]), class_=m.groups()[3], driver=m.groups()[4], speed=int(m.groups()[5]), path=path)

            else:
                m = re.match(re_node, l)
                if m:
                    port = int(m.groups()[1])
                    d = len(m.groups()[0])
                    if d > depth:
                        path.append(port)
                    elif d < depth:
                        path = path[:-2]
                        path.append(port)
                    else:
                        path[-1] = int(m.groups()[1])

                    depth = d
                    _collect_details(bus=path[0], port=int(m.groups()[1]), deviceId=int(m.groups()[2]), interface=int(
                        m.groups()[3]), class_=m.groups()[4], driver=m.groups()[5], speed=int(m.groups()[6]), path=path)

    def get_devices_by_id(self, vendor: str, product: str) -> 'list':

        return [d for d in self.devices if d["vendor"] == vendor and d["product"] == product]

    def bind(self, path: str) -> None:

        try:
            with open("/sys/bus/usb/drivers/usb/bind", "w") as f:
                print("bind %s" % path)
                f.write(path)
        except OSError as ex:
            print(ex, file=sys.stderr)

    def unbind(self, path: str) -> None:

        try:
            with open("/sys/bus/usb/drivers/usb/unbind", "w") as f:
                print("unbind %s" % path)
                f.write(path)
        except OSError as ex:
            print(ex, file=sys.stderr)

    def rebind(self, path: str, sleep=3) -> None:

        self.unbind(path)
        time.sleep(sleep)
        self.bind(path)

    def checkID(self, s: str) -> 'tuple[str:str]':

        m = re.match(self.id_pattern, s)
        if not m:
            return None, None

        return m.groups()[0], m.groups()[1]

    def isPath(self, s: str) -> bool:

        return re.match(self.path_pattern, s) is not None


def prepare_args(argv: 'list[str]') -> 'tuple[argparse.ArgumentParser,argparse.Namespace]':

    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true",
                        help="prints usb details in json format")
    parser.add_argument("--version", action="store_true",
                        help="print version")
    parser.add_argument("--bind", type=str,
                        help="bind usb device given as path, e.g. 1-2.3")
    parser.add_argument("--unbind", type=str,
                        help="unbind usb device given as path, e.g. 1-2.3, or vendorID:productID, e.g. 0ccd:0077")
    parser.add_argument("--rebind", type=str,
                        help="rebind usb device given as path, e.g. 1-2.3, or vendorID:productID, e.g. 0ccd:0077")
    parser.add_argument("--device", type=str,
                        help="prints details of usb device given as path, e.g. 1-2.3, or vendorID:productID, e.g. 0ccd:0077, in json format")

    return parser, parser.parse_args(argv[1:])


def print_help(parser: argparse.ArgumentParser) -> None:

    print_version()
    parser.print_help()


def print_version() -> None:

    print("A tool that makes binding of USB devices easy.\nVersion: %s\n" % VERSION)


def parseIds(usb: Usb, s: str) -> 'tuple[str,str]':

    v, p = usb.checkID(s)
    if not v:
        print("vendorID and productID must be given like this: 0ccd:0077")
        exit(1)

    return v, p


def _perform(method, arg) -> None:

    usb = Usb()
    if usb.isPath(arg):
        paths = [arg]
    else:
        v, p = parseIds(usb, arg)
        paths = [d["path"] for d in usb.get_devices_by_id(v, p) if "path" in d]

    m = getattr(usb, method)
    for p in paths:
        m(p)


if __name__ == "__main__":

    parser, args = prepare_args(sys.argv)

    if args.json:
        usb = Usb()
        print(json.dumps(usb.devices, indent=2))

    elif args.device:
        usb = Usb()
        if usb.isPath(args.device):
            devices = [
                d for d in usb.devices if "path" in d and d["path"] == args.device]

        else:
            v, p = parseIds(usb, args.device)
            devices = usb.get_devices_by_id(v, p)

        print(json.dumps(devices, indent=2))

    elif args.bind:
        _perform("bind", args.bind)

    elif args.unbind:
        _perform("unbind", args.unbind)

    elif args.rebind:
        _perform("rebind", args.rebind)

    elif args.version:
        print_version()

    else:
        print_help(parser)
