#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main signage client script

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, re, stat, glob, time, json, logging, logging.config, threading, random
import socket, urllib, urllib2, urlparse, commands, functools, subprocess

sys.path.insert(0,'lib') # prefer bundled libraries to local installs

import bottle, utils

# read configuration file and setup various globals, including logging formats
from config import settings

# Set up logging
log        = logging.getLogger()
# validate framebuffer settings
settings   = utils.check_resolution(settings)
# setup static file root
staticroot = utils.path_for('static')
# check if we have a valid IP address
ip_address = utils.get_ip_address(settings.interface)
# Shared data used by other modules
version    = '0.13.08.02.1'
# Flag for controlled thread termination
running    = True
# Screen state sent from server
screen     = {}
# Local URI Prefix
local_uri  = 'http://%s:%s' % (settings.http.bind_address, settings.http.port)

# Defaults sent to templates
template_vars = {
    'version'   : version,
    'ip_address': ip_address,
    'width'     : settings.screen.width,
    'height'    : settings.screen.height,
    'debug'     : settings.debug
}


if __name__=='__main__':
    if settings.debug:
        if 'BOTTLE_CHILD' not in os.environ:
            log.debug('Using reloader, spawning first child.')
        else:
            log.debug('Child spawned.')

    if not settings.debug or ('BOTTLE_CHILD' in os.environ):
        log.info("Setting up application.")
        import routes, playlist, browser, beacon, video

        # Check if another instance is still running
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((settings.http.bind_address, settings.http.port))
            print "Server already running, exiting."
            sys.exit(2)
        except socket.error, msg:
            pass
        log.info("Socket free.")

        uzbl = None
        if not settings.staging:
            # Get the browser going
            uzbl = browser.Browser()
            p = playlist.Player(uzbl, 'playlist.json')
            log.info("Starting player thread")
            p.start()

            if hasattr(settings, 'server_url'):
                b = beacon.Beacon( utils.get_mac_address(settings.interface), uzbl)
                log.info("Starting beacon thread")
                b.start()
            else:
                log.info("No server configured, operating in standalone mode.")

    log.info("Serving requests.")
    bottle.run(
        port     = settings.http.port, 
        host     = settings.http.bind_address, 
        debug    = settings.debug,
        reloader = settings.debug
    )
