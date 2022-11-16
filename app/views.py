from django.shortcuts import render

from . import models


def index(request):
    context = models.Context({'page_obj': models.Question.objects.GetPaginatedNew(request)})
    return render(request=request, template_name='index.html', context=context)


def question(request, id: int):
    context = models.Context({
        'question': models.Question.objects.filter(id=id).first(),
        'page_obj': models.Answer.objects.GetPaginated(request, id)})
    return render(request, 'question.html', context=context)


def new_question(request):
    context = models.Context({})
    return render(request, 'new_question.html', context=context)


def hot_questions(request):
    # TODO Get questions by likes
    context = models.Context({'page_obj': models.Question.objects.GetPaginatedNew(request)})
    return render(request=request, template_name='hot_questions.html', context=context)


def tag(request, id: int):
    context = models.Context({
        'page_obj': models.Question.objects.GetPaginatedByTag(request, id),
        'tag': models.Tag.objects.filter(id=id).first()})
    return render(request, 'question_by_tag.html', context=context)


def login(request):
    context = models.Context()
    return render(request, 'login.html', context=context)


def register(request):
    context = models.Context()
    return render(request, 'register.html', context=context)


def settings(request):
    context = models.Context({'profile': models.TEST_PROFILE})
    return render(request, 'settings.html', context=context)
