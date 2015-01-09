# -*- coding: utf-8 -*-
from django.db.models.aggregates import Count
from django.http import HttpResponse, Http404, HttpResponseRedirect
from common.decorators import render_to, ajax
from django.shortcuts import get_object_or_404, render_to_response
from hospital.models import Doctor, Hospital, DoctorHospital, Profession
from models import Record
from django.conf import settings

from datetime import time
import datetime
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from hospital.decorators import policy_required
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from signals import new_record_created
from django.template.context import RequestContext
from accounts.models import UserProfile

@login_required
@policy_required
@render_to('onlinereg/index.html')
def index(request):
    doctors = Doctor.objects.filter(doctorhospital__record_enabled=True).order_by('profession').distinct()
    return {'doctors':doctors}

@login_required
@policy_required
@render_to('onlinereg/index.html')
def hospital(request,hospital_id):
    hospital = get_object_or_404(Hospital,pk=hospital_id)
    return {'doctors':hospital.doctors.filter(doctorhospital__record_enabled=True).order_by('profession'),'hospital':hospital, 'page_title':hospital.title}

def get_min_max_time(doctor_in_hospital):
    """ Минимальное и максимальное время, приход, уход """
    min_time = time.max
    max_time = time.min

    for i in doctor_in_hospital.scheduleitem_set.all():
        if i.period_from < min_time:
            min_time = i.period_from
        if i.period_to > max_time:
            max_time = i.period_to
    return min_time, max_time

def get_ticks(min_time, max_time, period_in_minutes,begin_time=None):
    """ Отметки времени для записи """
    ticks = []
    
    t1 = datetime.datetime.strptime(min_time.isoformat(),'%H:%M:%S')
    t2 = datetime.datetime.strptime(max_time.isoformat(),'%H:%M:%S')
    period = datetime.timedelta(0, 0, 0, 0, period_in_minutes)

    if begin_time:
    	bt = datetime.datetime.strptime(begin_time.isoformat(),'%H:%M:%S')
	
	if t1 > bt:
    	    n = bt
	    while True:
                n = n + period
                if n >= t1:
	            t1 = n
                    break
    
    ticks.append(t1)
    
    next_tick = t1

    while True:
        next_tick = next_tick + period
        
        if next_tick <= t2:
            ticks.append(next_tick)
        else:
            break
    
    return ticks


def get_work_days(week_days,doctor_in_hospital):
    """ Вернуть приемные дни с интервалами приема """
    work_days = {}
    
    def update_day(d,period):
        if d in work_days:
            work_days[d].append(period)
        else:
            work_days[d] = [ period, ]
    
    for i in doctor_in_hospital.scheduleitem_set.all():
        for d in week_days:
            # Параметры текущего дня
            even = (d.day % 2 == 0)   # четность
            wd = d.weekday() # день недели
            
            if (i.chet == True or i.chet == False) and i.day != None:
                if even == i.chet and wd == i.day:
                    update_day(d,(i.period_from, i.period_to,))
            elif (i.chet == True or i.chet == False) and i.day == None:
                if even == i.chet:
                    update_day(d,(i.period_from, i.period_to,))
            elif i.chet == None and i.day != None:
                if wd == i.day:
                    update_day(d,(i.period_from, i.period_to,))
    return work_days

def is_work_in_this_datetime(day, t, work_days):
    if day in work_days:
        periods = work_days[day]
        for p in periods:
            if t.time() >= p[0] and t.time() <= p[1]:
                return datetime.datetime(day.year,day.month,day.day,t.hour,t.minute,)

