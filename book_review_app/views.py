from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import mixins
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from book_review_app.permissions import IsAuthorOrReadOnly
from rest_framework import status
from rest_framework.response import Response
from book_review_app import serializers, models


class LogoutView(APIView):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)   

class CreateAuthorView(mixins.CreateModelMixin, GenericViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = serializers.AuthorSerializer
    permission_classes = [AllowAny]

class AuthorViewSet(ModelViewSet, GenericViewSet):
    queryset = models.AuthorUser.objects.all()
    serializer_class = serializers.AuthorSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    http_method_names = ["get", "head", "patch"]
    
    
class BookViewSet(ModelViewSet, GenericViewSet):
    queryset = models.Book.objects.all()
    serializer_class = serializers.BookSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    
    def create(self, request, *args, **kwargs):
        genre_name = request.data.get("genre", None)
        if genre_name:
            genre = models.Genre.objects.filter(name=genre_name).first()
            if genre:
                request.data.update({"author": request.user.id, "genre": genre.id})
                return super().create(request, *args, **kwargs)
            else:
                return Response({"genre": F"{genre_name} not found"}, status=status.HTTP_400_BAD_REQUEST)    
        else:
            return Response({"genre": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    
class GenreViewSet(ModelViewSet, GenericViewSet):
    queryset = models.Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    
    def retrieve(self, request, *args, **kwargs):
        genre = self.get_object()
        books_by_genre = genre.books.all()
        serializer = self.get_serializer(genre)
        b_serializer = serializers.BookSerializer(books_by_genre, many=True)

        response = {
            **serializer.data,
            "books_by_genre": b_serializer.data,
        }
        return Response(response)
