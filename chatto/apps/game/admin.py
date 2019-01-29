from django.contrib import admin

# Register your models here.
from .models import Game, Challenge

class GameAdmin(admin.ModelAdmin):
    fields = ('name', 'url', 'start', 'end', 'join_code', 'codimd',
              'rocket_chat_id', 'rocket_chat_name', 'user')
    list_display = ('id', 'name', 'url', 'start', 'end', 'join_code', 'create_time')


class ChallengeAdmin(admin.ModelAdmin):
    fields = ('game', 'name', 'type', 'status', 'source', 'codimd', 'hide', 'rocket_chat',
              'rocket_chat_id', 'user')
    list_display = ('id', 'name', 'type', 'status', 'source', 'create_time')

admin.site.register(Game, GameAdmin)
admin.site.register(Challenge, ChallengeAdmin)
