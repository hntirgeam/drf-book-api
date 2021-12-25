from django.core.management.base import BaseCommand, CommandParser
from book_review_app.models import AuthorUser, Book, Comment, Genre, Library
import shortuuid
from rest_framework.authtoken.models import Token
from faker import Faker
import random
from django.utils import timezone
from tqdm import tqdm
from datetime import datetime

fake = Faker()

book_genres = [
    "Fantasy",
    "Adventure",
    "Romance",
    "Contemporary",
    "Dystopian",
    "Mystery",
    "Horror",
    "Thriller",
    "Paranormal",
    "Historical fiction",
    "Science Fiction",
    "Children’s",
    "Memoir",
    "Cooking",
    "Art",
    "Self-help / Personal",
    "Development",
    "Motivational",
    "Health",
    "History",
    "Travel",
    "Guide / How-to",
    "Families & Relationships",
]

def create_genres(): 
    Genre.objects.bulk_create([Genre(name=i) for i in book_genres])

def get_new_user_data():
    profile = fake.profile()
    reg_json = {
        "username": profile["username"].join(shortuuid.ShortUUID().random(length=8)), # Faker sometimes creates non-unique usernames. I fixed it. 
        "password": "super_secure_password1337",
        "name": profile["name"].split(" ")[0],
        "last_name": profile["name"].split(" ")[1],
        "birthday": str(profile["birthdate"]),
    }
    return reg_json

def get_new_book_data():
    y = random.randint(1900, 2021)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    
    book_json = {
        "title": fake.text(max_nb_chars=20),
        "publication_date": datetime(y, m, d, tzinfo=timezone.get_current_timezone()),  # fake.date_object(tzinfo=timezone.utc) doesn't work :C
        "year": random.randint(1900, 2021),
    }
    return book_json

class Command(BaseCommand):
    help = 'Creates N number of authors with M number of books with Y number of comments'
    
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--users', type=int, default=500)
        parser.add_argument('--books', type=int, default=5)
        parser.add_argument('--comments', type=int, default=5)
        
        return super().add_arguments(parser)


    def handle(self, *args, **options):
        print("Долго... n^2 всё таки...")
        create_genres()

        genres = Genre.objects.all()
        
        for _ in tqdm(range(options["users"])):
            profile = get_new_user_data()
            user = AuthorUser.objects.create_user(**profile)
            Token.objects.create(user=user)
            Library.objects.create(author=user, name=fake.company(), address=fake.address(), from_hour="9:30", to_hour="21:00")
            
            for _ in range(options["books"]):
                book = get_new_book_data()
                Book.objects.create(author=user, genre=random.choice(genres), **book)
        
        books = Book.objects.all()
        
        for book in tqdm(books):
            for _ in range(options["comments"]):
                _authors = AuthorUser.objects.exclude(id=book.author.id).all()
                comment_creator = random.choice(_authors)
                Comment.objects.create(author=comment_creator, book=book, text=fake.text())
                
        print(F"{options['users']} authors created each with {options['books']}books. Every book now has {options['comments']} comments from random author (excluding book creator)!")