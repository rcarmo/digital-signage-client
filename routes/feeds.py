#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, logging

sys.path.append('../lib')
log = logging.getLogger()

from bottle import route, view, HTTPError, response
import app, config, utils, proxy


@route('/feeds/<name>')
def route_feeds(name):
    """Feed proxy handler"""
    if name in config.feeds.keys():
        return proxy.fetch(config.feeds[name], response)
    return HTTPError(404,"File not found")


@route('/feeds/<name>/<id>')
def route_item(name, id):
    """Feed proxy handler"""
    if name in config.feeds.keys():
        return proxy.fetch(config.feeds[name] + '/%s' % id, response)
    return HTTPError(404,"File not found")