print 'glass'

import json
import httplib2
import oauth2 as oauth
from apiclient.discovery import build_from_document
from oauth2client.client import OAuth2WebServerFlow


def build_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    
    discovery_file = open('glass.v1.rest.json')
    service = build_from_document(discovery_file.read(), http=http)
    discovery_file.close()
    
    return service
    
def insert(service, item):
    return service.timeline().insert(body=item).execute()


def subscribe_to_notifications(service, profile):
    """Subscribe to notifications for the current user.

    Args:
    service: Authorized Glass service.
    collection: Collection to subscribe to (supported values are "timeline"
                and "locations").
    user_token: Opaque token used by the Glassware to identify the user the
                notification pings are sent for (recommended).
    verify_token: Opaque token used by the Glassware to verify that the
                  notification pings are sent by the API (optional).
    callback_url: URL receiving notification pings (must be HTTPS).
    operation: List of operations to subscribe to. Valid values are "UPDATE",
               "INSERT" and "DELETE" or None to subscribe to all.
    """
    subscription = {
        'collection': 'timeline',
        'callbackUrl': 'https://abraham-glass.herokuapp.com/notifications',
        'operation': None,
        'user_token': profile.get('profile_id'),
    }
    return service.subscriptions().insert(body=subscription).execute()


def create_item(service, text):
    item = {
        "text": text + 'f',
        "notification": {"level": "AUDIO_ONLY"},
        "menuItems": [
           {
             "action": "REPLY",
           },
           {
             "action": "DELETE",
           },
           {
             "action": "READ_ALOUD",
           },
       ],
       "bundleId": "f",
    }
    if text == 'Tasks':
        item['creator'] = {
            'displayName': 'Tasks',
            'id': 'GTD',
        }
    mirror = insert(service, item)
    print 'mirror:insert', mirror
    return mirror

def get_item(service, id):
    return service.timeline().get(id=id).execute()
    