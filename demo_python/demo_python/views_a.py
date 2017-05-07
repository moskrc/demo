import json
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from api.serializers import UserSerializer
from core.models import Game
from online.status import CACHE_PREFIX_USER, OnlineStatus, refresh_user, refresh_users_list, CACHE_USERS

User = get_user_model()

class OnlineViewSet(viewsets.ViewSet):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(OnlineViewSet, self).dispatch(*args, **kwargs)


    def list(self, request, game_id):
        game = get_object_or_404(Game, pk=game_id)

        raw = cache.get(CACHE_USERS % game.id) or []

        resp = []
        for r in raw:
            resp.append({'user': {'id': r.user.id, 'username': r.user.username, 'email': r.user.email},
            'game': r.game.id,
            'status': r.status,
            'seen': r.seen,
            'ip': r.ip,
            'session': r.session,
            })

        def date_handler(obj):
            return obj.isoformat() if hasattr(obj, 'isoformat') else obj

        return HttpResponse(json.dumps(resp, default=date_handler), content_type='application/json')


class OnlineListPingViewSet(viewsets.ViewSet):


    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(OnlineListPingViewSet, self).dispatch(*args, **kwargs)

    def create(self, request, game_id):
        game = get_object_or_404(Game, pk=self.kwargs.get('game_id'))

        onlinestatus = cache.get(CACHE_PREFIX_USER % (request.user.pk, game.id))

        if not onlinestatus:
            onlinestatus = OnlineStatus(request, game)
        refresh_user(request, game)
        refresh_users_list(updated=onlinestatus, game_id=game.id)

        return HttpResponse('ok')