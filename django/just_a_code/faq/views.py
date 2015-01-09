# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from faq.models import Question, Chapter


def index(request, chapter_slug=None):
    if chapter_slug:
        chapter = get_object_or_404(Chapter, slug=chapter_slug)
        chapters = chapter.get_children()
        questions = Question.objects.filter(is_active=True, chapter=chapter)
        if not request.user.is_authenticated():
            questions = questions.filter(is_for_registered_users=False)
    else:
        chapter = None
        questions = []
        chapters = Chapter.objects.filter(parent=None)

    return render(request, 'faq/index.html', {'questions': questions, 'chapters': chapters, 'chapter': chapter})

