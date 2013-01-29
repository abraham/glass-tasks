print 'tasks'


'''
{
    'kind': 'tasks#taskList',
    'updated': '2013-01-28T22:09:04.000Z',
    'id': 'MDIzNDA2ODUxNjI0NzEyNzExNTU6MzcwMDkwOTQ3OjA',
    'selfLink': 'https://www.googleapis.com/tasks/v1/users/@me/lists/MDIzNDA2ODUxNjI0NzEyNzExNTU6MzcwMDkwOTQ3OjA',
    'title': 'List 2'
}
'''


import httplib2
import oauth2 as oauth
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow


def build_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    
    service = build('tasks', 'v1', http=http)
    
    return service
    
def list_lists(service):
    return service.tasklists().list().execute()


def list_tasks(service, tasklist='@default'):
    return service.tasks().list(tasklist=tasklist).execute()


def create_tasks(service, tasklist='@default'):
    return service.tasks().list(tasklist='@default').execute()


def create_tasks(service, tasklist='@default'):
    return service.tasks().list(tasklist='@default').execute()