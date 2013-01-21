#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
omxplayer wrapper

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, time, logging
from subprocess import *
from signal import alarm, signal, SIGALRM
import utils

log = logging.getLogger()


class Alarm(Exception):
    """Exception class to be thrown on SIGALRM"""
    pass


def _handler(signum, frame):
    """signal handler"""
    raise Alarm


class Player:

    def __init__(self, config):
        """Handle initialization."""
        self.config = config


    def launch(self, uri, timeout=0):
        """Launch omxplayer"""

        # set up timeout
        if timeout:
            signal(SIGALRM,_handler)
            alarm(timeout)

        try:
            self.omxplayer = Popen(['/usr/bin/omxplayer','-o','local',uri], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            alarm(0)
        except Alarm:
            self.terminate()


    def terminate(self):
        """Kill the player (softly)"""
        self.omxplayer.terminate()


    def kill(self):
        """Kill the player"""
        self.omxplayer.kill()