@never_cache
@login_required
@policy_required
def calendar(request, hospital_id, doctor_id):
    
    from_admin = request.GET.get('from_admin',False)
    
    if from_admin:
        template = 'onlinereg/calendar_for_admin.html'
    else:
        template = 'onlinereg/calendar.html'
    
    doctor_in_hospital = get_object_or_404(DoctorHospital, doctor=doctor_id, hospital=hospital_id)

    period_in_minutes = doctor_in_hospital.doctor.profession.time_period
    
    if doctor_in_hospital.scheduleitem_set.all().count() < 1:
        raise Http404
    
    def get_next_week_days(current_date,days=None):
        """ Узнать даты дней на следующей неделе """
        if not days:
            days = 7
        # Узнаем номер дня недели (0-Пн, 6-Вс)
        #wd = current_date.weekday()
        # Делаем дельту в количество дней до понедельника
        #first_day_distance = datetime.timedelta(days=wd)
        # Вычитаем из текущей даты это количество дней, получаем первый день текущей недели., 
        #monday_date = current_date - first_day_distance
        # Создаем дельту на неделю (7 дней)
        week_distance = datetime.timedelta(days=days)
        #Прибавляем к дате первого дня недели эту дельту получаем дату понедельника следующей недели. 
        first_date = current_date + datetime.timedelta(days=1)
        # Прибавляем к дате сл. понедельника еще неделю и получаем понедельник сл.сл.недели. 
        next_next_monday_date = first_date + week_distance
        
        days = []
        d = first_date
        while d < next_next_monday_date:
            days.append(d)
            d = d + datetime.timedelta(days=1)
        
        return days
    
    # Узнаем начальное и конечно время чтобы нарисовать сетку
    min_time, max_time = get_min_max_time(doctor_in_hospital)
    
    # Отметки для оси Y - отметки времени
    ticks = get_ticks(min_time,max_time,period_in_minutes)
    
    # Отметки для оси X - список дат
    
    now = datetime.datetime.now()
    
    today_crit_time = datetime.datetime.strptime(datetime.datetime.today().strftime('%d.%m.%Y')+' 18:30:00','%d.%m.%Y %H:%M:%S')
    
    # вычислить сл. вторник и раст до него
    now_date = datetime.date.today()
    
    if now_date.weekday() in [5,6,] or (now_date.weekday()==4 and now > today_crit_time):
        # Узнаем номер дня недели (0-Пн, 6-Вс)
        wd = now_date.weekday()
        # Делаем дельту в количество дней до понедельника
        first_day_distance = datetime.timedelta(days=wd)
        # Вычитаем из текущей даты это количество дней, получаем первый день текущей недели., 
        monday_date = now_date - first_day_distance
        # Создаем дельту до вторника (7 дней)
        next_next_monday_date = monday_date + datetime.timedelta(days=7)
        delta_until_next_tue =  next_next_monday_date - now_date
        from_date = datetime.date.today() + delta_until_next_tue 
    else:
        if now > today_crit_time:
            from_date = datetime.date.today() + datetime.timedelta(days=1)
        else:
            from_date = datetime.date.today()
    
    if from_admin:
        dates = get_next_week_days(from_date,15)
    else:
        dates = get_next_week_days(from_date,8)
    
    # Все записи на неделю
    records =  Record.active.filter(doctor_in_hospital=doctor_in_hospital).filter(ontime__gte=dates[0]).filter(ontime__lte=dates[-1])
    busy_datetimes = [x.ontime for x in records]
    
    work_days = get_work_days(dates,doctor_in_hospital)
    
    table = []
    
    for t in ticks:
        row = []
        row.append({'is_tick':True,'tick':t.time() })
        for d in dates:
            res = is_work_in_this_datetime(d, t, work_days)
            
            if d.weekday() in [5,6]:
                holiday = True
            else:
                holiday = False 
            
            if res:
                # Есть приемное время, проверим. Есть ли на это время записи.
                
                # Тут конечно жутко, но время уже третий час....
                pacient=''
                pacient_full=''
                pacient_birthday=''
                
                busy = False
                record = None
                
                if res in busy_datetimes:
                    busy = True
                    
                    # I don't know what is it
                    try:
                        record = Record.objects.get(ontime=res,doctor_in_hospital=doctor_in_hospital, canceled=False)
                    except:
                        records = Record.objects.filter(ontime=res, doctor_in_hospital=doctor_in_hospital, canceled=False)
                        records[records.count()-1].delete()
                        
                    pacient = "%s %s.%s." % (record.user.get_profile().surname,record.user.get_profile().name[0],record.user.get_profile().patronymic[0],)
                    pacient_full = "%s" % (record.user.get_profile().fio)
                    pacient_birthday = record.user.get_profile().birth_date
                
                row.append({'holiday':holiday,'is_tick':False,'on_work':True,'ontime':res,'busy':busy,'pacient':pacient,'pacient_full':pacient_full,'pacient_birthday':pacient_birthday,'record':record})
                # жуть кончилась
            else:
                row.append({'holiday':holiday,'is_tick':False, 'on_work':False,'ontime':res,'busy':False,})
        table.append(row)
        
    # для подстветки выходных в шапке
    mod_dates = []
    for d in dates:
        if d.weekday() in [5,6]:
            holiday = True
        else:
            holiday = False
            
        mod_dates.append({'date':d,'holiday':holiday}) 
    
    data = {'dates':dates, 'mod_dates':mod_dates, 'table':table,'ticks':ticks,'doctor_in_hospital':doctor_in_hospital,'page_title':doctor_in_hospital.doctor.name}
    return render_to_response(template,data,context_instance=RequestContext(request))

