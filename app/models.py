from django.contrib.auth.models import User
from django.core.paginator import Page, Paginator
from django.db import models
from django import forms


def paginate(objectsList, request, perPageObjects: int = 10) -> Page:
    paginator = Paginator(objectsList, perPageObjects)
    return paginator.get_page(request.GET.get("page", 1))


###################################################################
######## DB Models ################################################
###################################################################

class Profile(models.Model):
    class Meta:
        db_table = "profile"

    avatar = models.ImageField(null=True, blank=True,
                               default="img/avatar/default.png",
                               upload_to="img/avatar/%Y/%m/%d")
    user = models.OneToOneField(User, models.PROTECT, related_query_name="profile")


class Like(models.Model):
    class Meta:
        abstract = True

    LIKE = 1
    NONE = 0
    DISLIKE = -1

    STATUSES = [
        (LIKE, "Like"),
        (NONE, "None"),
        (DISLIKE, "Dislike")]

    status = models.IntegerField(choices=STATUSES)
    user = models.ForeignKey(Profile, models.PROTECT)


class TagManager(models.Manager):
    def GetTop(self) -> models.QuerySet:
        return self.all().annotate(count=models.Count("question")).order_by("-count")[:15]


class Tag(models.Model):
    class Meta:
        db_table = "tag"

    name = models.CharField(max_length=64)

    objects = TagManager()


class QuestionManager(models.Manager):
    def GetById(self, id: int):
        res = self.filter(id=id).first()
        return res

    def GetPaginatedNew(self, request) -> Page:
        res = paginate(self.order_by("-creation_datetime"), request)
        return res

    def GetPaginatedHot(self, request) -> Page:
        # TODO Get questions by likes
        res = paginate(self.order_by("-creation_datetime")
                       .annotate(likesVar=models.functions.Coalesce(models.Sum('questionlike__status'), 0))
                       .order_by("-likesVar"), request)
        # .annotate(likes=models.Count('questionlike',filter=models.Q(questionlike__status=Like.LIKE))).order_by("likes"))
        return res

    def GetPaginatedByTag(self, request, tagId: int) -> Page:
        res = paginate(self.filter(tag=tagId).order_by("-creation_datetime"), request)

        return res


class QuestionLike(Like):
    class Meta:
        db_table = "question_like"

    question = models.ForeignKey("Question", models.PROTECT)


class Question(models.Model):
    class Meta:
        db_table = "question"

    title = models.CharField(max_length=128)
    text = models.TextField()
    creation_datetime = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(Profile, models.PROTECT)
    tag = models.ManyToManyField(Tag, through="QuestionTag")

    @property
    def tags(self):
        return self.tag.all()

    @property
    def likes(self):
        return QuestionLike.objects.filter(
            question=self).aggregate(
            likes=models.functions.Coalesce(models.Sum("status"), 0))["likes"]

    @property
    def answers(self):
        return Answer.objects.filter(question=self).count()

    objects = QuestionManager()


class QuestionTag(models.Model):
    class Meta:
        db_table = "question_tag"

    question = models.ForeignKey(Question, models.PROTECT)
    tag = models.ForeignKey(Tag, models.PROTECT)


class AnswerManager(models.Manager):
    def GetPaginated(self, request, questionId: int) -> Page:
        res = paginate(self.filter(question=questionId).order_by("-creation_datetime"), request, 5)
        return res


class Answer(models.Model):
    class Meta:
        db_table = "answer"

    text = models.TextField()
    question = models.ForeignKey(Question, models.PROTECT)
    creation_datetime = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(Profile, models.PROTECT)
    correct = models.BooleanField(default=False)

    @property
    def likes(self):
        return AnswerLike.objects.filter(
            answer=self).aggregate(
            likes=models.functions.Coalesce(models.Sum("status"), 0))["likes"]

    objects = AnswerManager()


class AnswerLike(Like):
    class Meta:
        db_table = "answer_like"

    answer = models.ForeignKey(Answer, models.PROTECT)


def context(context=None):
    res = {"tags": Tag.objects.GetTop()}
    if context != None:
        res.update(context)
    return res


###################################################################
######## Form Models ##############################################
###################################################################

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter you username"}),
        label="Username")

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "********"}),
        label="Password")


class RegisterForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter you username"}),
        label="Username")

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Enter you email"}),
        label="Email")

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter you nickname"}),
        label="NickName")

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "********"}),
        label="Password")

    password_check = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "********"}),
        label="Password Check")

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "password", "password_check"]

    def clean(self):
        super().clean()
        password_1 = self.cleaned_data.get("password")
        password_2 = self.cleaned_data.get("password_check")

        if password_1 and password_1 != password_2:
            raise forms.ValidationError("Passwords do not match!")

        return self.cleaned_data

    def save(self):
        self.cleaned_data.pop("password_check")
        user = User.objects.create_user(**self.cleaned_data)

        profile = Profile.objects.create(user=user)
        profile.save()

        return profile


class SettingsForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter you username"}),
        label="Username")

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Enter you email"}),
        label="Email")

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter you nickname"}),
        label="NickName")

    avatar = forms.ImageField(widget=forms.FileInput(attrs={
        "class": "form-control"}),
        label="Avatar",
        required=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name"]

    def save(self):
        avatar = self.cleaned_data.pop("avatar")

        user = super().save()

        profile = user.profile
        if (avatar):
            profile.avatar = avatar
        profile.save()

        return profile


class QuestionForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Question title"}),
        label="Title")

    text = forms.CharField(widget=forms.Textarea(attrs={
        "class": "form-control",
        "rows": "8",
        "placeholder": "Question description"}),
        label="Text")

    tags = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Tags like: tag1; tag2; tag3"}),
        label="NickName")

    class Meta:
        model = Question
        fields = ["title", "text"]

    def clean(self):
        super().clean()

        tags_str = self.cleaned_data.get("tags")
        if not tags_str:
            raise forms.ValidationError("No tags!")

        for tag in tags_str.split(";"):
            if not tag.strip():
                raise forms.ValidationError("Wrong tags format!")

        return self.cleaned_data

    def save(self, user):
        tags_str = self.cleaned_data.pop("tags").strip()
        tags = []
        for tag_name in tags_str.split(";"):
            if db_tag := Tag.objects.filter(name=tag_name.strip()).first():
                tags.append(db_tag)
            else:
                new_db_tag = Tag.objects.create(name=tag_name)
                new_db_tag.save()
                tags.append(new_db_tag)

        question = Question.objects.create(**self.cleaned_data, user=user.profile)
        question.tag.set(tags)

        question.save()
        return question


class AnswerForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={
        "class": "form-control",
        "rows": "4",
        "placeholder": "Question description"}),
        label="Text")

    class Meta:
        model = Answer
        fields = ["text"]

    def clean(self):
        super().clean()

        return self.cleaned_data

    def save(self, question_id, user):
        print(self.cleaned_data)
        if question_id != None and not Question.objects.filter(id=question_id).first():
            return None

        if user and not user.is_authenticated:
            return None
        print("user.is_authenticated", user.is_authenticated)

        print(user)
        print(question_id)
        answer = Answer.objects.create(**self.cleaned_data, user=user.profile, question_id=question_id)
        answer.save()
        return answer
