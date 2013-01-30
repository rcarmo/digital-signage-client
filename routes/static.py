#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Routes for local static content

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, logging
from bottle import qroute, static_file, view

log = logging.getLogger()

import app, utils

@route('/')
def index():
    """Index page"""
    return static_file('index.html', root=app.staticroot)

@route('<filepath:path>')
def static(filepath):
    """Handles all the remanining static files"""
    return static_file(filepath, root=app.staticroot)

