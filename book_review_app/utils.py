from book_review_app.models import Genre
import shortuuid
from faker import Faker
import random
from django.utils import timezone
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