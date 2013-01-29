import bottle
import os
import httplib2
import json
import base64


from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow, AccessTokenCredentials
from oauth2client.tools import run


import auth
import models
import glass


SCOPES = ['https://www.googleapis.com/auth/glass.timeline',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/tasks',
         ]
flow = OAuth2WebServerFlow(client_id=os.environ.get('CLIENT_ID'),
                           client_secret=os.environ.get('CLIENT_SECRET'),
                           scope=' '.join(SCOPES),
                           redirect_uri=os.environ.get('URI') + 'auth/callback',
                           access_type='offline',
                           approval_prompt='force')


@bottle.get('/auth/end')
def get_auth_start():
    bottle.response.delete_cookie('token', path='/')
    bottle.redirect('/')


@bottle.get('/auth/start')
def get_auth_start():
    bottle.redirect(flow.step1_get_authorize_url())


@bottle.get('/auth/callback')
def get_auth_callback():
    '''
    {
        "_module": "oauth2client.client",
        "_class": "OAuth2Credentials",
        "access_token": "ya29.AHES6ZQE6k8Aa4HA-xtb51Rae68X3qGBA4abOuEqBsmLeA",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "invalid": false,
        "client_id": "421542679600.apps.googleusercontent.com",
        "id_token": {
            "aud": "421542679600.apps.googleusercontent.com",
            "cid": "421542679600.apps.googleusercontent.com",
            "iss": "accounts.google.com",
            "id": "109414663835355699455",
            "exp": 1359418206,
            "iat": 1359414306,
            "token_hash": "iJD-fbnWDL02xgSJC38jLA",
            "email": "abraham.williams@glasspioneer.com",
            "hd": "glasspioneer.com",
            "verified_email": "true"
        },
        "client_secret": "kOvjeUtdWWYMfjih0aUXHPb-",
        "token_expiry": "2013-01-29T00:10:07Z",
        "refresh_token": "1/jZ_t3yGGiC99WX8swI8973-D93vY9WbejbvtwyCGzts",
        "user_agent": null
    }
    '''
    if bottle.request.query.get('error', False) or not bottle.request.query.get('code', False):
        return 'ERROR: authorization is required'
    code = bottle.request.query.get('code')
    credentials = flow.step2_exchange(code)
    credentials_json = json.loads(credentials.to_json())
    profile = models.find_profile_by_id(id=credentials_json.get('id_token').get('id'))
    if profile:
        profile = models.update_profile(credentials=credentials_json, old=profile)
    else:
        profile = models.insert_profile(credentials=credentials_json)
    bottle.response.set_cookie('token', profile.get('session_token'), path='/')

    credentials = auth.credentials_from_json(profile.get('credentials'))
    gservice = glass.build_service(credentials)
    print 'subscribing to notifications'
    print glass.subscribe_to_notifications(gservice)

    bottle.redirect('/')


def find_user_from_session(request):
    token = request.get_cookie('token', default=False)
    if not token:
        return False
    profile = models.find_profile_by_session(token=token)
    print 'find_user_from_session', profile
    return profile


def generate_secret():
    return base64.urlsafe_b64encode(os.urandom(64)).replace('=', '')


def credentials_from_json(credentials):
    return AccessTokenCredentials.from_json(json.dumps(credentials))
