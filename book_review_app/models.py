from django.db import models
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE, PROTECT
from django.utils import timezone


class AuthorUser(AbstractUser):
    name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    middle_name = models.CharField(max_length=32)

    birthday = models.DateField()
    
    REQUIRED_FIELDS = ['name', 'last_name', 'middle_name', 'birthday']


class Library(models.Model):
    creator = models.ForeignKey(AuthorUser, on_delete=CASCADE, related_name="libraries")
    
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=256)

    latitude = models.DecimalField(max_digits=16, decimal_places=16, default=Decimal(0))
    longitude = models.DecimalField(max_digits=16, decimal_places=16, default=Decimal(0))

    from_hour = models.TimeField()
    to_hour = models.TimeField()


class Genre(models.Model):
    author = models.ForeignKey(AuthorUser, on_delete=CASCADE, related_name="genres")
    name = models.CharField(max_length=50, unique=True)


class Book(models.Model):
    title = models.CharField(max_length=50)
    publication_date = models.DateTimeField(default=timezone.now)
    year = models.IntegerField()
    author = models.ForeignKey(AuthorUser, on_delete=CASCADE, related_name="books")
    genre = models.ForeignKey(Genre, on_delete=PROTECT, related_name="books")


class Comment(models.Model):
    author = models.ForeignKey(AuthorUser, on_delete=CASCADE, related_name="comments")
    book = models.ForeignKey(Book, on_delete=CASCADE, related_name="comments")
    creation_date = models.DateTimeField(default=timezone.now)
