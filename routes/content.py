#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Routes for built-in content and templates

Created by: Rui Carmo
License: MIT (see LICENSE for details)
"""

import os, sys, logging, random
import bottle
import app, proxy, utils

log = logging.getLogger()


@bottle.route('/qrcode')
@bottle.view('screens/qrcode')
def qrcode():
    """Renders a QR Code and associated message"""
    app.template_vars.update({
        'title'  : 'DECODE THIS',
        'code'   : 'https://codebits.eu',
        'message': 'Have you checked out the site lately?',
    })
    app.template_vars.update(app.screen)
    return app.template_vars


@bottle.route('/text')
@bottle.view('screens/text')
def textmessage():
    """Renders a text/HTML message"""
    app.template_vars.update({
        'title'  : 'ATTENTION',
        'message': 'This is a generic warning message',
    })
    app.template_vars.update(app.screen)
    return app.template_vars


@bottle.route('/pixelart')
@bottle.view('screens/pixelart')
def pixelart():
    """Renders the pixelart view"""
    return {
        'width': config.width,
        'height': config.height,
        'debug': config.debug
    }


@bottle.route('/hype/random')
def random_hype():
    """Provides the random imagery for the pixelart view"""
    return bottle.redirect(
        'http://localhost:8000/hype/img/' +
        random.choice(
            filter( lambda x: x[0] != '.',
                    os.listdir(os.path.join(config.staticroot, 'hype/img')))
        ), 303)


@bottle.route('/tweets')
@bottle.view('screens/tweets')
def tweets():
    """Renders the twitter stream"""
    return {
        'title': 'Tweets',
        'width': config.width,
        'height': config.height,
        'debug': config.debug
    }


@bottle.route('/photos')
@bottle.view('screens/photos')
def photos():
    """Renders a photo montage"""
    return {
        'feed': 'photos',
        'title': 'Photos',
        'width': config.width,
        'height': config.height,
        'debug': config.debug
    }


@bottle.route('/news/<name>')
@bottle.view('screens/news')
def newsfrom(name):
    """Renders a news feed"""
    try:
        title = {'codebits': 'Codebits', 'sapo': 'Notícias'}[name]
    except:
        title = "News"
    return {
        'feed': name,
        'title': title,
        'width': config.width,
        'height': config.height,
        'debug': config.debug
    }
    

@bottle.route('/brand')
@bottle.view('brand')
def brand():
    return {
        'title': 'Codebits',
        'width':  config.width,
        'height': config.height,
        'debug': config.debug
    }


@bottle.route('/shorten/<name:path>')
def shorten(name):
    log.info(name)
    return utils.shorten(name)



