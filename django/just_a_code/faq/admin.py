# -*- coding: utf-8
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from django_markdown.admin import MarkdownModelAdmin

from models import Question, Chapter


class QuestionTabInline(admin.TabularInline):
    model = Question


class ChapterAdmin(MPTTModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    inlines = [QuestionTabInline,]


admin.site.register(Chapter, ChapterAdmin)


class QuestionAdmin(MarkdownModelAdmin):
    list_display = ('question', 'is_active', 'is_for_registered_users', 'chapter', 'collapsed')
    search_fields = ['question', 'answer', ]


admin.site.register(Question, QuestionAdmin)

