from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import status
from django.conf import settings
import rest_framework_jwt.utils
from django.http import HttpResponseRedirect
import json
from .oauth import Oauth
from .models import User
from rest_framework_jwt.settings import api_settings
import datetime

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


class OauthView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def __init__(self):
        self._oauth = Oauth()

    def get(self, request, *args, **kwargs):
        code = request.GET.get('code', False)
        if request.user.pk:
            return Response({
                'success': True,
                'message': 'You are already logged in.'
                }, status=status.HTTP_200_OK
            )
        elif code:
            res = self._oauth.callback(code)
            if not res:
                return Response({'success': False, 'error': 'Authorization code error.'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user_info = self._oauth.user_info(res['access_token'])
                rocket = settings.CHATTO_PAD['ROCKET']
                # rocket_token = rocket.users_create_token(user_id=user_info['sub']).json()  # 重新生成 REST_TOKEN
                rocket_info = rocket.users_info(user_id=user_info['sub']).json()
                try:
                    user = User.objects.get(email=user_info['email'])
                    user.last_login=datetime.datetime.now()
                    user.username = user_info['preffered_username']
                    user.avatar = user_info['picture']
                    user.roles = json.dumps(rocket_info['user']['roles'])
                    user.rocket = user_info['sub']
                except User.DoesNotExist:
                    user = User(
                        id=user_info['sub'],
                        last_login=datetime.datetime.now(),
                        email=user_info['email'],
                        username=user_info['preffered_username'],
                        avatar=user_info['picture'],
                        roles=json.dumps(rocket_info['user']['roles']),
                        rocket=user_info['sub']
                    )

                user.save()  # 更新用户信息

                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
            return Response({
                'success': True,
                'token': token
            }, status=status.HTTP_200_OK)
        return Response({
                'success': False,
                'error': 'Authorization code error.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class UserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if request.user.pk:
            return Response({
                'success': True,
                'message': 'Login successful.'
                }
            )
        return Response({'success': False}, status=status.HTTP_401_UNAUTHORIZED)

def oauth_url(request):
    return HttpResponseRedirect(Oauth().oauth_url())
