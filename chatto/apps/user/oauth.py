import requests
from django.conf import settings


class Oauth:
    _oauth_authorize = settings.CHATTO_PAD['OAUTH']['SERVER_URL_EXT'] + '/oauth/authorize'
    _oauth_token = settings.CHATTO_PAD['OAUTH']['SERVER_URL_INT'] + '/oauth/token'
    _oauth_profile = settings.CHATTO_PAD['OAUTH']['SERVER_URL_INT'] + '/oauth/userinfo'
    _client_id = settings.CHATTO_PAD['OAUTH']['CLIENT_ID']
    _client_secret = settings.CHATTO_PAD['OAUTH']['CLIENT_SECRET']

    def __init__(self):
        pass

    def user_info(self, code):
        res = requests.get(self._oauth_profile,
                           headers={'Authorization': 'Bearer ' + code}, verify=False)
        if res.status_code == requests.codes.ok:
            return res.json()
        else:
            return False

    def oauth_url(self):
        return "%s?client_id=%s&redirect_uri=%s" % \
               (self._oauth_authorize, self._client_id, settings.CHATTO_PAD['OAUTH']['CALLBACK_URL'])

    def callback(self, code):
        data = {
            'grant_type': 'authorization_code',
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'code': code
        }
        res = requests.post(self._oauth_token, data=data, verify=False)
        if res.status_code == requests.codes.ok:
            return res.json()
        else:
            return False
