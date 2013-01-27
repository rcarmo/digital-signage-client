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

# read configuration file and setup various globals
config     = utils.get_config(os.path.join(utils.path_for('data'),'config.json'))
# validate framebuffer settings
config = utils.validate_resolution(config)
# setup static file root
staticroot = utils.path_for('static')
# check if we have a valid IP address
ip_address = utils.get_ip_address(config.interface)
# Shared data used by other modules
version    = '0.13.01.21.1'
# Flag for controlled thread termination
running    = True
# Screen state sent from server
screen     = {}

# Defaults sent to templates
template_vars = {
    'version'   : version,
    'ip_address': ip_address,
    'width'     : config.screen.width,
    'height'    : config.screen.height,
    'debug'     : config.debug
}

# Set up logging
logging.config.dictConfig(dict(config.logging))
log = logging.getLogger()


if __name__=='__main__':
    if config.debug:
        if 'BOTTLE_CHILD' not in os.environ:
            log.debug('Using reloader, spawning first child.')
        else:
            log.debug('Child spawned.')

    if not config.debug or ('BOTTLE_CHILD' in os.environ):
        log.info("Setting up application.")
        import routes, playlist, browser, beacon, video
        log.info("Serving requests.")

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
            uzbl = None
            if not config.staging:
                # Get the browser going
                uzbl = browser.Browser(config)
                p = playlist.Player(uzbl, 'playlist.json')
                log.info("Starting player thread")
                p.start()

                try:
                    assert('http' in config.server_url)
                    b = beacon.Beacon(config, utils.get_mac_address(config.interface), ip_address, uzbl)
                    log.info("Starting beacon thread")
                    b.start()
                except Exception, e:
                    log.info("%s, operating in standalone mode." % e)
                    pass
        else:
            # Signal for help and stay put. There's no point in debugging the LAN ourselves.
            uzbl = browser.Browser(config)
            uzbl.do(config.command['local'] % 'nonet')
            log.error("Failsafe mode")

    bottle.run(
        port     = config.http.port, 
        host     = config.http.bind_address, 
        debug    = config.debug,
        reloader = config.debug
    )
