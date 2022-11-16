from django.core.management.base import BaseCommand
from ...models import *
from datetime import date
import time
import math


class Command(BaseCommand):
    help = "Add default values to db"
    maxLimit = 1000
    ratio = 100

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
            self.ratio,
            lambda s, e: User.objects.bulk_create([User(
                username=f"LM{x}",
                password="12345678",
            ) for x in range(s, e)]))
        return User.objects.all()

    def CreateProfile(self, users: models.QuerySet) -> models.QuerySet:
        self.BulkCreate(
            "Profile",
            self.ratio,
            lambda s, e: Profile.objects.bulk_create([Profile(
                avatar=f"img/avatar-{x % 4 + 1}.png",
                user=users[x]
            ) for x in range(s, e)]))
        return Profile.objects.all()

    def CreateTag(self) -> models.QuerySet:
        self.BulkCreate(
            "Tag",
            self.ratio,
            lambda s, e: Tag.objects.bulk_create([Tag(
                name=f"C+={x}"
            ) for x in range(s, e)]))
        return Tag.objects.all()

    def CreateQuestion(self, users: models.QuerySet, tags: models.QuerySet) -> models.QuerySet:
        self.BulkCreate(
            "Question",
            self.ratio * 10,
            lambda s, e: Question.objects.bulk_create([Question(
                title=f"What is C++? {x}",
                text=f"Hey guys, I want to learn C++!!! But I don't know what does it mean((( {x}",
                user=users[x % len(users)],
            ) for x in range(s, e)]))

        questions = Question.objects.all()
        self.BulkCreate(
            "QuestionTag",
            self.ratio * 10,
            lambda s, e: QuestionTag.objects.bulk_create([QuestionTag(
                question=questions[x],
                tag=tags[x % len(tags)]
            ) for x in range(s, e)])
        )
        self.BulkCreate(
            "QuestionTag",
            self.ratio * 10,
            lambda s, e: QuestionTag.objects.bulk_create([QuestionTag(
                question=questions[x],
                tag=tags[(x + 1) % len(tags)]
            ) for x in range(s, e)])
        )

        return Question.objects.all()

    def CreateAnswer(self, users: models.QuerySet, questions: models.QuerySet) -> models.QuerySet:
        self.BulkCreate(
            "Answer",
            self.ratio * 100,
            lambda s, e: Answer.objects.bulk_create([Answer(
                text=f"Just use python. lol {x}",
                question=questions[x % len(questions)],
                user=users[(x + 2) % len(users)],
                correct=(x + 2) % 10 == 0
            ) for x in range(s, e)]))
        return Answer.objects.all()

    def CreateQuestionLike(self, users: models.QuerySet, questions: models.QuerySet) -> models.QuerySet:
        self.BulkCreate(
            "QuestionLike",
            self.ratio * 200,
            lambda s, e: QuestionLike.objects.bulk_create([QuestionLike(
                status=Like.LIKE if x % 10 else Like.DISLIKE,
                user=users[(x + 4) % len(users)],
                question=questions[(x + 40) % len(questions)]
            ) for x in range(s, e)]))
        return QuestionLike.objects.all()

    def CreateAnswerLike(self, users: models.QuerySet, answers: models.QuerySet) -> models.QuerySet:
        self.BulkCreate(
            "AnswerLike",
            self.ratio * 200,
            lambda s, e: AnswerLike.objects.bulk_create([AnswerLike(
                status=Like.LIKE if x % 10 else Like.DISLIKE,
                user=users[(x + 4) % len(users)],
                answer=answers[(x + 40) % len(answers)]
            ) for x in range(s, e)]))
        return AnswerLike.objects.all()

    def handle(self, *args, **options):
        start_time = time.time()
        ratio = options["ratio"][0]
        self.ratio = options["ratio"][0]

        print("Ratio", ratio)

        # QuestionTag.objects.all().delete()
        # Tag.objects.all().delete()
        # AnswerLike.objects.all().delete()
        # Answer.objects.all().delete()
        # QuestionLike.objects.all().delete()
        # Question.objects.all().delete()
        # Profile.objects.all().delete()
        # User.objects.all().delete()

        #users = self.CreateProfile(self.CreateUser())
        #tags = self.CreateTag()
        #questions = self.CreateQuestion(users, tags)
        #answers = self.CreateAnswer(users, questions)
        #questionLikes = self.CreateQuestionLike(users, questions)
        #answerLikes = self.CreateAnswerLike(users, answers)

        print("--- %s seconds ---" % (time.time() - start_time))
