from book_review_app import models
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from datetime import date


class AuthorSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True)
    class Meta:
        model = models.AuthorUser
        fields = ['name', 'last_name', 'middle_name', 'birthday', 'password', 'username']
        
    def create(self, validated_data):
        user = models.AuthorUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name=validated_data['name'],
            last_name=validated_data['last_name'],
            middle_name=validated_data['middle_name'],
            birthday=validated_data['birthday']
        )

        return user


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre
        fields = ['id', 'name']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Book
        fields = ['id', 'title', 'year', 'author', 'genre', 'publication_date']
            
    
    def validate_year(self, year):
        if year > 0 and year < date.today().year:
            return year
        else:
            raise ValidationError("Incorrect year")
        
            
        
class CommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Comment
        fields = ['author', 'book']

class LibrarySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Library
        fields = ['name', 'address', 'latitude', 'longitude', 'from_hour', 'to_hour']
        
        