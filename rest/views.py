import json
import os
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files import File
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse

from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

from rest_framework import status, viewsets, parsers, renderers
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from accounts.forms import UserProfileAvatarForm
from analytics.models import DataItem
from api.permissions import IsOwnerOrAdminOnly

from api.serializers import UserSerializer, LevelSerializer,  ScoreSerializer, AuthTokenSerializer, \
    NewUserSerializer, GameSerializer, SettingsSerializer, AnalyticsSerializer, ConfigSerializer, UserSerializerWrite, \
    ServerSerializer, ChangePasswordSerializer, TopUsersSerializer, RankUserSerializer
from core.models import Level, Score, Game, Settings, Config, Server

from renderers import ConfigRenderer

User = get_user_model()

@api_view(('GET',))
def api_root(request):
    return Response({
        'scores': reverse('score-list', request=request),
        'games': reverse('game-list', request=request),
    })


# XXX
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, pk):

        print 'AAAAA'

        file_obj = request.FILES['file']
        user = get_object_or_404(User, pk=pk)

        filename = request.POST.get('flowFilename')

        user.avatar.save(
            filename,
            file_obj
        )
        user.save()
        return HttpResponse(json.dumps({'filename': user.avatar.name}), content_type="application/json")


# XXX
class UserViewSetDetail(UserViewSet):
    permission_classes = (IsOwnerOrAdminOnly,)

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UserSerializerWrite
        else:
            return UserSerializer



# XXX
class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def get_object(self, queryset=None):
        return get_object_or_404(Game, pk=self.kwargs.get('game_id'))


class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    search_fields = ('type', )

    def get_queryset(self):
        queryset = Server.objects.filter(game__pk=self.kwargs.get('game_id'))
        server_type = self.request.QUERY_PARAMS.get('type', None)
        if server_type is not None:
            queryset = queryset.filter(type=server_type)
        return queryset


# XXX
class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

    def get_queryset(self):
        return Level.objects.filter(game__pk=self.kwargs.get('game_id'))

    def get_object(self, queryset=None):
        return get_object_or_404(Level, game__pk=self.kwargs.get('game_id'), pk=self.kwargs.get('level_id'))

    def pre_save(self, obj):
        game = Game.objects.get(pk=self.kwargs.get('game_id'))
        obj.game = game

class ConfigViewSet(viewsets.ModelViewSet):
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer
    renderer_classes = (JSONRenderer, ConfigRenderer)

    def get_queryset(self):
        return Config.objects.filter(game__pk=self.kwargs.get('game_id'))

    def get_object(self, queryset=None):
        return get_object_or_404(Config, game__pk=self.kwargs.get('game_id'), pk=self.kwargs.get('config_id'))

    def pre_save(self, obj):
        game = Game.objects.get(pk=self.kwargs.get('game_id'))
        obj.game = game



class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer

    def get_queryset(self):
        return Score.objects.filter(user__pk=self.request.user.id)

    def get_object(self, queryset=None):
        return get_object_or_404(Score, user__pk=self.request.user.id)


class AnalyticsViewSet(viewsets.ModelViewSet):
    queryset = DataItem.objects.all()
    serializer_class = AnalyticsSerializer

    def get_queryset(self):
        return DataItem.objects.filter(game__pk=self.kwargs.get('game_id'), user__pk=self.request.user.id)

    def get_object(self, queryset=None):
        return get_object_or_404(DataItem, game__pk=self.kwargs.get('game_id'), user__pk=self.request.user.id, pk=self.kwargs.get('pk'))

    def pre_save(self, obj):
        user = self.request.user
        game = Game.objects.get(pk=self.kwargs.get('game_id'))
        obj.game = game
        obj.user = user


class TopUsersViewSet(viewsets.ModelViewSet):
    queryset = Settings.objects.all()
    serializer_class = RankUserSerializer

    def get_queryset(self):
        return Settings.objects.filter(game=self.kwargs.get('game_id')).order_by('rank_by_wins_pre_calculated')[:50]

class TopUsersByGumballsViewSet(viewsets.ModelViewSet):
    queryset = Settings.objects.all()
    serializer_class = RankUserSerializer

    def get_queryset(self):
        return Settings.objects.filter(game=self.kwargs.get('game_id')).order_by('rank_by_gumballs_pre_calculated')[:50]



class SettingsViewSet(viewsets.ModelViewSet):
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer

    def get_queryset(self):
        return Settings.objects.filter(user__pk=self.kwargs.get('user_id'), game__pk=self.kwargs.get('game_id'))

    def get_object(self, queryset=None):
        user = User.objects.get(pk=self.kwargs.get('user_id'))
        game = Game.objects.get(pk=self.kwargs.get('game_id'))
        return Settings.objects.get_or_create(user=user, game=game)[0]


    def pre_save(self, obj):
        user = User.objects.get(pk=self.kwargs.get('user_id'))
        game = Game.objects.get(pk=self.kwargs.get('game_id'))
        obj = Settings.objects.get_or_create(user=user, game=game)[0]



from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
@permission_classes((AllowAny, ))
def api_register(request):
    serialized = NewUserSerializer(data=request.DATA)
    auth_serializer = AuthTokenSerializer(data=request.DATA)

    if serialized.is_valid():

        if auth_serializer.is_valid():
            token, created = Token.objects.get_or_create(user=auth_serializer.object['user'])

            return Response({'token': token.key,
                             'user_id': auth_serializer.object['user'].id,
                            'username': auth_serializer.object['user'].username,
                            'nickname': auth_serializer.object['user'].nickname})
        else:
            username = serialized.init_data['username']

            if User.objects.filter(username=username).exists():
                counter = 0
                while (User.objects.filter(username='%s%s' % (username, counter)).exists()):
                    counter+=1
                generated_username = '%s%s' % (username, counter)
                serialized.data.update({'username': generated_username})
            else:
                generated_username = username


            email = serialized.init_data.get('email', '')
            first_name = serialized.init_data.get('first_name', '')

            try:
                user = User.objects.create_user(username=generated_username,
                                                email=email,
                                                password=serialized.init_data['password'],
                                                site=None, first_name=first_name,
                                                )

                print '*888'
                print user
                print '****'
                serialized.data.update({'token': user.auth_token.key, 'user_id': user.id})
                return Response(serialized.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = (AllowAny,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer
    model = Token

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            role  = {}
            if serializer.object['user'].is_superuser:
                role = {'title':'admin', 'bitMask': 4}
            else:
                role = {'title': 'user', 'bitMask': 2}


            token, created = Token.objects.get_or_create(user=serializer.object['user'])
            return Response({'token': token.key, 'user_id': serializer.object['user'].id,
                'username': serializer.object['user'].username, 'role': role})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


obtain_auth_token = ObtainAuthToken.as_view()


class ChangePassword(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            serializer.object['user'].set_password(serializer.object['new_password'])
            serializer.object['user'].save()

            return Response({'status': 'ok'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


change_password = ChangePassword.as_view()