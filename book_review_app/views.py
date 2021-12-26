from django.core.exceptions import ObjectDoesNotExist
from rest_framework import response
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from book_review_app.permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly, IsOwnProfileOrReadOnly
from rest_framework import status
from rest_framework.response import Response
from book_review_app import serializers, models


class LogoutView(APIView):
    """
    Simple API View to implement token revoking
    """

    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            return Response({"detail": "Error"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class CreateAuthorViewSet(mixins.CreateModelMixin, GenericViewSet):
    """
                          ^^^^^^^^^^^^^^^^
    Registration ViewSet. Allows only POST
    """

    queryset = models.AuthorUser.objects.all()
    serializer_class = serializers.AuthorSerializer
    permission_classes = [AllowAny]


class AuthorViewSet(ModelViewSet, GenericViewSet):
    queryset = models.AuthorUser.objects.all()
    serializer_class = serializers.AuthorSerializer
    permission_classes = [IsAuthenticated, IsOwnProfileOrReadOnly]
    http_method_names = ["get", "head", "patch"]


class BookViewSet(ModelViewSet, GenericViewSet):
    queryset = models.Book.objects.all()
    serializer_class = serializers.BookSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def create(self, request, *args, **kwargs):
        """
        This section can be moved inside BookSerializer. Somehow I need to deduce genre object by string not by ID (as in PDF)... // Depends on implementations.
        """
        genre_name = request.data.get("genre", None)
        if genre_name:
            genre = models.Genre.objects.filter(name=genre_name).first()
            if genre:
                request.data.update({"author": request.user.id, "genre": genre.id})
                return super().create(request, *args, **kwargs)
            else:
                return Response({"genre": f"{genre_name} not found"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"genre": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["post", "get"],
        detail=True,
        url_path="comments",
        permission_classes=[IsAuthenticated, IsAuthorOrReadOnly],
        serializer_class=serializers.CommentSerializer,
    )
    def comment(self, request: Request, pk: int):
        """
        Allows us create or view a comment(s) by URL like /api/books/<pk>/comments/
        """
        if request.method == "POST":
            request.data.update({"book": pk})
            comment_serializer = self.get_serializer(data=request.data)
            comment_serializer.is_valid(raise_exception=True)
            comment_serializer.save()
            return Response(comment_serializer.data, status.HTTP_201_CREATED)

        if request.method == "GET":
            book = self.get_object()
            book_serializer = serializers.BookSerializer(book)
            comment_serializer = self.get_serializer(book.comments, many=True)
            response = {**book_serializer.data, "comments": comment_serializer.data}
            return Response(response, status=status.HTTP_200_OK)

    @action(
        methods=["put", "patch", "delete", "get"],
        detail=True,
        url_path="comments/(?P<comment_id>[0-9]+)",
        permission_classes=[IsAuthenticated, IsAuthorOrReadOnly],
        serializer_class=serializers.CommentSerializer,
    )
    def edit_or_remove_comment(self, request: Request, pk: int, comment_id: int):
        """
        Allows to edit or delete a comment by URL like /api/books/<pk>/comments/<comment_id>
        """
        if request.method == "DELETE":
            comment = get_object_or_404(models.Comment, id=comment_id)
            self.check_object_permissions(
                request, comment
            )  # As I used self.get_object in previous action I can't overload it. But I can check permission using this method anyways
            comment.delete()
            return Response("Comment deleted", status.HTTP_204_NO_CONTENT)

        if request.method in ["PUT", "PATCH"]:
            comment = get_object_or_404(models.Comment, id=comment_id)
            self.check_object_permissions(request, comment)
            comment_serializer = self.get_serializer(comment, request.data, partial=True)
            comment_serializer.is_valid()
            comment_serializer.save()
            return Response(comment_serializer.data, status.HTTP_200_OK)

        if request.method == "GET":
            comment = get_object_or_404(models.Comment, id=comment_id)
            comment_serializer = self.get_serializer(comment)
            return Response(comment_serializer.data, status=status.HTTP_200_OK)


class GenreViewSet(ModelViewSet, GenericViewSet):
    queryset = models.Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    permission_classes = [
        IsAuthenticated,
        IsAdminOrReadOnly,
    ]  # Assuming that only admin can add new genre (because, hmmm, that's how I see it)

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


class LibraryViewSet(ModelViewSet, GenericViewSet):
    queryset = models.Library.objects.all()
    serializer_class = serializers.LibrarySerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
