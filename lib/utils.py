#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility classes and functions

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, time, re, logging, subprocess, urllib, urllib2
import json, xml.dom.minidom
import socket, fcntl, struct, platform, inspect
from collections import deque
from decorators import memoize

log = logging.getLogger()


class Struct(dict):
    """An object that recursively builds itself from a dict and allows easy access to attributes"""

    def __init__(self, obj):
        dict.__init__(self, obj)
        for k, v in obj.iteritems():
            if isinstance(v, dict):
                self.__dict__[k] = Struct(v)
            else:
                self.__dict__[k] = v

    def __getattr__(self, attr):
        try:
            return self.__dict__[attr]
        except KeyError:
            raise AttributeError(attr)

    def __setitem__(self, key, value):
        super(Struct, self).__setitem__(key, value)
        self.__dict__[key] = value

    def __setattr__(self, attr, value):
        self.__setitem__(attr, value)


class InMemoryHandler(logging.Handler):
    """In memory logging handler with a circular buffer"""

    def __init__(self, limit=8192):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Our custom argument
        self.limit = limit
        self.flush()

    def emit(self, record):
        self.records.append(self.format(record))

    def flush(self):
        self.records = deque([], self.limit)

    def dump(self):
        return self.records


@memoize
def shorten(url):
    """Minimalist URL shortener using SAPO services"""
    u = '?'.join(('http://services.sapo.pt/PunyURL/GetCompressedURLByURL',urllib.urlencode({'url':url})))
    try:
        x = xml.dom.minidom.parseString(urllib2.urlopen(u).read())
        return x.getElementsByTagName('ascii')[0].firstChild.data
    except:
        return url


def valid_mac_address(addr):
    """Validate a physical Ethernet address"""
    return re.match("[0-9a-f]{2}([-:][0-9a-f]{2}){5}$", addr.lower())


def valid_ip_address(addr):
    """Quick and dirty way to validate any kind of IP address"""
    try:
        socket.inet_aton(addr)
        return True
    except socket.error:
        return False


def get_pid_stats(pid):
    """Retrieve process kernel counters"""
    stats = open('/proc/%d/status' % pid,'r').readlines()
    return dict(filter(lambda x: len(x)==2, map(lambda x: x.split()[:2], stats)))


def get_pid_rss(pid):
    """Retrieve a process' resident set size"""
    try:
        return int(get_pid_stats(pid)['VmRSS:'])
    except:
        return 0


def get_net_bytes(dev='eth0'):
    """Read network interface traffic counters"""
    return {
        'rx': float(open('/sys/class/net/%s/statistics/rx_bytes' % dev, 'r').read().strip()),
        'tx': float(open('/sys/class/net/%s/statistics/tx_bytes' % dev, 'r').read().strip())
    }


def get_cpu_stat():
    """Retrieves CPU stats"""
    cpu = open('/proc/stat','r').readlines()[0]
    return map(float, cpu.split()[1:5])


def get_cpu_usage(interval=0.1):
    """Estimates overall CPU usage during a short time interval"""
    t1 = get_cpu_stat()
    time.sleep(interval)
    t2 = get_cpu_stat()
    delta = [t2[i] - t1[i] for i in range(len(t1))]
    try:
        return 1.0 - (delta[-1:].pop()/(sum(delta)*1.0))
    except:
        return 0.0


def get_cpu_freq(cpu='cpu0'):
    """Retrieves the current CPU speed in MHz - for a single CPU"""
    if 'Linux' in platform.system():
        return float(open('/sys/devices/system/cpu/%s/cpufreq/scaling_cur_freq' % cpu, 'r').read().strip())/1000.0
    return 0


def get_cpu_temp(cpu='cpu0'):
    """Retrieves the current CPU core temperature in degrees Celsius - specific to the Raspberry Pi"""
    if 'Linux' in platform.system():
        return float(open('/sys/class/thermal/thermal_zone%s/temp' % cpu[-1], 'r').read().strip())/1000.0
    return 0


def get_uptime():
    """Retrieves the system uptime, in seconds"""

    # if we're running this in Mac OS X (for staging, etc.)
    if 'Darwin' in platform.system():
        sysctl = subprocess.Popen('sysctl kern.boottime', shell=True, stdout=subprocess.PIPE)
        return time.time() - float(re.match('kern.boottime:\D+(\d+)', sysctl.stdout.read()).group(1))

    # else assume we're doing in Linux and get it from /proc
    return float(open('/proc/uptime', 'r').read().split(' ')[0])


@memoize
def get_mac_address(dev="eth0"):
    """Retrieves the MAC address for a given interface"""

    # if we're running this in Mac OS X (for staging, etc.)
    if 'Darwin' in platform.system():
        ifconfig = subprocess.Popen('ifconfig %s' % dev, shell=True, stdout=subprocess.PIPE)
        return filter(lambda x: 'ether' in x.strip(), ifconfig.stdout.readlines())[0].split()[1]

    # else assume we're doing in Linux and get it from /sys
    return open('/sys/class/net/%s/address' % dev, 'r').read().strip()


def get_ip_address(dev="eth0"):
    """Retrieves the IP address for a given interface"""

    # if we're running this in Mac OS X (for staging, etc.)
    if 'Darwin' in platform.system():
        ipconfig = subprocess.Popen('ipconfig getifaddr %s' % dev, shell=True, stdout=subprocess.PIPE)
        return ipconfig.stdout.read().strip()

    # else assume we're doing it in Linux and do it via SIOCGIFADDR
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', str(dev)[:15]))[20:24])
    except Exception, e:
        log.debug('Error getting IP address for %s: %s' % (dev,e))
        return None


def get_config(filename):
    """Parses the configuration file."""
    try:
        config = Struct(json.load(open(filename, 'r')))
    except Exception, e:
        # this is one of the few instanceis where we cannot rely on logging to be active
        print 'Error loading configuration file %s: %s' % (filename, e)
        sys.exit(2)
    return config


def path_for(name):
    """Build relative paths to current script"""
    return os.path.join(os.path.dirname(sys.argv[0]), name)


def check_resolution(settings):
    """If we're running on Linux, try to figure out what the display's set to"""
    if 'Linux' in platform.system():
        res = subprocess.Popen('fbset', stdout=subprocess.PIPE, stderr=open(os.devnull,'wb'), shell=True)
        # We're only going to account for one other case here
        if '"1024x768"' in res.stdout.read().split():
            settings.screen.width = 1024
            settings.screen.height = 768
    return settings


def get_log_entries():
    """Locates the RAM log handler (if any) and returns the last log entries"""
    for handler in log.handlers:
        if type(handler) is InMemoryHandler:
            return handler.dump()
    return None


def docs(app):
    """Gather all docstrings related to routes and return them grouped by module"""
    modules = {}
    for route in app.routes:
        doc = inspect.getdoc(route.callback) or inspect.getcomments(route.callback)
        if not doc:
            doc = ''
        module = inspect.getmodule(route.callback).__name__
        item = {
            'method': route.method,
            'route': route.rule,
            'function': route.callback.__name__,
            'module': module,
            'doc': inspect.cleandoc(doc)
        }
        if not module in modules:
            modules[module] = []
        modules[module].append(item)
    return modules
