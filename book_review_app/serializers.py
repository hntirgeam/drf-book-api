from book_review_app import models
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from datetime import date


class AuthorSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True)
    class Meta:
        model = models.AuthorUser
        fields = ['id', 'name', 'last_name', 'middle_name', 'birthday', 'password', 'username']
        extra_kwargs = {"middle_name": {"required": False}}
        
    def create(self, validated_data):
        middle_name = validated_data.get('middle_name', None)
        user = models.AuthorUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name=validated_data['name'],
            last_name=validated_data['last_name'],
            middle_name=middle_name,
            birthday=validated_data['birthday']
        )

        return user


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre
        fields = ['id', 'name']      
            
        
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    class Meta:
        model = models.Comment
        fields = ['id', 'author', 'book', 'text', 'creation_date']
        
        
    def create(self, validated_data):
        author = self.context["request"].user
        comment = models.Comment.objects.create(author=author, **validated_data)
        return comment
    
    def get_author(self, obj):
        return F"{obj.author.last_name} {obj.author.name} {obj.author.middle_name}"
    

class BookSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True)
    class Meta:
        model = models.Book
        fields = ['id', 'title', 'year', 'author', 'genre', 'publication_date', 'comments']
            
    
    def validate_year(self, year):
        if year > 0 and year < date.today().year:
            return year
        else:
            raise ValidationError("Incorrect year")

class LibrarySerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    class Meta:
        model = models.Library
        fields = ['id','author', 'name', 'address', 'latitude', 'longitude', 'from_hour', 'to_hour']
        
    def create(self, validated_data):
        author = self.context["request"].user
        library = models.Library.objects.create(author=author, **validated_data)
        return library
        
    def get_author(self, obj):
        return F"{obj.author.last_name} {obj.author.name} {obj.author.middle_name}"
        