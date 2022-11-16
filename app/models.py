from django.db import models
from django.contrib.auth.models import User
from django.core.paginator import Paginator, Page


def Paginate(objectsList, request, perPageObjects: int = 10) -> Page:
    paginator = Paginator(objectsList, perPageObjects)
    return paginator.get_page(request.GET.get('page', 1))


class Profile(models.Model):
    class Meta:
        db_table = "profile"

    avatar = models.CharField(max_length=320)
    user = models.ForeignKey(User, models.PROTECT)


class Like(models.Model):
    class Meta:
        db_table = "likes"
        abstract = True

    LIKE = "l"
    DISLIKE = "d"

    STATUSES = [
        (LIKE, "Like"),
        (DISLIKE, "Dislike")]

    status = models.CharField(max_length=1, choices=STATUSES)
    user = models.ForeignKey(Profile, models.PROTECT)


class TagManager(models.Manager):
    def GetTop(self) -> models.QuerySet:
        return self.all().annotate(count=models.Count("question")).order_by("count")[:15]


class Tag(models.Model):
    class Meta:
        db_table = "tag"

    name = models.CharField(max_length=64)

    objects = TagManager()


class QuestionManager(models.Manager):
    def GetPaginatedNew(self, request) -> Page:
        res = Paginate(self.order_by("-craetion_datetime"), request)
        for item in res:
            item.LoadData()
        return res

    def GetPaginatedByTag(self, request, tagId: int) -> Page:
        res = Paginate(self.filter(tag=tagId).order_by("-craetion_datetime"), request)
        for item in res:
            item.LoadData()

        return res


class Question(models.Model):
    class Meta:
        db_table = "question"

    title = models.CharField(max_length=128)
    text = models.TextField()
    craetion_datetime = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(Profile, models.PROTECT)
    tag = models.ManyToManyField(Tag, through='QuestionTag')

    tags = []
    likes = 0
    answers = 0

    def LoadData(self):
        self.tags = self.tag.all()
        # TODO LIKES
        # TODO ANSWERS

    objects = QuestionManager()


class QuestionTag(models.Model):
    class Meta:
        db_table = "question_tag"

    question = models.ForeignKey(Question, models.PROTECT)
    tag = models.ForeignKey(Tag, models.PROTECT)


class QuestionLike(Like):
    class Meta:
        db_table = "question_like"

    question = models.ForeignKey(Question, models.PROTECT)


class AnswerManager(models.Manager):
    def GetPaginated(self, request, questionId: int) -> Page:
        res = Paginate(self.filter(question=questionId).order_by("-craetion_datetime"), request, 5)
        # TODO LIKES
        return res


class Answer(models.Model):
    class Meta:
        db_table = "answer"

    text = models.TextField()
    question = models.ForeignKey(Question, models.PROTECT)
    craetion_datetime = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(Profile, models.PROTECT)
    correct = models.BooleanField(default=False)

    likes = 0

    objects = AnswerManager()


class AnswerLike(Like):
    class Meta:
        db_table = "answer_like"

    answer = models.ForeignKey(Answer, models.PROTECT)


TEST_PROFILE = {
    "id": 0,
    "name": "Mihail",
    "login": "microintex",
    "email": "lm@mail.ru",
    "nickname": "LM",
    "avatar": "img/avatar-4.png",
}


def Context(context=None):
    res = {'tags': Tag.objects.GetTop()}
    if context != None:
        res.update(context)
    return res
