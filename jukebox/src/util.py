from flask import current_app as app
from flask import session, redirect
from functools import wraps
import re, subprocess, socket, os, json


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session or session['user'] is None:
            return redirect("/auth")
        return f(*args, **kwargs)

    return decorated


def get_subnet():
    ip_out = subprocess.check_output(["ip", "addr", "show",
                                      CONFIG["iface"]]).decode()
    return re.findall("inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,3})",
                      ip_out)[0]


def scan(subnet):
    #TODO: remove nmap dependency
    nmap_out = subprocess.check_output(
        ["nmap", "-n", "-sP", "-oG", "-", "subnet"]).decode()
    return re.findall("Host: ([\d\.]+) \(\)", nmap_out)[0]


def get_mac(ip):
    if ip == "127.0.0.1":
        return "00:00:00:00:00:00"
    else:
        arping_out = subprocess.check_output(["arp", "-a"]).decode()
        return re.findall("\({}\) at ([\w:]+)".format(ip), arping_out)[0]
