#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Routes for local static content

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, logging
from bottle import app, route, static_file, view

log = logging.getLogger()

import utils, config

@route('/')
def index():
    """Index page"""
    return static_file('index.html', root=config.staticroot)

@route('<filepath:path>')
def static(filepath):
    """Handles all the remanining static files"""
    return static_file(filepath, root=config.staticroot)

