#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main signage client script

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, re, stat, glob, time, json, logging, logging.config, threading, random
import socket, urllib, urllib2, urlparse, commands, functools, subprocess

sys.path.append('lib')

import bottle, utils

# our own modules
import routes, beacon, playlist, browser

# Shared data used by other modules
version    = '0.13.01.21.1'
# Flag for controlled thread termination
running    = True
# Screen state sent from server
screen     = {}

# various
staticroot = utils.path_for('static')
config     = utils.get_config(os.path.join(utils.path_for('data'),'config.json'))
ip_address = utils.get_ip_address(config.interface)

# Defaults sent to templates
template_vars = {
    'version'   : version,
    'ip_address': ip_address,
    'width'     : config.screen.width,
    'height'    : config.screen.height,
    'debug'     : config.debug
}

if __name__=='__main__':
    # Set up logging
    logging.config.dictConfig(json.loads(str(config.logging)))
    log = logging.getLogger()

    log.info("Starting application.")

    # If we're running on a Pi, try to figure out what the display's set to
    res = subprocess.Popen('fbset', stdout=subprocess.PIPE, stderr=open(os.devnull,'wb'), shell=True)

    # We're only going to account for one other case here
    if '"1024x768"' in res.stdout.read().split():
        config.screen.width = 1024
        config.screen.height = 768
    
    # Check if another instance is still running
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((config.http.bind_address,config.http.port))
        log.error("Server already running, exiting.")
        sys.exit(1)
    except socket.error, msg:
        pass

    log.info("Socket free.")
    if ip_address or config.staging:
        if not config.staging:
            # Get the browser going
            u = browser.Browser(config)
            p = playlist.Player(u, 'playlist.json')
            log.info("Starting player thread")
            p.start()
        try:
            assert(config.server_url)
            b = beacon.Beacon(config, utils.get_mac_address(), ip_address, u)
            log.info("Starting beacon thread")
            b.start()
        except:
            log.info("Server URL not set, operating in standalone mode")
            pass
    else:
        # Signal for help and stay put. There's no point in debugging the LAN ourselves.
        b = browser.Browser(config)
        b.do(config.command['local'] % 'nonet')
        log.error("Failsafe mode")

    bottle.run(port=config.http.port,host=config.http.bind_address,debug=config.debug,reloader=config.debug)
