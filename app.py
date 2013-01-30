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
    
    get_tasks(tservice, gservice, profile)
    return 'Hello ', profile.get('email'), ' | <a href="/auth/end">logout</a>'


@bottle.post('/notifications')
@bottle.get('/notifications')
def route_notifications():
    body = bottle.request.body.getvalue()
    print 'notification', body
    if body:
        body = json.loads(body)
    
    if body.get('operation') == 'DELETE' and body.get('collection') == 'timeline':
        
        item = models.find_task_by_mirror(body.get('itemId'))
        if not item:
            return '{"status":"error","message":"Not found"}'

        profile = models.find_profile_by_id(item.get('profile_id'))
        credentials = auth.credentials_from_json(profile.get('credentials'))
        tservice = tasks.build_service(credentials)
        gservice = glass.build_service(credentials)

        tasks.delete(tservice, item.get('task_id'))
        get_tasks(tservice, gservice, profile)
    
    if body.get('operation') == 'INSERT' and body.get('collection') == 'timeline':
        
        profile = models.find_profile()
        credentials = auth.credentials_from_json(profile.get('credentials'))
        tservice = tasks.build_service(credentials)
        gservice = glass.build_service(credentials)
        
        mirror = glass.get_item(gservice, body.get('itemId'))
        result = tservice.tasks().insert(tasklist='@default', body={'title':mirror.get('text')}).execute()
        print 'mirror', mirror
        
        
    return '{"status":"ok"}'

def get_tasks(tservice, gservice, profile):
    tasksx = tservice.tasks().list(tasklist='@default').execute()
    for task in tasksx['items'][0:3]:
        in_db = tasks.find_by_id(task.get('id'))
        if not in_db:
            print 'not in db'
            # send notification
            # insert in db
            mirror = glass.create_item(gservice, task['title'])
            models.create_task(task, mirror, profile)
            print 'task', task
            print 'mirror', mirror
    
    mirror = glass.create_item(gservice, 'Tasks')


if os.environ.get('DEBUG', False):
    print '==================================='
    print '==RUNNING WITH DEBUG MODE ENABLED=='
    print '==================================='
    bottle.debug(mode=True)
bottle.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), reloader=True)
