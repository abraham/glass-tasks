import bottle
import datetime
import json
import os
import requests
import time
import uuid


import models
import auth
import glass
import tasks


@bottle.get('/')
def get_index():
    profile = auth.find_user_from_session(bottle.request)
    if not profile:
        return '<a href="/auth/start">Sign in with Google+</a>'
    
    
    credentials = auth.credentials_from_json(profile.get('credentials'))
    tservice = tasks.build_service(credentials)
    gservice = glass.build_service(credentials)
    
    tasksx = tservice.tasks().list(tasklist='@default').execute()

    for task in tasksx['items']:
      print task['title']
    
    # tasklists = tasks.list_lists(tservice)
    
    # tasks_from_list = tasks.list_taks(tservice, taskslist['items'][0])
    
    n = {
        "notification": {"level": "AUDIO_ONLY"},
        "text": "Default tasks list",
    }
    print glass.insert(gservice, n)
    
    return 'hello ', profile.get('email'), ' <a href="/auth/end">logout</a>'


@bottle.route('/notifications')
def route_notifications():
    print 'notification', bottle.request.body.getvalue()
    return '{"status":"ok"}'

if os.environ.get('DEBUG', False):
    print '==================================='
    print '==RUNNING WITH DEBUG MODE ENABLED=='
    print '==================================='
    bottle.debug(mode=True)
bottle.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), reloader=True)
