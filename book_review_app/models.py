from django.db import models
from decimal import Decimal

from django.db.models.deletion import CASCADE, PROTECT

class Library(models.Model):
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=256)
    
    latitude = models.DecimalField(max_digits=16, decimal_places=16, default=Decimal(0))
    longitude = models.DecimalField(max_digits=16, decimal_places=16, default=Decimal(0))
    
    from_hour = models.TimeField()
    to_hour = models.TimeField()
    
    
class Author(models.Model):
    name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    middle_name = models.CharField(max_length=32)
    
    birthday = models.DateField(auto_now=False, auto_now_add=False)

    
class Genre(models.Model):
    genre_name = models.CharField(max_length=50)
    
class Book(models.Model):
    title = models.CharField(max_length=50)
    publication_date = models.DateField()
    author = models.ForeignKey(Author, on_delete=CASCADE, related_name="books")
    genre = models.ForeignKey(Genre, on_delete=PROTECT, related_name="books")
    