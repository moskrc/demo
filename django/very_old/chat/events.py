from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.utils.text import normalize_newlines
from django_socketio import events
from chat.models import Message


@events.on_message(channel="^room-")
def message(request, socket, context, message):
    context["user"] = User.objects.get(pk=message['uid'])

    try:
        user = context["user"]
    except KeyError:
        return

    if message["action"] == "message":
        message["message"] = u"%s"% strip_tags(normalize_newlines(message["message"]).replace('\n', ' '))
        message["name"] = user.get_profile().name
        socket.send_and_broadcast_channel(message)

    Message.objects.create(user=user, task_id=message['room'], body=message['message'])


@events.on_finish(channel="^room-")
def finish(request, socket, context):
    try:
        user = context["user"]
    except KeyError:
        return
