from django.contrib.auth import get_user_model
from rest_framework import serializers
from core.models import Message, Level, Score

User = get_user_model()

class MessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = ('guid', 'gesture_type', 'data', 'created', 'modified')


class LevelSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.Field()

    class Meta:
        model = Level
        fields = ('guid', 'name', 'data', 'user', 'created', 'modified')
        depth = 0

class ScoreSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.Field()

    class Meta:
        model = Score
        fields = ('user',
                    'username',
                    'deviceID',
                    'action',
                    'name',
                    'time',
                    'speed',
                    'location',
                    'score',
                    'gameID',
                    'game_name',
                    'created', 'modified')
        depth = 0


class UserSerializer(serializers.HyperlinkedModelSerializer):
    levels = LevelSerializer(source='level_set', read_only=True)
    scores = ScoreSerializer(source='score_set', read_only=True)

    class Meta:
        model = User
        fields = ('username', 'levels', 'scores' )
        depth = 1


