from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import HttpResponseRedirect
from django.conf import settings
# Create your views here.
from rest_framework_jwt.utils import jwt_encode_handler, jwt_decode_handler
from jwt.exceptions import ExpiredSignature, InvalidAudience, InvalidIssuer
from django.contrib.auth import get_user_model
from ..game.models import Challenge
from .jwt import jwt_user
import urllib

class TokenView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        client_id = request.POST.get('client_id')
        client_secret = request.POST.get('client_secret')
        code = request.POST.get('code')
        try:
            jwt_decode_handler(code)
        except (ExpiredSignature, InvalidAudience, InvalidIssuer):
            return Response({
                'success': False,
                'error': 'unauthorized',
            }, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'access_token': code, 'refresh_token': '', 'expires_in': 3600}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        auth = request.META.get('HTTP_AUTHORIZATION')
        code = auth.replace('Bearer ', '')
        try:
            payload = jwt_decode_handler(code)
        except (ExpiredSignature, InvalidAudience, InvalidIssuer):
            return Response({
                'success': False,
                'error': 'unauthorized',
            }, status=status.HTTP_401_UNAUTHORIZED)

        if 'uid' in payload:
            User = get_user_model()
            try:
                user = User.objects.get(id=payload['uid'])
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'unauthorized',
                }, status=status.HTTP_401_UNAUTHORIZED)
            return Response({
                'id': '%s/%s' % (payload['gid'], payload['uid']),
                'name': user.username,
                'email': user.email
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                    'id': payload['gid'],
                    'name': payload['gid'],
                    'email': '',
                }, status=status.HTTP_200_OK)


class CodimdView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        note_id = kwargs['noteId']
        try:
            challenge = Challenge.objects.get(codimd=note_id, user=request.user)
        except Challenge.DoesNotExist:
            return Response({
                'success': False,
                'error': 'unauthorized',
            }, status=status.HTTP_401_UNAUTHORIZED)

        callback = '%s?code=%s&redirect_uri=%s' % \
                   (settings.CHATTO_PAD['CODIMD']['SERVER_URL_INT'] + '/auth/oauth2/callback',
                    urllib.parse.quote(jwt_user(str(challenge.game.id), request.user)),
                    urllib.parse.quote(note_id))


        return HttpResponseRedirect(callback)
