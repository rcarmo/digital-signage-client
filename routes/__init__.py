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

from bottle import route, view
import app, utils

# import all other routes


import static, feeds, content

@route('/')
@view('generic/index')
def index():
    """Renders the initial screen"""
    app.template_vars.update({
        'title' : 'Status',
    })
    return app.template_vars


@route('/locate')
@view('generic/locate')
def locate():
    """Renders a red template"""
    app.template_vars.update({
        'title' : 'Locate',
    })
    return app.template_vars


@route('/nonet')
@view('generic/nonet')
def locate():
    """Renders a built-in warning"""
    app.template_vars.update({
        'title' : 'No Network',
    })
    return app.template_vars


