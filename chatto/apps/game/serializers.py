from rest_framework import serializers
from chatto.apps.game.models import Game, Challenge
from rest_framework.fields import empty
from django.utils import six
from collections import OrderedDict
from rest_framework.fields import SkipField
import json
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.relations import PKOnlyObject


class BaseSerializer(serializers.Serializer):
    def to_representation(self, instance):
        ret = OrderedDict()
        fields = self._readable_fields
        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue
            if field.field_name in self.hide_fields:
                continue
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)
        return ret

    def __init__(self, instance=None, data=empty, **kwargs):
        self.hide_fields = kwargs.pop('hide_fields', [])
        super(serializers.Serializer, self).__init__(instance=instance, data=data, **kwargs)


class OwnerField(serializers.CharField):
    def to_representation(self, obj):
        if obj.is_anonymous:
            raise serializers.ValidationError('Incorrect user.')
        return obj.id

    def to_internal_value(self, data):
        return data

class GameField(serializers.CharField):
    def to_representation(self, obj):
        return obj.id

    def to_internal_value(self, data):
        return data

class GameSerializer(BaseSerializer):
    id = serializers.CharField(read_only=True)
    owner = OwnerField(write_only=True)
    name = serializers.CharField(max_length=256)
    url = serializers.URLField(allow_blank=True, required=False)
    start = serializers.DateTimeField(allow_null=True, required=False)
    end = serializers.DateTimeField(allow_null=True, required=False)
    join_code = serializers.CharField(max_length=256, allow_blank=True, required=False, write_only=True)
    rocket_chat_id = serializers.CharField(required=False, write_only=True)
    rocket_chat = serializers.CharField(required=False, source='rocket_chat_name')
    create_time = serializers.DateTimeField(read_only=True)
    codimd = serializers.CharField(max_length=64, required=False)

    def create(self, validated_data):
        return Game.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.url = validated_data.get('url', instance.url)
        instance.start = validated_data.get('start', instance.start)
        instance.end = validated_data.get('end', instance.end)
        instance.account = validated_data.get('account', instance.account)
        instance.password = validated_data.get('account', instance.password)
        instance.introduction = validated_data.get('introduction', instance.introduction)
        instance.save()
        return instance

    def validate(self, data):

        return data

class ChallengeSerializer(BaseSerializer):
    id = serializers.CharField(read_only=True)
    game = GameField(required=True)
    name = serializers.CharField(max_length=256)
    type = serializers.CharField(max_length=64)
    status = serializers.IntegerField(required=False)
    source = serializers.IntegerField(required=False)
    codimd = serializers.CharField(max_length=64, required=False)
    hide = serializers.BooleanField(required=False)
    rocket_chat = serializers.CharField(max_length=64, required=False)
    rocket_chat_id = serializers.CharField(max_length=64, required=False)
    create_time = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Challenge.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.type = validated_data.get('type', instance.type)
        instance.source = validated_data.get('source', instance.type)
        instance.status = validated_data.get('status', instance.status)
        instance.hide = validated_data.get('hide', instance.hide)
        instance.save()
        return instance

    def validate(self, data):
        return data
