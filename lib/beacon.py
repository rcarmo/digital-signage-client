#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Beacon thread to report and fetch instructions from server

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, time, random, logging
import urllib, urllib2, hashlib, shutil
import json, threading, subprocess
from Queue import Queue, Empty

# our own libraries
import utils, proxy, browser

log = logging.getLogger()

queue = Queue()

def call_home(data, server_url):
    """Talk to the server and get back any queued actions."""

    conn = urllib2.build_opener(proxy.SmartRedirectHandler())
    data = urllib.urlencode(data)
    req = urllib2.Request(server_url, data, {'Version': config.version} )
    resp = conn.open(req, timeout=15)
    try:
        actions = json.loads(resp.read().strip())
        return actions
    except:
        return None


class Beacon(threading.Thread):
    """Beacon thread that talks to the server and tries to obtain commands."""

    def __init__(self, config, mac_address, ip_address, browser = None, poll_interval = 11):
        threading.Thread.__init__(self)
        self.config         = config
        self.mac_address    = mac_address
        self.ip_address     = ip_address
        self.poll_interval  = poll_interval
        self.browser        = browser
        self.playlist       = 'Built-in'
        self.local_uri      = 'http://%s:%s/' % (config.http.bind_address, config.http.port)


    def do_update(self, item):
        """Perform a client update by dint of downloading a tarball and expanding it"""

        if 'bundle' in item:
            self.browser.do(config.command['local'] % 'updating.html')
            # Signal other threads to quit cleanly
            config.running = False

            # Rather simple-minded approach to update via a tar file
            # Improvements to this are welcome, but this is field-tested :)
            log.debug('Preparing to update %s' % item)
            conn = urllib2.build_opener(proxy.SmartRedirectHandler())                        
            req = urllib2.Request('%s/updates/%s' % (config.server, item['bundle']))
            try:
                resp = conn.open(req, timeout=30)   
                # Yes, we assume the update will always fit into RAM 
                log.debug('Preparing to update using: %s' % item)
                buffer = resp.read()
                open('/tmp/update.tgz','wb').write(buffer)
                os.chdir(os.environ['HOME'])
                # Remove previous version
                shutil.rmtree(os.path.join(os.environ['HOME'] + 'signage'), True)
                # Expand update
                subprocess.call('tar -zxvf /tmp/update.tgz', shell=True)
                # Kill browser
                self.browser.kill()
                # Exit all threads
                os._exit(1)
            except Exception as e:
                log.error("Got %s while updating" % e)


    def do_playlist(self, item):
        log.debug('Preparing to update %s' % item)
        conn = urllib2.build_opener(proxy.SmartRedirectHandler())                        
        req = urllib2.Request('%s/playlists/%s' % (config.server + item['playlist']))
        try:
            resp = conn.open(req, timeout=30)
            # try to parse the playlist
            playlist = json.loads(resp.read())
            self.playlist = playlist['playlist']['name']
            # hand it over to the other thread
            queue.put({'playlist': playlist})
        except Exception as e:
            log.error("Got %s while fetching a new playlist", e)
            
    
    def do_uri(self, item):
        log.debug('Preparing to display %s' % item)
        queue.put(item)
        

    def do_text(self, item):
        log.debug('Preparing to display %s' % item)
        item.update({'uri': self.local_uri + 'text'})
        queue.put(item)
        

    def do_video(self, item):
        log.debug('Preparing to play %s' % item)
        queue.put(item)
        

    def do_qrcode(self, item):
        log.debug('Preparing to display %s' % item)
        item.update({'uri': self.local_uri + 'qrcode'})
        queue.put(item)
        

    def do_clock(self, item):
        """Deal with Raspberry Pi clock drift - assumes the UID we're running under can sudo date"""
        if 'time' in item:
            if abs(time.time() - item['time']) > 5:
                log.debug("Clock drift detected. Resetting clock according to server time.")
                subprocess.call('sudo date --set="@%f"' % item['time'], shell=True)


    def do_report_ip(self, item):
        """Handle the locate/report_ip action by queueing an URL view"""
        queue.put({'uri': self.local_uri = 'locate', 'duration': item })


    def run(self):
        """Thread main loop"""
        while(config.running):
            try:
                time.sleep(self.poll_interval)
                log.debug("Calling home...")
                reply = call_home({
                    'playlist'    : self.playlist,
                    'mac_address' : self.mac_address,
                    'ip_address'  : self.ip_address,
                    'cpu_freq'    : utils.get_cpu_freq(),
                    'cpu_temp'    : utils.get_cpu_temp(),
                    'cpu_usage'   : utils.get_cpu_usage(),
                    'browser_ram' : utils.get_pid_rss(self.browser.uzbl.pid),
                    'uptime'      : utils.get_uptime()
                }, self.config.server_url)
                log.debug("Got reply %s" % reply)
                self.do_clock(reply)
                try:
                    method = getattr(self, 'do_' + reply['action'])
                except AttributeError:
                    log.debug("Cannot handle reply %s", reply)
                if config.running: # state may have changed in the meantime
                    method(reply['data'])
            except Exception as e:
                log.debug("Got %s while calling home" % e)
                pass
        log.info("Exiting beacon thread.")

