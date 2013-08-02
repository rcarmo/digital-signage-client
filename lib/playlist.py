#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Playlist handling thread

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, time, threading, json, random, logging, subprocess
from Queue import Queue, Empty
import app, beacon, utils, browser, video
from config import settings

log = logging.getLogger()

class Player(threading.Thread):

    def __init__(self, browser, filename='default.json', start_interval=10):
        """Initialization"""
        
        threading.Thread.__init__(self)
        self.start_interval = start_interval
        self.browser        = browser
        self.video          = video.Player()
        self.filename       = filename
        self.playlist       = self.read_playlist(filename)
        self.local_uri      = 'http://%s:%s' % (settings.http.bind_address, settings.http.port)

    def read_playlist(self, name):
        """Retrieve playlist data from a JSON file"""
        try:
            playlist = json.loads(open(os.path.join(utils.path_for('data'), 
                '%s' % name),'r').read())['playlist']
            settings.content.playlist_name = playlist['playlist']['name']
        except Exception, e:
            log.error('Error %s loading playlist "%s", attempting to fallback to default' % (e,name))
            playlist = json.loads(open(os.path.join(utils.path_for('data'),
                self.filename),'r').read())['playlist']
        return playlist


    def do_screen(self, item):
        """Display a given screen"""
        # Set the global state variable.
        app.screen = item
        # This works because we're only displaying a screen at a time,
        # makes it trivial to pass context to the HTML templates
        # and avoids messy parameter passing via the URI
        log.debug('Showing screen %s' % app.screen)

        # if playlist has schemaless URIs, assume they're local
        if item['uri'][0] == '/':
            item['uri'] = self.local_uri + item['uri']
        self.browser.do(settings.uzbl.uri % item['uri'])
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
        self.browser.blank()
        if 'duration' in item:
            self.video.launch(item['file'], int(item['duration']))
        else:
            self.video.launch(item['file'])
        log.debug('Played video %s' % item)
        return True


    def do_playlist(self, item):
        """Set current playlist"""
        self.playlist = item['playlist']['playlist']
        # persist the playlist as the default for this player
        f = open(os.path.join(utils.path_for('data'),
            self.filename),'w').write(json.dumps(item['playlist'], 2))
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
        while(app.running):
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
                if app.running: # state may have changed
                    self.handle_item(item)
        log.info("Exiting player thread.")
