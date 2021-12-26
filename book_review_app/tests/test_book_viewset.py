import random
from model_bakery import baker
from rest_framework.test import APIClient, APITestCase

from book_review_app import models


class TestBookView(APITestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(models.AuthorUser)
        self.user2 = baker.make(models.AuthorUser)

        genres = baker.make(models.Genre, _quantity=5)

        self.book1 = baker.make(models.Book, author=self.user1, genre=random.choice(genres))
        self.book2 = baker.make(models.Book, author=self.user2, genre=random.choice(genres))

        self.user1_client = APIClient()
        self.user2_client = APIClient()
        self.anon = APIClient()

        self.user1_client.force_authenticate(user=self.user1)
        self.user2_client.force_authenticate(user=self.user2)

        self.book_data = {"title": "Вам и не снилось", "year": 1984, "genre": random.choice([i.name for i in genres])}

    def test_get_books_auth(self):
        response = self.user1_client.get(path="/api/books/")
        res_json = response.json()[0]

        self.assertEqual(response.status_code, 200)
        self.assertIn("title", res_json)
        self.assertIn("year", res_json)
        self.assertIn("author", res_json)
        self.assertIn("genre", res_json)
        self.assertIn("publication_date", res_json)
        self.assertIn("comments", res_json)

    def test_retrieve_book_auth(self):
        response = self.user1_client.get(path=f"/api/books/{self.book1.id}/")

        expected_json = {
            "id": self.book1.id,
            "title": self.book1.title,
            "year": self.book1.year,
            "author": self.book1.author.id,
            "genre": self.book1.genre.id,
            "publication_date": self.book1.publication_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),  # timezones :)))))))))))
            "comments": [],
        }
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_json)

    def test_retrieve_book_library_auth(self):
        response = self.user1_client.get(path=f"/api/books/{self.book2.id}/")
        expected_json = {
            "id": self.book2.id,
            "title": self.book2.title,
            "year": self.book2.year,
            "author": self.book2.author.id,
            "genre": self.book2.genre.id,
            "publication_date": self.book2.publication_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "comments": [],
        }

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_json)

    def test_get_books_unauth(self):
        response = self.anon.get(path=f"/api/books/")
        expected_json = {"detail": "Authentication credentials were not provided."}

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, expected_json)

    def test_retrieve_library_unauth(self):
        response = self.anon.get(path=f"/api/books/{self.book1.id}/")
        expected_json = {"detail": "Authentication credentials were not provided."}

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, expected_json)

    def test_create_book_auth(self):
        book_id = models.Book.objects.count() + 1

        response = self.user1_client.post(path=f"/api/books/", data=self.book_data, format="json")

        expected_json = {
            "id": book_id,
            "title": self.book_data["title"],
            "year": self.book_data["year"],
            "author": self.book1.author.id,
            "genre": models.Genre.objects.get(name=self.book_data["genre"]).id,
            "publication_date": models.Book.objects.get(id=book_id).publication_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "comments": [],
        }

        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(response.content, expected_json)

    def test_user_tries_patch_his_book_data(self):
        patch_data = {"title": "War and Peace"}
        response = self.user1_client.patch(path=f"/api/books/{self.book1.id}/", data=patch_data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(patch_data["title"], response.json()["title"])

        book = models.Book.objects.get(id=self.book1.id)
        self.assertEqual(patch_data["title"], book.title)

    def test_user_tries_patch_others_book_data(self):
        expected_json = {"detail": "You do not have permission to perform this action."}
        patch_data = {"title": "War and Peace"}

        response = self.user1_client.patch(path=f"/api/books/{self.book2.id}/", data=patch_data, format="json")

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, expected_json)

        book = models.Book.objects.get(id=self.book2.id)
        self.assertNotEqual(patch_data["title"], book.title)

    def test_user_tries_delete_his_book(self):
        response = self.user1_client.delete(path=f"/api/books/{self.book1.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertNotIn(self.book1, models.Book.objects.filter(id=self.book1.id))

    def test_user_tries_delete_others_book(self):
        expected_json = {"detail": "You do not have permission to perform this action."}
        response = self.user1_client.delete(path=f"/api/books/{self.book2.id}/")

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, expected_json)
