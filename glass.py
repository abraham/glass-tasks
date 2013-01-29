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
    