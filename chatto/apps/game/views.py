from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework.generics import ListAPIView
import urllib.parse
from rest_framework import status
from django.conf import settings
import json, time
import random
from .models import Game, Challenge
from rocketchat_API.rocketchat import RocketChat
from .serializers import GameSerializer, ChallengeSerializer
from ..codimd.jwt import jwt_gid, jwt_user
from ..codimd.utils import new_note
from django.forms.models import model_to_dict
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



class GamesView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GameSerializer

    def __init__(self):
        pass

    def get(self, request, *args, **kwargs):
        objects = Game.objects.filter(user=request.user).order_by('-create_time')
        page = self.paginate_queryset(objects)
        serializer = self.get_serializer(page, many=True, hide_fields=['url', 'rocket_chat', 'codimd'])
        _list = serializer.data
        return Response({
            'success': True,
            'games': _list
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):  # 新增一场比赛
        roles = json.loads(request.user.roles)
        if not settings.CHATTO_PAD['ROCKET_CHAT']['MANAGER_ROLE'] in roles:
            return Response({'success': False, 'error': "You don't have permission to create."},
                            status=status.HTTP_403_FORBIDDEN)

        data = JSONParser().parse(request)
        data['owner'] = request.user
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            # 创建 chat channel 并且邀请创建者
            rocket = settings.CHATTO_PAD['ROCKET']

            group_name = "%s_%s" % (time.strftime('%Y-%m-%d', time.localtime()), hex(random.randint(0x10000000, 0xffffffff))[2:])
            group = rocket.groups_create(group_name).json()
            data['rocket_chat_id'] = group['group']['_id']
            data['rocket_chat'] = group['group']['name']
            rocket.groups_set_topic(data['rocket_chat_id'], serializer.data['name'])  # 设置标题
            rocket.groups_invite(group['group']['_id'], request.user.id)              # 邀请用户
            rocket.groups_add_owner(group['group']['_id'], request.user.id)           # 添加owner权限
            serializer = self.get_serializer(data=data)
            serializer.is_valid()
            game = serializer.save()
            game.user.add(request.user)
            # 创建codimd 页面
            body = '''%s
==================
:::info
* Home: http://
* Start: **%s**
* End: **%s**
* Account: user
* Password: ~~passwd~~
%s
:::
''' % (serializer.data['name'].replace('\n', ' '), data['start'].replace('\n', ' '), data['start'].replace('\n', ' '),
        data['message'].replace(':::', ':\::'))
            game.codimd = new_note(jwt_gid(game.id), body)  # 新增 note
            game.save()
            return Response({
                'success': True,
                'game': game.id,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)


class GameView(ListAPIView):
    permission_classes = (IsAuthenticated,)

    def __init__(self):
        self.rocket = settings.CHATTO_PAD['ROCKET']
        self.channel_layer = get_channel_layer()

    def get(self, request, *args, **kwargs):
        if kwargs['cid']:
            self.serializer_class = ChallengeSerializer
            try:
                game = Game.objects.get(id=kwargs['id'], user=request.user)
                challenge = Challenge.objects.get(game=game, id=kwargs['cid'], user=request.user)
            except Game.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Does not exist or does not have access.',
                }, status=status.HTTP_403_FORBIDDEN)
            except Challenge.DoesNotExist:
                try:
                    challenge = Challenge.objects.get(game=game, id=kwargs['cid'])
                except Challenge.DoesNotExist:
                    return Response({
                        'success': False,
                        'error': 'Does not exist or does not have access.',
                    }, status=status.HTTP_403_FORBIDDEN)
                finally:
                    challenge.user.add(request.user)
                    self.rocket.groups_invite(challenge.rocket_chat_id, request.user.id)  # 邀请用户
            serializer = self.get_serializer(challenge, hide_fields=['game', 'hide', 'create_time', 'rocket_chat_id'])
            _list = serializer.data
            return Response({
                'success': True,
                'challenge': _list,
            }, status=status.HTTP_200_OK)

        else:
            self.serializer_class = GameSerializer
            try:
                game = Game.objects.get(id=kwargs['id'], user=request.user)
            except Game.DoesNotExist:
                try:
                    game = Game.objects.get(id=kwargs['id'])
                except Game.DoesNotExist:
                    return Response({
                        'success': False,
                        'error': 'Does not exist or does not have access.',
                    }, status=status.HTTP_403_FORBIDDEN)
                finally:
                    code = request.GET.get('code', '')
                    if game.join_code == '' or code == game.join_code:
                        game.user.add(request.user)
                        self.rocket.groups_invite(game.rocket_chat_id, request.user.id)  # 邀请用户
                    else:  # 没有权限参加这个比赛
                        return Response({
                            'success': False,
                            'error': 'Does not exist or does not have access.',
                        }, status=status.HTTP_403_FORBIDDEN)
            serializer = self.get_serializer(game, hide_fields=['join_code', 'create_time'])
            challenges_object = Challenge.objects.filter(game=game, hide=False)\
                .values('id', 'name', 'type', 'status', 'source').order_by('type', 'create_time')
            _list = serializer.data

            _list['codimdUrl'] = '%s?code=%s&redirect_uri=%s' % \
                (settings.CHATTO_PAD['CODIMD']['SERVER_URL_EXT'] + '/auth/oauth2/callback',
                    urllib.parse.quote(jwt_user(str(game.id), request.user)),
                    urllib.parse.quote(_list['codimd']))
            types = ['web', 'pwn', 'reverse', 'misc', 'crypto']

            for challenge in challenges_object:
                types += [challenge['type'].lower()]
            return Response({
                'success': True,
                'game': _list,
                'owner': request.user.pk == game.owner_id,
                'challenges': challenges_object,
                'types': set(types),
            }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):  # 新增题目
        self.serializer_class = ChallengeSerializer
        try:
            game = Game.objects.get(id=kwargs['id'], user=request.user)
        except Game.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Does not exist or does not have access.',
            }, status=status.HTTP_403_FORBIDDEN)

        data = JSONParser().parse(request)
        data['game'] = game
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            body = '''[%s] %s
==================
- [ ] SOLVED
:::info

:::
''' % (data['type'].replace('\n', ' '), serializer.data['name'].replace('\n', ' '))
            data['codimd'] = new_note(jwt_gid(game.id), body)       # 新增 note

            group_name = "%s_%s_%s" % (time.strftime('%Y-%m-%d', time.localtime()),
                                       data['type'], hex(random.randint(0x10000000, 0xffffffff))[2:])
            group = self.rocket.groups_create(group_name).json()
            self.rocket.groups_set_topic(group['group']['_id'], serializer.data['name'])  # 设置标题
            self.rocket.groups_invite(group['group']['_id'], request.user.id)              # 邀请用户
            self.rocket.groups_add_owner(group['group']['_id'], request.user.id)           # 添加owner权限
            # 公告新题目添加
            message = ":exclamation:New challenge %s online!" % (serializer.data['name'])
            ret = self.rocket.chat_post_message(message, room_id=game.rocket_chat_id).json()

            #self.rocket.
            data['rocket_chat_id'] = group['group']['_id']
            data['rocket_chat'] = group['group']['name']
            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                challenge = serializer.save()
                async_to_sync(self.channel_layer.group_send)(   # 通过ws 广播更新
                    str(serializer.data['game']),
                    {'type': 'new_challenge', 'challenge': {
                        'id': str(challenge.id),
                        'name': challenge.name,
                        'source': challenge.source,
                        'status': challenge.status,
                        'type': challenge.type
                    }}
                )
                return Response({
                    'success': True,
                    'challenge': challenge.id,
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)



    def put(self, request, *args, **kwargs):  # 修改题目信息
        self.serializer_class = ChallengeSerializer
        if kwargs['id'] and kwargs['cid']:
            try:
                game = Game.objects.get(id=kwargs['id'], user=request.user)
                challenge = Challenge.objects.get(game=game, id=kwargs['cid'])
            except (Game.DoesNotExist, Challenge.DoesNotExist):
                return Response({
                    'success': False,
                    'error': 'unauthorized',
                }, status=status.HTTP_401_UNAUTHORIZED)
            data = JSONParser().parse(request)
            d = model_to_dict(challenge)
            d.update(data)
            serializer = self.get_serializer(data=d, instance=challenge)
            if serializer.is_valid():
                challenge = serializer.save()
                async_to_sync(self.channel_layer.group_send)(   # 通过ws 广播更新
                    str(serializer.data['game']),
                    {'type': 'update_challenge', 'challenge': {
                        'id': str(challenge.id),
                        'name': challenge.name,
                        'source': challenge.source,
                        'status': challenge.status,
                        'type': challenge.type
                    }}
                )
                return Response({
                    'success': True,
                    'message': 'Successfully modified.',
                }, status=status.HTTP_200_OK)
            return Response({
                'success': False,
                'message': serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, *args, **kwargs):  # 删除题目
        # 只有创建这个比赛的人才可以删题目
        if kwargs['id'] and kwargs['cid']:
            try:
                game = Game.objects.get(id=kwargs['id'], owner=request.user)
                challenge = Challenge.objects.get(game=game, id=kwargs['cid'])
            except (Game.DoesNotExist, Challenge.DoesNotExist):
                return Response({
                    'success': False,
                    'error': 'Does not exist or is not a admin.',
                }, status=status.HTTP_403_FORBIDDEN)
            challenge.hide = True
            challenge.save()
            self.rocket.groups_archive(challenge.rocket_chat_id)    # 归档掉

            async_to_sync(self.channel_layer.group_send)(  # 通过ws 广播更新
                kwargs['id'],
                {'type': 'delete_challenge', 'challenge': {
                    'id': kwargs['cid'],
                }}
            )

            return Response({
                'success': True,
                'message': 'Successfully deleted.',
            }, status=201)
        else:
            return Response({
                'success': False,
                'message': 'Bad request',
                }, status=status.HTTP_400_BAD_REQUEST)

