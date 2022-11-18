from django.core.management.base import BaseCommand
from ...models import *
from datetime import date
import time
import math


class Command(BaseCommand):
    help = "Add default values to db"
    maxLimit = 1000
    ratio = 100
    userRatio = ratio
    tagRatio = ratio
    questionRatio = ratio * 10
    answerRatio = ratio * 100
    likeRatio = ratio * 200

    def add_arguments(self, parser) -> None:
        parser.add_argument("ratio", nargs=1, type=int)

    def BulkCreate(self, name: str, ratio: int, foo):
        print(f"Start {name}")
        ratioRange = math.ceil(ratio / self.maxLimit)
        for i in range(ratioRange):
            print("    ", i + 1, "/", ratioRange)
            foo(self.maxLimit * i, min(ratio, self.maxLimit * (i + 1)))
        print(f"End {name}")
        print()

    def CreateUser(self) -> models.QuerySet:
        self.BulkCreate(
            "User",
            self.userRatio,
            lambda s, e: User.objects.bulk_create([User(
                id=x + 1,
                username=f"LM{x}",
                password="12345678",
            ) for x in range(s, e)]))
        return User.objects.all()

    def CreateProfile(self) -> models.QuerySet:
        self.BulkCreate(
            "Profile",
            self.userRatio,
            lambda s, e: Profile.objects.bulk_create([Profile(
                id=x + 1,
                avatar=f"img/avatar-{x % 4 + 1}.png",
                user_id=x + 1
            ) for x in range(s, e)]))
        return Profile.objects.all()

    def CreateTag(self) -> models.QuerySet:
        self.BulkCreate(
            "Tag",
            self.tagRatio,
            lambda s, e: Tag.objects.bulk_create([Tag(
                id=x + 1,
                name=f"C+={x}"
            ) for x in range(s, e)]))
        return Tag.objects.all()

    def CreateQuestion(self) -> models.QuerySet:
        self.BulkCreate(
            "Question",
            self.questionRatio,
            lambda s, e: Question.objects.bulk_create([Question(
                id=x + 1,
                title=f"What is C++? {x}",
                text=f"Hey guys, I want to learn C++!!! But I don't know what does it mean((( {x}",
                user_id=x % self.userRatio + 1,
            ) for x in range(s, e)]))

        self.BulkCreate(
            "QuestionTag",
            self.questionRatio,
            lambda s, e: QuestionTag.objects.bulk_create([QuestionTag(
                question_id=x + 1,
                tag_id=x % self.tagRatio + 1
            ) for x in range(s, e)])
        )
        self.BulkCreate(
            "QuestionTag",
            self.questionRatio,
            lambda s, e: QuestionTag.objects.bulk_create([QuestionTag(
                question_id=x + 1,
                tag_id=(x + 1) % self.tagRatio + 1
            ) for x in range(s, e)])
        )

        return Question.objects.all()

    def CreateAnswer(self) -> models.QuerySet:
        self.BulkCreate(
            "Answer",
            self.answerRatio,
            lambda s, e: Answer.objects.bulk_create([Answer(
                id=x + 1,
                text=f"Just use python. lol {x}",
                question_id=x % self.questionRatio + 1,
                user_id=(x + 2) % self.userRatio + 1,
                correct=(x + 2) % 10 == 0
            ) for x in range(s, e)]))
        return Answer.objects.all()

    def CreateQuestionLike(self) -> models.QuerySet:
        self.BulkCreate(
            "QuestionLike",
            self.likeRatio,
            lambda s, e: QuestionLike.objects.bulk_create([QuestionLike(
                id=x + 1,
                status=Like.LIKE if x % 10 else Like.DISLIKE,
                user_id=(x + 4) % self.userRatio + 1,
                question_id=(x + 40) % self.questionRatio + 1
            ) for x in range(s, e)]))
        return QuestionLike.objects.all()

    def CreateAnswerLike(self) -> models.QuerySet:
        self.BulkCreate(
            "AnswerLike",
            self.likeRatio,
            lambda s, e: AnswerLike.objects.bulk_create([AnswerLike(
                id=x + 1,
                status=Like.LIKE if x % 10 else Like.DISLIKE,
                user_id=(x + 4) % self.userRatio + 1,
                answer_id=(x + 40) % self.answerRatio + 1
            ) for x in range(s, e)]))
        return AnswerLike.objects.all()

    def handle(self, *args, **options):
        start_time = time.time()
        ratio = options["ratio"][0]
        self.ratio = options["ratio"][0]
        self.userRatio = ratio
        self.tagRatio = ratio
        self.questionRatio = ratio * 10
        self.answerRatio = ratio * 100
        self.likeRatio = ratio * 200

        print("Ratio", ratio)

        print("Del QuestionTag")
        while QuestionTag.objects.all():
            QuestionTag.objects.all().delete()

        print("Del Tag")
        while Tag.objects.all():
            Tag.objects.all().delete()

        print("Del AnswerLike")
        while AnswerLike.objects.all():
            AnswerLike.objects.all().delete()

        print("Del QuestionLike")
        while QuestionLike.objects.all():
            QuestionLike.objects.all().delete()

        print("Del Answer")
        ansSize = Answer.objects.count()
        for i in range(ansSize, 0, -self.maxLimit):
            Answer.objects.filter(id__gt=i).delete()
        Answer.objects.all().delete()
        # while Answer.objects.all():

        print("Del Question")
        while Question.objects.all():
            Question.objects.all().delete()

        print("Del Profile")
        while Profile.objects.all():
            Profile.objects.all().delete()

        print("Del User")
        while User.objects.all():
            User.objects.all().delete()

        self.CreateUser()
        self.CreateProfile()
        self.CreateTag()
        self.CreateQuestion()
        self.CreateAnswer()
        self.CreateQuestionLike()
        self.CreateAnswerLike()

        print("--- %s seconds ---" % (time.time() - start_time))