@never_cache
@ajax
@login_required
def make_record(request):
    if request.user.get_profile().medical_policy_status!=3:
        return HttpResponseRedirect('/')
    
    doctor_in_hospital_id = request.POST.get('doctor_in_hospital')
    record_date = request.POST.get('record_date')
    record_time = request.POST.get('record_time')
    record_first = request.POST.get('record_first')
    
    profile_id = request.POST.get('record_profile',False)
    
    if profile_id:
        profile = UserProfile.objects.get(pk=profile_id)
        user = profile.user
    else:
        user = request.user
    

    if record_first in ['on']:
        record_first = True
    else:
        record_first = False
    
    d_in_h =  get_object_or_404(DoctorHospital, id=int(doctor_in_hospital_id))
    
    dt = datetime.datetime.strptime("%s %s"%(record_date, record_time,),'%d.%m.%Y %H:%M:%S')
    
    if Record.active.filter(doctor_in_hospital = d_in_h, ontime = dt).count() == 0:
        r = Record(user=user, doctor_in_hospital = d_in_h, ontime = dt, first_time = record_first )
        r.save()
        res = 'ok'
        new_record_created.send(sender=None, record=r)
    else:
        res = 'busy'
    
    return {'res':res}

def on_new_record_created(record,*args,**kwargs):
    from mailer import send_mail
    from mailer import mail_managers
    current_site = Site.objects.get_current()
    
    subject = u"Новая запись к врачу"
    subject = ''.join(subject.splitlines())
    message = render_to_string('onlinereg/new_record_created_email.txt', {'site': current_site,'record':record })
    mail_managers(subject, message)

    user_subject = u"Вы записаны к врачу"
    user_subject = ''.join(user_subject.splitlines())
    user_message = render_to_string('onlinereg/new_record_created_email_to_user.txt', {'site': current_site,'record':record })
    
    if record.user.email:
        send_mail(user_subject, user_message, settings.DEFAULT_FROM_EMAIL, [record.user.email,])
    
@never_cache
@render_to('onlinereg/myrecords.html')
@login_required
def myrecords(request):
    myrecords = Record.objects.filter(user=request.user)
    return {'page_title':u'История записей','myrecords':myrecords}

@never_cache
@login_required
def cancel_record(request,record_id):
    record = get_object_or_404(Record, id=record_id)
    record.cancel()
    return HttpResponseRedirect(reverse(myrecords))

new_record_created.connect(on_new_record_created,sender=None)
