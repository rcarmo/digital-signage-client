#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Routes for RSS feeds and other proxied urls

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, logging

sys.path.append('../lib')
log = logging.getLogger()

from bottle import route, view, HTTPError, response
import app, utils, proxy


@route('/feeds/<name>')
def route_feeds(name):
    """Feed proxy handler"""
    if name in app.config.content.feeds:
        return proxy.fetch(app.config.content.feeds[name], response)
    return HTTPError(404,"File not found")


@route('/feeds/<name>/<id>')
def route_item(name, id):
    """Feed proxy handler"""
    if name in app.config.content.feeds:
        return proxy.fetch(app.config.content.feeds[name] + '/%s' % id, response)
    return HTTPError(404,"File not found")