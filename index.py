#!/usr/bin/env python3 

import sys
import json
import os
import bottle
from bottle import route, run, template,debug, get, static_file, post, get,request, redirect
from model import files

@route('/index.html')
@route('/')
def showIndex():
    if 'refresh' in request.query and request.query['refresh'] == 'true':
        refresh = True
    else:
        refresh = False
    fileList = files.getFileList(refresh)
    return template('views/index.tpl', fileList=fileList)

@route('/info.html')
def showInfo():
    fileInfo = files.getFileInfo(request.query['file'])

    return template('views/info.tpl', fileInfo=fileInfo)  

@route('/css/<filepath:path>')
def css(filepath):
    print ('looking for {}'.format(filepath))
    return static_file(filepath, root='./css')

@route('/img/<filepath:path>')
def css(filepath):
    print ('looking for {}'.format(filepath))
    return static_file(filepath, root='./img')


@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='./img')

if __name__ == "__main__":

    debug(True)
    app = bottle.app()
    run(app=app, host='0.0.0.0', port=8000)
