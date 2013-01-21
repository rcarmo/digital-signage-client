#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Proxy helper routines with simple caching

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, time, logging, urllib, urllib2
import bottle
from subprocess import *

log = logging.getLogger()

# feed cache
_cache = {}

cache_interval = 120

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    """Redirect handler helper class"""

    def http_error_301(self, req, fp, code, msg, headers):
        log.debug("Handling 301 redirect")
        result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
        result.status = code
        return result

    def http_error_302(self, req, fp, code, msg, headers):
        log.debug("Handling 302 redirect")
        result = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
        result.status = code
        return result


def sanitize_headers(headers, server_response):
    """Remove potentially troublesome headers from the remote server response"""
    for h in headers.keys():
        if h not in ['connection','cache-control','server','accept-ranges',
            'keep-alive','proxy-authenticate','proxy-authorization','te',
            'trailers','transfer-encoding']:
            server_response.set_header(h, headers[h])


def fetch(uri, server_response):
    """Fetch an uri as required"""
    
    if uri in _cache:
        if (time.time() - _cache[uri]['time']) <= cache_interval:
            sanitize_headers(_cache[uri]['headers'], server_response)
            return _cache[uri]['data']
            
    conn = urllib2.build_opener(SmartRedirectHandler())
    req = urllib2.Request(uri)
    
    try:
        resp = conn.open(req)

    except urllib2.HTTPError, e:
        log.error("Got error code %s while proxying %s" % (str(e.code), uri))
        if cache_interval and uri in _cache:
            sanitize_headers(_cache[uri]['headers'],server_response)
            return _cache[uri]['data']
        return bottle.HTTPError(e.code,"Server could not fullfill request")

    except urllib2.URLError, e:
        log.error("Got error while proxying %s: %s" % (uri, e.reason))
        if cache_interval and uri in _cache:
            sanitize_headers(_cache[uri]['headers'],server_response)
            return _cache[uri]['data']
        return bottle.HTTPError(500,e.reason)

    buffer = resp.read()
    conn.close()

    # Store the results
    _cache[uri] = {
        'data':     buffer,
        'headers':  resp.headers,
        'time':     time.time()
    }
    sanitize_headers(resp.headers, server_response)
    return buffer
