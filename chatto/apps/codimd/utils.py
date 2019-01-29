import requests
import urllib
from django.conf import settings


def new_note(oauth_code, body):
    session = requests.Session()

    session.get(settings.CHATTO_PAD['CODIMD']['SERVER_URL_INT'] + '/auth/oauth2/callback', params={
        'code': oauth_code
    }, allow_redirects=True)
    r = session.post(settings.CHATTO_PAD['CODIMD']['SERVER_URL_INT'] + '/new', data=body.encode('utf-8'),
                     headers={'Content-Type': 'text/markdown'},
                     allow_redirects=True)
    return urllib.parse.urlparse(r.url).path[1:]
