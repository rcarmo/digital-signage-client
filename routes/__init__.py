#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generic routes

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, logging, inspect, json, cgi

sys.path.append('../lib')
log = logging.getLogger()

from bottle import route, view, abort, app as bottle_default_app
import app, utils

# import all other routes - order is significant, keep static at the end

import feeds, content, static

@route('/')
@view('generic/index')
def index():
    """Startup screen"""
    app.template_vars.update({
        'title' : 'Startup Screen',
    })
    return app.template_vars


@route('/locate')
@view('generic/locate')
def locate():
    """Found me! screen"""
    app.template_vars.update({
        'title' : 'Locate',
    })
    return app.template_vars


@route('/nonet')
@view('generic/nonet')
def no_network():
    """No network screen"""
    app.template_vars.update({
        'title' : 'No Network Connection'
    })
    return app.template_vars

@route('/debug')
@view('generic/debug')
def dump_debug():
    """Debug screen (active routes)"""
    if not app.config.debug:
        abort(400, "Access Denied")
    app.template_vars.update({
        'title': 'Debug information',
        'modules': utils.docs(bottle_default_app())
    })
    return app.template_vars
