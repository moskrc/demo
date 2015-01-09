# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
import mptt
from datetime import time

from cms.models import CMSPlugin
from cms.models.fields import PlaceholderField

class Profession(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    time_period = models.IntegerField(_('Time period'))
    
    class Meta:
        verbose_name = u'Профессия'
        verbose_name_plural = u'Профессии'
        ordering = ('title', )
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('profession', kwargs={'id':self.id})
    
class Doctor(models.Model):
    name = models.CharField(u'ФИО', max_length=255)
    profession = models.ForeignKey(Profession)
    active = models.BooleanField(default=True)
    not_active_description = models.CharField(u'Отсутствует по причине', max_length=255, null=True, blank=True)
    
    def record_may_be_in_hospitals(self):
        return self.hospital_set.filter(doctorhospital__record_enabled=True)
    
    class Meta:
        verbose_name = u'Доктор'
        verbose_name_plural = u'Доктора'
        ordering = ('name', )
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('profession', kwargs={'id':self.id})
    

class Hospital(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    doctors = models.ManyToManyField(Doctor,through="DoctorHospital")
    address = models.CharField(u'Адрес', max_length=255)
    telephone = models.CharField(u'Телефон', max_length=255, null=True, blank=True)
    slug = models.SlugField(_('Slug'),unique=True)
    record_enabled = models.BooleanField(u'Запись разрешена', default=False)
    
    class Meta:
        verbose_name = u'Здание'
        verbose_name_plural = u'Здания'
        ordering = ('title', )
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('hospital', kwargs={'id':self.id})
    

class DoctorHospital(models.Model):
    doctor = models.ForeignKey(Doctor)
    hospital = models.ForeignKey(Hospital)
    room = models.CharField(u'Кабинет',max_length=255)
    comment = models.CharField(u'Комментарий',max_length=255,null=True, blank=True)
    record_enabled = models.BooleanField(u'Запись разрешена', default=False)

    def human_schedule_items(self):
        out = []
        for i in self.scheduleitem_set.all().order_by('day'):
            s = i.get_day_display()
            if i.chet!=None:
                if i.chet:
                    s=s+u' (четн)'
                else:
                    s=s+u' (нечетн)'
            s=s+u" с %s по %s" % (i.period_from.strftime("%H:%M"), i.period_to.strftime("%H:%M"),)
            out.append(s)
        return out
    
    def is_work_day(self, d):
        """ День приемный? возвр. смену, 1 или 2 """
        for i in self.scheduleitem_set.all():
            # Параметры текущего дня
            even = (d.day % 2 == 0)   # четность
            wd = d.weekday() # день недели
            
            if (i.chet == True or i.chet == False) and i.day != None:
                if even == i.chet and wd == i.day:
                    return (i.period_from, i.period_to,)
            elif (i.chet == True or i.chet == False) and i.day == None:
                if even == i.chet:
                    return (i.period_from, i.period_to,)
            elif i.chet == None and i.day != None:
                if wd == i.day:
                    return (i.period_from, i.period_to,)
        return False
    
    def period_in_smena(self, smena, period_from, period_to):
        obed = time(12,0,0,)

        if smena == 1 and period_from < obed:
            return True
        
        if smena == 2 and period_to >= obed:
            return True
        
        return False        
        

    class Meta:
        verbose_name = u'Доктор в здании'
        verbose_name_plural = u'Доктора в зданиях'
        ordering = ('doctor__profession', 'doctor__name','hospital__title' )
    
    def __unicode__(self):
        return u"%s [%s]" % (self.doctor, self.hospital)

DAYS = (
        (0,'Понедельник'),
        (1,'Вторник'),
        (2,'Среда'),
        (3,'Четверг'),
        (4,'Пятница'),
        (5,'Суббота'),
        (6,'Воскресенье'),
        )    

class ScheduleItem(models.Model):
    day = models.IntegerField(choices=DAYS,null=True,blank=True)
    chet = models.NullBooleanField()
    period_from = models.TimeField()
    period_to = models.TimeField()
    doctor_in_hospital = models.ForeignKey(DoctorHospital)

    class Meta:
        verbose_name = u'Пункт расписания'
        verbose_name_plural = u'Пункты расписания'
    
    def __unicode__(self):
        return u"DAY %s с %s  по %s" % (self.day, self.period_from, self.period_to)

from django.contrib.auth.models import User

class SchedulePlugin(CMSPlugin):
    hospital = models.CharField(u'Здание', max_length=255)
    show_contact_info = models.BooleanField(u'Отображать контактную информацию',default=False)
    show_comments = models.BooleanField(u'Отображать комментарии к врачам',default=False)
