from model_bakery import baker

from rest_framework.test import APIClient, APITestCase
from book_review_app import models
from model_bakery import baker
from pprint import pp
from django.utils import timezone
import random
from datetime import datetime
import pytz


class TestCommentsView(APITestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(models.AuthorUser)
        self.user2 = baker.make(models.AuthorUser)

        genres = baker.make(models.Genre, _quantity=5)

        self.book1 = baker.make(
            models.Book, author=self.user1, genre=random.choice(genres), publication_date=timezone.now()
        )
        self.book2 = baker.make(
            models.Book, author=self.user2, genre=random.choice(genres), publication_date=timezone.now()
        )

        self.comment1 = baker.make(models.Comment, author=self.user1, book=self.book1, text="Всё очень плохорошо")
        self.comment2 = baker.make(models.Comment, author=self.user2, book=self.book1, text="Всё очень плохорошо")

        self.user1_client = APIClient()
        self.user2_client = APIClient()
        self.anon = APIClient()

        self.user1_client.force_authenticate(user=self.user1)
        self.user2_client.force_authenticate(user=self.user2)

        self.comment_data = {
            "text" : "Всё очень плохорошо"
        }

    def test_get_comments_auth(self):
        response = self.user1_client.get(path=f"/api/books/{self.book1.id}/comments/")
        res_json = response.json()["comments"]

        self.assertEqual(response.status_code, 200)

        self.assertIn("id", res_json[0])
        self.assertIn("author", res_json[0])
        self.assertIn("book", res_json[0])
        self.assertIn("text", res_json[0])
        self.assertIn("creation_date", res_json[0])

    def test_retrieve_comment_auth(self):
        response = self.user1_client.get(path=f"/api/books/{self.book1.id}/comments/1/")

        expected_json = {
            "id": self.comment1.id,
            "author": self.comment1.author.id,
            "book": self.comment1.book.id,
            "text": self.comment1.text,
            "creation_date": self.comment1.creation_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        }

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_json)

    def test_get_comments_unauth(self):
        response = self.anon.get(path=f"/api/books/{self.book1.id}/comments/")
        expected_json = {"detail": "Authentication credentials were not provided."}

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, expected_json)

    def test_retrieve_comment_unauth(self):
        response = self.anon.get(path=f"/api/books/{self.book1.id}/comments/1/")
        expected_json = {"detail": "Authentication credentials were not provided."}

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, expected_json)

    def test_create_comment_auth(self):
        comment_id = models.Comment.objects.count() + 1

        response = self.user1_client.post(path=f"/api/books/{self.book1.id}/comments/", data=self.comment_data, format="json")

        expected_json = {
            "id": comment_id, # first 2 was created in setUp func
            "author": self.user1.id,
            "book": self.book1.id,
            "text": self.comment_data["text"],
            "creation_date": models.Comment.objects.get(id=comment_id).creation_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        }
        
        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(response.content, expected_json)

    def test_user_tries_patch_his_comment_data(self):
        patch_data = {"text": "Передумал! Отврасхитительно"}
        response = self.user1_client.patch(path=f"/api/books/{self.book1.id}/comments/{self.comment1.id}/", data=patch_data, format="json")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(patch_data["text"], response.json()["text"])

        comment = models.Comment.objects.get(id=self.comment1.id)
        self.assertEqual(patch_data["text"], comment.text)

    def test_user_tries_patch_others_comment_data(self):
        expected_json = {'detail': 'You do not have permission to perform this action.'}
        patch_data = {"text": "Передумал! Отврасхитительно"}

        response = self.user1_client.patch(path=f"/api/books/{self.book1.id}/comments/{self.comment2.id}/", data=patch_data, format="json")

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, expected_json)

        book = models.Book.objects.get(id=self.book2.id)
        self.assertNotEqual(patch_data["text"], book.title)

    def test_user_tries_delete_his_comment(self):
        response = self.user1_client.delete(path=f"/api/books/{self.book1.id}/comments/{self.comment1.id}/")
        
        self.assertEqual(response.status_code, 204)
        self.assertNotIn(self.comment1, models.Comment.objects.filter(id=self.comment1.id))

    def test_user_tries_delete_others_comment(self):
        expected_json = {'detail': 'You do not have permission to perform this action.'}
        response = self.user1_client.delete(path=f"/api/books/{self.book1.id}/comments/{self.comment2.id}/")

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, expected_json)
