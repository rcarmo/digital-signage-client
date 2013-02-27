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

log = logging.getLogger()


def _handler(player):
    """Timer handler"""
    log.debug("Terminating player")
    player.terminate()


class Player:

    def __init__(self, config):
        """Handle initialization."""
        self.config = config
        self.omxplayer = self.timer = None


    def launch(self, uri, timeout=0):
        """Launch omxplayer"""

        # set up timeout
        if timeout:
            self.timer = Timer(timeout, _handler, [self])
            self.timer.start()

        # we need to provide at least a valid stdin parameter,
        # otherwise omxplayer will fail.
        # Note that we force audio to "local" to mute HDMI output
        self.omxplayer = Popen(['/usr/bin/omxplayer','-o','local',uri], stdin=PIPE, stdout=PIPE, stderr=PIPE)


    def terminate(self):
        """Kill the player (softly)"""
        self.omxplayer.terminate()


    def kill(self):
        """Kill the player"""
        self.omxplayer.kill()
