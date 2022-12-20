from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict

from . import models


@require_http_methods(["GET", "POST"])
def index(request):
    print(request.user)
    context = models.context({"page_obj": models.Question.objects.GetPaginatedNew(request)})
    return render(request=request, template_name="index.html", context=context)


@require_http_methods(["GET", "POST"])
def question(request, id: int):
    answer_form = models.AnswerForm()
    if request.method == "POST":
        answer_form = models.AnswerForm(request.POST)
        if answer_form.is_valid():
            if answer := answer_form.save(id, request.user):
                return redirect(f"/question/{id}")
            else:
                answer_form.add_error(field=None, error="You are not loged in!")

    context = models.context({
        "question": models.Question.objects.filter(id=id).first(),
        "page_obj": models.Answer.objects.GetPaginated(request, id),
        "form": answer_form})
    return render(request, "question.html", context=context)


@login_required(login_url="login", redirect_field_name="continue")
@require_http_methods(["GET", "POST"])
def new_question(request):
    question_form = models.QuestionForm()
    if request.method == "POST":
        question_form = models.QuestionForm(request.POST)
        if question_form.is_valid():
            if question := question_form.save(request.user):
                return redirect(f"/question/{question.id}")
            else:
                question_form.add_error(field=None, error="Field Errors!")

    context = models.context({"form": question_form})
    return render(request, "new_question.html", context=context)


@require_http_methods(["GET"])
def hot_questions(request):
    context = models.context({"page_obj": models.Question.objects.GetPaginatedHot(request)})
    return render(request=request, template_name="hot_questions.html", context=context)


@require_http_methods(["GET"])
def tag(request, id: int):
    context = models.context({
        "page_obj": models.Question.objects.GetPaginatedByTag(request, id),
        "tag": models.Tag.objects.filter(id=id).first()})
    return render(request, "question_by_tag.html", context=context)


@require_http_methods(["GET", "POST"])
def login(request):
    next = request.GET.get('continue')
    print("GET:", next)

    login_form = models.LoginForm()
    if request.method == "POST":
        login_form = models.LoginForm(request.POST)
        if login_form.is_valid():
            user = auth.authenticate(request, **login_form.cleaned_data)
            if user:
                auth.login(request, user)
                next = request.POST.get("continue", None)
                print("POST:", next)
                return redirect(next if next and next != "None" else reverse("index"))
            else:
                login_form.add_error(field=None, error="Wrong username or password!")

    context = models.context({"form": login_form, "continue": next})
    return render(request, "login.html", context=context)


@login_required(login_url="login", redirect_field_name="continue")
@require_http_methods(["POST"])
def logout(request):
    auth.logout(request)
    next = request.POST.get("continue")
    return redirect(next if next and next != "None" else reverse("index"))


@require_http_methods(["GET", "POST"])
def register(request):
    register_form = models.RegisterForm()
    if request.method == "POST":
        register_form = models.RegisterForm(request.POST)
        if register_form.is_valid():
            if user := register_form.save():
                return redirect(reverse("index"))
            else:
                register_form.add_error(field=None, error="User Error!")

    context = models.context({"form": register_form})
    return render(request, "register.html", context=context)


@login_required(login_url="login", redirect_field_name="continue")
@require_http_methods(["GET", "POST"])
def settings(request):
    settings_form = models.SettingsForm(initial=model_to_dict(request.user))
    if request.method == "POST":
        print("FILES: ", request.FILES)
        settings_form = models.SettingsForm(request.POST, request.FILES, instance=request.user)
        if settings_form.is_valid():
            settings_form.save()
        else:
            print("Settings error!!!!!!!!!!!!!!!!!!!!!!!!")

    context = models.context({"form": settings_form})
    return render(request, "settings.html", context=context)


@login_required(login_url="login", redirect_field_name="continue")
@require_http_methods(["POST"])
def like(request):
    print(request.POST)
    id = request.POST.get("id")
    type = request.POST.get("type")
    itemtype = request.POST.get("itemtype")

    if not id or not type or not itemtype:
        return HttpResponse("Like", status=404)

    db_like_object = None
    if itemtype == "answer":
        if not models.Answer.objects.filter(id=id).first():
            return HttpResponse("Like", status=404)

        db_like_object = models.AnswerLike.objects.filter(answer_id=id).filter(user=request.user.profile).first()
        if not db_like_object:
            db_like_object = models.AnswerLike.objects.create(
                answer_id=id,
                user=request.user.profile,
                status=models.Like.NONE)
    else:   # itemtype == "question"
        if not models.Question.objects.filter(id=id).first():
            return HttpResponse("Like", status=404)

        db_like_object = models.QuestionLike.objects.filter(question_id=id).filter(user=request.user.profile).first()
        if not db_like_object:
            db_like_object = models.QuestionLike.objects.create(
                question_id=id,
                user=request.user.profile,
                status=models.Like.NONE)

    db_like_object.status = models.Like.DISLIKE if type == "dislike" else models.Like.LIKE
    db_like_object.save()

    obj = None
    if itemtype == "answer":
        obj = models.Answer.objects.filter(id=id).first()
    else:   # itemtype == "question"
        obj = models.Question.objects.filter(id=id).first()

    if (obj):
        return JsonResponse({"status": obj.likes})

    return HttpResponse("Like", status=404)


@login_required(login_url="login", redirect_field_name="continue")
@require_http_methods(["POST"])
def correct(request):
    print(request.POST)
    id = request.POST.get("id")
    correct_in = request.POST.get("correct")

    if not id or not correct_in:
        return HttpResponse("Like", status=404)

    print("no abort")

    correct = correct_in == "true"
    print("correct:", correct)

    if answer := models.Answer.objects.filter(id=id).first():
        print("answer")
        question = answer.question
        if question.user == request.user.profile:
            print("question")
            answer.correct = correct
            answer.save()
            return JsonResponse({"correct": correct})

    return HttpResponse("Like", status=404)
