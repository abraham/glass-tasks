import os
from pymongo import MongoClient

import auth

def get():
    '''Create connection to MongoDB'''
    # TODO: add error handling
    uri = os.environ.get('MONGODB_URI')
    connection = MongoClient(uri)
    return connection[uri.split('/')[-1]]


db = get()


def find_profile_by_id(id):
    return db.profiles.find_one({'profile_id': id})


def find_profile_by_session(token):
    return db.profiles.find_one({'session_token': token})


def insert_profile(credentials, transform=True):
    profile = {
        'email': credentials.get('id_token').get('email'),
        'profile_id': credentials.get('id_token').get('id'),
        'credentials': credentials,
        'session_token': auth.generate_secret(),
    }
    db.profiles.insert(profile)
    return profile


def update_profile(old, credentials, transform=True):
    profile = {
        'email': credentials.get('id_token').get('email'),
        'profile_id': credentials.get('id_token').get('id'),
        'credentials': credentials,
        'session_token': auth.generate_secret(),
    }
    db.profiles.update({'_id': old.get('_id')}, profile)
    return profile


def delete_task(id):
    db.tasks.remove({'task_id': id})

def create_task(task, mirror, profile, tasklist={"id":"@default"}):
    item = {
        "task_id": task.get('id'),
        "mirror_id": mirror.get('id'),
        "tasklist_id": tasklist.get('id'),
        "profile_id": profile.get('profile_id'),
    }
    print 'profile', profile
    db.tasks.insert(item)

def find_task(id):
    return db.tasks.find_one({"task_id": id})
    
def find_task_by_mirror(id):
    return db.tasks.find_one({"mirror_id": id})