# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect

from chat.models import Message
from concierge.youdo import saveChatLog
from services.models import Task

@staff_member_required
def dashboard(request):
    tasks = Task.objects.all()[:25]
    messages = Message.objects.all().exclude(user=request.user).order_by('-created')[:25]
    return render(request, 'chat/dashboard.html',{'new_tasks':tasks,'new_messages':messages})

@staff_member_required
def dashboard_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST':
        if request.POST.get('send_history',False):

            log = ''

            for m in task.message_set.all():
                log+="\n\n %s %s\n %s" % (m.user.get_full_name(), m.created, m.body)

            try:
                res =  saveChatLog(int(task.youdo_task_id), log)
                if res['IsSuccess']:
                    messages.info(request, u'Сообщения успешно отравлены')
                else:
                    messages.error(request, u'Отправка не удалась. Ответ: %s' % res)
            except Exception as e:
                messages.error(request, u'Отправка не удалась')

    task.message_set.update(is_new=False)
    return render(request, 'chat/dashboard_task.html',{'task':task, 'ajax_updater_url':reverse('dashboard_updater',kwargs={'task_id':task_id}) })

@staff_member_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    return render(request, 'chat/elements/task_info.html', {'task':task})
