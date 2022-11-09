from django.core.paginator import Paginator
from django.shortcuts import render
from . import models

def paginate(objectsList, request, perPageObjects = 10):
    paginator = Paginator(objectsList, perPageObjects)
    return paginator.get_page(request.GET.get('page', 1)) 


def Context(context = None):
    res = { 'tags': models.TEST_TAGS }
    if context != None: 
        res.update(context)
    return res


def index(request):
    context = Context({ 'questions': models.TEST_QUESTIONS, 'page_obj': paginate(models.TEST_QUESTIONS, request) })
    return render(request=request, template_name='index.html', context=context)


def question(request, id: int):
    context = Context({ 'question': models.TEST_QUESTIONS[id], 'answers': models.TEST_ANSWERS })
    return render(request, 'question.html', context=context)


def new_question(request):
    return render(request, 'new_question.html')


def tag(request, id: int):
    paginator = Paginator(models.TEST_QUESTIONS, 5)
    pageNumber = request.GET.get('page', 1)
    page_obj = paginator.get_page(pageNumber) 
    context = Context({ 'questions': models.TEST_QUESTIONS, 'page_obj': paginate(models.TEST_QUESTIONS, request), 'tag': models.TEST_TAGS[id] })
    return render(request, 'question_by_tag.html', context=context)


def login(request):
    context = Context()
    return render(request, 'login.html', context=context)


def register(request):
    context = Context()
    return render(request, 'register.html', context=context)

    
def settings(request):
    context = Context({'profile': models.TEST_PROFILE})
    return render(request, 'settings.html', context=context)
