# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from hospital.models import Hospital, Doctor, DoctorHospital
from common.widgets import CalendarWidget
from high_schools.models import HighSchool
from django.contrib.auth.models import User
import datetime
from datetime import time
from hospital import utils

SMENA = (
         (1,u'Первая',),
         (2,u'Вторая',),
        )

class SearchForm(forms.Form):
    hospital = forms.ChoiceField()
    date = forms.DateField(widget=CalendarWidget)
    smena = forms.ChoiceField(choices=SMENA)
    doctor = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['hospital'].choices = [(h.id, h.title) for h in Hospital.objects.filter(record_enabled=True)]
        
        

        def period_in_smena(smena,period_from,period_to):
            obed = time(12,0,0,)

            if smena == 1 and period_from < obed:
                return True
            
            if smena == 2 and period_to >= obed:
                return True
            
            return False
        
        try:
            hospital =  int(args[0][u'hospital'])
            date =  datetime.datetime.strptime(args[0][u'date'],'%d.%m.%Y')
            smena =  int(args[0][u'smena'])
            
            self.fields['doctor'].choices = utils.doctors_in_building_at_date_and_smena(hospital,date,smena)
        except Exception as e:
            print e        
        
            

class StudentActivitySearchForm(forms.Form):
    high_school = forms.ChoiceField()
    student = forms.ChoiceField()
    date_from = forms.DateField(widget=CalendarWidget)
    date_to = forms.DateField(widget=CalendarWidget)

    def __init__(self, *args, **kwargs):
        high_school_id = kwargs.pop('high_school_id',None)
        
        super(StudentActivitySearchForm, self).__init__(*args, **kwargs)
        self.fields['high_school'].choices = [('', '---------')] + [(h.id, h.title) for h in HighSchool.objects.all()]
        if high_school_id:
            self.fields['student'].choices = [(s.id, s.get_profile().fio) for s in User.objects.filter(profile__high_school__id=high_school_id)]

class ProfessionSearchForm(forms.Form):
    hospital = forms.ChoiceField()
    profession = forms.ChoiceField()
    date_from = forms.DateField(widget=CalendarWidget)
    date_to = forms.DateField(widget=CalendarWidget)

    def __init__(self, *args, **kwargs):
        hospital_id = kwargs.pop('hospital_id',None)
        
        super(ProfessionSearchForm, self).__init__(*args, **kwargs)
        self.fields['hospital'].choices = [('', '---------')] + [(h.id, h.title) for h in Hospital.objects.filter(record_enabled=True)]
        if hospital_id:
            h = Hospital.objects.get(pk=hospital_id)
            professions = set(h.doctorhospital_set.values_list('doctor__profession','doctor__profession__title'))
            self.fields['profession'].choices = [(p[0], p[1]) for p in professions]

class HighSchoolActivitySearchForm(forms.Form):
    high_school = forms.ChoiceField()
    date_from = forms.DateField(widget=CalendarWidget)
    date_to = forms.DateField(widget=CalendarWidget)

    def __init__(self, *args, **kwargs):
        high_school_id = kwargs.pop('high_school_id',None)
        super(HighSchoolActivitySearchForm, self).__init__(*args, **kwargs)
        self.fields['high_school'].choices = [('', '---------')] + [(h.id, h.title) for h in HighSchool.objects.all()]

