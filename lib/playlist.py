#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Playlist handling thread

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, time, threading, json, random, logging, subprocess
from Queue import Queue, Empty
import app, beacon, utils, browser

log = logging.getLogger()

class Player(threading.Thread):

    def __init__(self, config, browser, playlist_name = 'default.json', start_interval=10):
        """Initialization"""
        
        threading.Thread.__init__(self)
        self.config         = config
        self.start_interval = start_interval
        self.browser        = browser
        self.playlist       = self.read_playlist(playlist_name)


    def read_playlist(self, name):
        """Retrieve playlist data from a JSON file"""
        try:
            playlist = json.loads(open(os.path.join(utils.path_for('data'), 
                '%s' % name),'r').read())['playlist']
        except Exception, e:
            log.error('Error %s loading playlist "%s", using default' % (e,name))
            playlist = json.loads(open(os.path.join(utils.path_for('data'),
                'default.json'),'r').read())['playlist']
        return playlist


    def do_screen(self, item):
        """Display a given screen"""
        # Set the global state variable.
        app.screen = item
        # This works because we're only displaying a screen at a time,
        # makes it trivial to pass context to the HTML templates
        # and avoids messy parameter passing via the URI
        log.debug('Showing screen %s' % app.screen)
        # now get the browser to ask for the item URI
        self.browser.do(config.command['uri'] % item['uri'])
        try:
            time.sleep(item['duration'])
        except:
            pass
        app.screen = {}
        return True


    def do_video(self, item):
        """Play a video"""
        log.debug('Playing video %s' % item)
        # Clear the screen first
        self.browser.do(config.command['uri'] % browser.blank)
        # we need to provide at least a valid stdin parameter,
        # otherwise omxplayer will fail.
        # Note that we force audio to "local" to mute HDMI output
        subprocess.call('omxplayer -o local %s' % item['file'], 
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, shell=True)
        log.debug('Played video %s' % item)
        return True


    def do_playlist(self, item):
        """Set current playlist"""
        self.playlist = item['playlist']['playlist']
        # persist the playlist as the default for this player
        f = open(os.path.join(utils.path_for('config'),
            'default.json'),'w').write(json.dumps(item['playlist'], 2))
        return False


    # TODO: change these to a getattr(self, 'do_' + cmd) construct
    def handle_item(self, item):
        """Handle a server item"""
        log.debug('Handling %s' % item)
        # Is it a whole new playlist?
        if 'playlist' in item:
            return self.do_playlist(item)
        # Is it a conventional screen?
        if 'uri' in item:
            return self.do_screen(item)
        if 'file' in item:
            return self.do_video(item)
        # Is it a random sample from a group?
        elif 'random' in item:
            try:
                item = random.sample(self.playlist['random'][item['random']],1)[0]
            except Exception, e:
                log.debug('Error %s in picking a sample from group %s' % (e, item['random']))
                return
            return self.handle_item(item)
        return False


    def run(self):
        """Thread loop"""
        log.info('Waiting %ds...' % self.start_interval)
        time.sleep(self.start_interval)
        log.info('Starting playlist')
        while(config.running):
            log.debug("Current playlist: %s" % self.playlist)
            for item in self.playlist['screens']:
                # reset shared data
                try:
                    server_item = beacon.queue.get_nowait()
                    log.debug("Current server item: %s" % server_item)
                    stay = self.handle_item(server_item)                        
                    beacon.queue.task_done()
                    if not stay:
                        log.debug("Exiting loop")
                        break
                except Empty:
                    pass
                log.debug("Current item: %s" % item)
                if config.running: # state may have changed
                    self.handle_item(item)
        log.info("Exiting player thread.")