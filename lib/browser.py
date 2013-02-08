#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Uzbl browser wrapper

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, time, logging
from subprocess import *
import resource
import utils

log = logging.getLogger()


# data URI for blank homepage with black background
blank = 'data:text/html;base64,PHN0eWxlPmJvZHkgeyBiYWNrZ3JvdW5kOiBibGFjazsgfTwvc3R5bGU+'

# helper variable for setrlimit
_threshold = 0

def setrlimit():
    """Helper function to set browser subprocess resource limits"""
    resource.setrlimit(resource.RLIMIT_RSS, (_threshold,_threshold))


class Browser:

    def __init__(self, config, home=blank):
        """Handle initialization."""
        self.config = config
        self.home = home
        # launch subprocess
        self.launch(self.home)
        # open homepage
        self.do('set uri = %s' % home)


    def launch(self, home=blank):
        """Launch uzbl"""

        _threshold = self.config.uzbl.ram.hard_limit
        # Note that we explicitely set the geometry here as well (besides rlimit)
        self.uzbl = Popen(['/usr/bin/uzbl-core','--geometry=%dx%d+0+0' % (self.config.screen.width, self.config.screen.height),'--uri=%s' % home], stdin=PIPE, stdout=PIPE, preexec_fn=setrlimit)
        # Grab the right FIFO filename for controlling the browser
        self.fifo = '/tmp/uzbl_fifo_%d' % self.uzbl.pid
        # ...But it usually takes a few seconds to be created
        while not os.path.exists(self.fifo):
            time.sleep(1)
        # Now remove the status bar (failsafe in case the uzbl config file isn't loaded for some reason)
        self.do('set show_status = 0')


    def terminate(self):
        """Kill the browser (softly)"""
        self.uzbl.terminate()


    def kill(self):
        """Kill the browser"""
        self.uzbl.kill()


    def restart(self):
        """Restart the browser and open a blank screen"""
        self.uzbl.terminate()
        self.launch(blank)


    def blank(self):
        """Blank the screen"""
        self.do('set uri = %s' % blank)


    def do(self, buffer):
        """Perform a browser command by talking to its FIFO"""
        returncode = self.uzbl.poll()
        if returncode == None: # still running
            # Even though we're using rlimit, the kill/respawn cycle tends to
            # flash the screen, so we'll still try to do controlled restarts
            if self.config.uzbl.ram.soft_limit < utils.get_pid_rss(self.uzbl.pid):
                log.debug("Restarting browser due to memory leak")
                self.restart()
            h = open(self.fifo,'a')
            h.write(buffer + '\n')
            h.close()
        else:
            log.error("Browser exited with return code %s, relaunching" % returncode)
            self.launch(self.home)
            self.do(buffer)
