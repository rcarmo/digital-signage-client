#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Beacon thread to report and fetch instructions from server

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, time, random, logging
import urlparse, urllib, urllib2, hashlib, shutil
import json, threading, subprocess
from Queue import Queue, Empty

# our own libraries
import app, utils, proxy, browser

log = logging.getLogger()

queue = Queue()


class Beacon(threading.Thread):
    """Beacon thread that talks to the server and tries to obtain commands."""

    def __init__(self, config, mac_address, ip_address, browser = None, poll_interval = 11):
        threading.Thread.__init__(self)
        self.config         = config
        self.mac_address    = mac_address
        self.ip_address     = ip_address
        self.poll_interval  = poll_interval
        self.browser        = browser
        self.local_uri      = 'http://%s:%s' % (config.http.bind_address, config.http.port)
        self.send_logs      = False
        self.opener         = urllib2.build_opener(proxy.SmartRedirectHandler())


    def call_home(self, data):
        """Talk to the server and get back any queued actions."""
        data = urllib.urlencode(data)
        req = urllib2.Request(self.config.server_url, data, {'Version': app.version} )
        resp = self.opener.open(req, timeout=15)
        try:
            actions = json.loads(resp.read().strip())
            return actions
        except:
            return None


    def do_update(self, item):
        """Perform a client update by dint of downloading a tarball and expanding it"""

        if 'bundle' in item:
            self.browser.do(self.config.uzbl.uri % (self.local_uri + 'updating.html'))
            # Signal other threads to quit cleanly
            app.running = False
            
            # Rather simple-minded approach to update via a tar file
            # Improvements to this are welcome, but this is field-tested :)
            log.debug('Preparing to update %s' % item)
            schema, host, _, _, _, _ = urlparse.urlparse(self.config.server_url)
            conn = urllib2.build_opener(proxy.SmartRedirectHandler())                     
            req = urllib2.Request('%s://%s/updates/%s' % (schema, host, item['bundle']))
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
        schema, host, _, _, _, _ = urlparse.urlparse(self.config.server_url)
        conn = urllib2.build_opener(proxy.SmartRedirectHandler())
        req = urllib2.Request('%s://%s/playlists/%s' % (schema, host, item['playlist']))
        try:
            resp = conn.open(req, timeout=30)
            # try to parse the playlist
            playlist = json.loads(resp.read())
            self.config.content.playlist_name = playlist['playlist']['name']
            # hand it over to the other thread
            queue.put({'playlist': playlist})
        except Exception as e:
            log.error("Got %s while fetching a new playlist", e)
            
    
    def do_uri(self, item):
        log.debug('Preparing to display %s' % item)
        queue.put(item)
        

    def do_text(self, item):
        log.debug('Preparing to display %s' % item)
        item.update({'uri': app.local_uri + '/text'})
        queue.put(item)
        

    def do_video(self, item):
        log.debug('Preparing to play %s' % item)
        queue.put(item)
        

    def do_qrcode(self, item):
        log.debug('Preparing to display %s' % item)
        item.update({'uri': app.local_uri + '/qrcode'})
        queue.put(item)
        

    def do_clock(self, item):
        """Deal with Raspberry Pi clock drift - assumes the UID we're running under can sudo date"""
        if 'time' in item:
            if abs(time.time() - item['time']) > 5:
                log.debug("Clock drift detected. Resetting clock according to server time.")
                subprocess.call('sudo date --set="@%f"' % item['time'], shell=True)


    def do_report_ip(self, item):
        """Handle the locate/report_ip action by queueing an URL view"""
        queue.put({'uri': app.local_uri + '/locate', 'duration': item })


    def do_send_logs(self, item):
        """Handle the logs action by toggling an instance variable"""
        self.send_logs = True


    def run(self):
        """Thread main loop"""
        while(app.running):
            time.sleep(self.poll_interval)
            if not hasattr(self.config,'server_url'):
                continue
            try:
                log.debug("Calling home...")
                data = {
                    'playlist'    : self.config.content.playlist_name,
                    'mac_address' : self.mac_address,
                    'ip_address'  : self.ip_address,
                    'cpu_freq'    : utils.get_cpu_freq(),
                    'cpu_temp'    : utils.get_cpu_temp(),
                    'cpu_usage'   : utils.get_cpu_usage(),
                    'browser_ram' : utils.get_pid_rss(self.browser.uzbl.pid),
                    'uptime'      : utils.get_uptime()
                }
                if self.send_logs:
                    data['logs'] = '\n'.join(utils.get_log_entries())
                    self.send_logs = False
                reply = self.call_home(data)
                log.debug("Got reply %s" % reply)
                self.do_clock(reply)
                try:
                    method = getattr(self, 'do_' + reply['action'])
                except AttributeError:
                    log.debug("Cannot handle reply %s", reply)
                if app.running: # state may have changed in the meantime
                    method(reply['data'])
            except Exception as e:
                log.debug("Got %s while calling home" % e)
                pass
        log.info("Exiting beacon thread.")

