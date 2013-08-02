#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
omxplayer wrapper

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, time, logging
from subprocess import *
from threading import Timer
import utils
from config import settings

log = logging.getLogger()


def _handler(player):
    """Timer handler"""
    player.terminate()


class Player:

    def __init__(self):
        """Handle initialization."""
        self.omxplayer = self.timer = None


    def launch(self, uri, timeout=0):
        """Launch omxplayer"""
        # we need to provide at least a valid stdin parameter,
        # otherwise omxplayer will fail.
        # Note that we force audio to "local" to mute HDMI output
        self.omxplayer = Popen(['/usr/bin/omxplayer','-o','local',uri], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        # set up timeout
        if timeout:
            self.timer = Timer(timeout, _handler, [self])
            self.timer.start()
            log.debug("Started timer for %ds" % timeout)
        self.omxplayer.wait()


    def terminate(self):
        """Kill the player (softly)"""
        # Send a quit command to omxplayer -- this _finally_ works properly in the latest versions
        output = self.omxplayer.communicate('q')[0]
        log.debug("omxplayer: %s" % output.replace('\n',' '))
        # try to quit the process normally in case the usual exit message isn't there.
        # in my experience omxplayer is notoriously flaky, so this sometimes doesn't work
        if "nice day" not in output:
            log.debug("Terminating player")
            self.omxplayer.terminate()


    def kill(self):
        """Kill the player"""
        log.debug("Killing player")
        self.omxplayer.kill()
