from django.db import models
from django.contrib.auth import get_user_model
import uuid

# Create your models here.


class Game(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)             # 唯一标识符
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, editable=False, related_name='game_owner')   # 创建人
    name = models.CharField(max_length=256)                                                 # 比赛名称
    url = models.URLField(default='')                                                       # 比赛地址
    start = models.DateTimeField(null=True)                                                 # 比赛结束时间
    end = models.DateTimeField(null=True)                                                   # 比赛结束时间
    join_code = models.CharField(max_length=256, default='')                                # 邀请码
    codimd = models.CharField(max_length=64)                                                # codimd id
    rocket_chat_id = models.TextField(max_length=64)                                        # rocket_chat id
    rocket_chat_name = models.TextField(max_length=256)                                     # rocket_chat name
    create_time = models.DateTimeField(auto_now_add=True)                                   # 创建时间
    user = models.ManyToManyField(get_user_model(), related_name='game_user')

# class GameMember(models.Model):
#     game = models.ForeignKey(Game, on_delete=models.CASCADE)                                # 参与的游戏
#     user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)                    # 用户
#     create_time = models.DateTimeField(auto_now_add=True)                                   # 创建时间
#
#     class Meta:
#         unique_together = ("game", "user")


class Challenge(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)             # 唯一标识符
    game = models.ForeignKey(Game(), on_delete=models.CASCADE)                              # 属于那个比赛
    name = models.CharField(max_length=256)                                                 # 题目名称
    type = models.CharField(max_length=64)                                                  # 题目种类
    status = models.IntegerField(default=0)                                                 # 状态
    source = models.IntegerField(default=0)                                                 # 分值
    codimd = models.CharField(max_length=64)                                                # codimd id
    hide = models.BooleanField(default=False)                                               # 是否显示
    rocket_chat = models.TextField(max_length=64)                                           # rocket_chat
    rocket_chat_id = models.TextField(max_length=64)                                        # rocket_chat
    create_time = models.DateTimeField(auto_now_add=True)                                   # 创建时间
    user = models.ManyToManyField(get_user_model(), related_name='user')


#class ChallengeMember(models.Model):
#    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)                      # 参与的题目
#    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)                    # 用户
#    create_time = models.DateTimeField(auto_now_add=True)                                   # 创建时间
#
#    class Meta:
#        unique_together = ("challenge", "user")
