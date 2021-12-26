from django.core.management.base import BaseCommand, CommandParser
from book_review_app.models import AuthorUser, Book, Comment, Genre, Library
from rest_framework.authtoken.models import Token
from faker import Faker
import random
from tqdm import tqdm
from book_review_app import utils

fake = Faker()


class Command(BaseCommand):
    help = "Creates N number of authors with M number of books with Y number of comments"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--users", type=int, required=True)
        parser.add_argument("--books", type=int, required=True)
        parser.add_argument("--comments", type=int, required=True)

        return super().add_arguments(parser)

    def handle(self, *args, **options):
        print("Долго... n^2 всё таки...")
        utils.create_genres()

        genres = Genre.objects.all()
        books = []
        users = []

        for _ in tqdm(range(options["users"])):
            profile = utils.get_new_user_data()
            user = AuthorUser.objects.create_user(**profile)
            users.append(user)
            Token.objects.create(user=user)
            Library.objects.create(author=user, name=fake.company(), address=fake.address(), from_hour="9:30", to_hour="21:00")

            for _ in range(options["books"]):
                book = utils.get_new_book_data()
                books.append(Book.objects.create(author=user, genre=random.choice(genres), **book))

        for book in tqdm(books):
            for _ in range(options["comments"]):
                _authors = AuthorUser.objects.filter(id__in=[u.id for u in users]).exclude(id=book.author.id)
                comment_creator = random.choice(_authors)
                Comment.objects.create(author=comment_creator, book=book, text=fake.text())

        print(
            f"{options['users']} authors created each with {options['books']} books. Every book now has {options['comments']} comments from random author (excluding book creator)!"
        )
