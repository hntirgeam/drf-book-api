from model_bakery import baker
from rest_framework.test import APIClient, APITestCase

from book_review_app import models


class TestLibraryView(APITestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.user1 = baker.make(models.AuthorUser)
        self.user2 = baker.make(models.AuthorUser)

        self.library1 = baker.make(models.Library, author=self.user1)
        self.library2 = baker.make(models.Library, author=self.user2)

        self.user1_client = APIClient()
        self.user2_client = APIClient()
        self.anon = APIClient()

        self.user1_client.force_authenticate(user=self.user1)
        self.user2_client.force_authenticate(user=self.user2)

        self.library_data = {
            "name": self.library1.name,
            "address": self.library1.address,
            "from_hour": self.library1.from_hour,
            "to_hour": self.library1.to_hour,
        }

    def test_get_libraries_auth(self):
        response = self.user1_client.get(path="/api/libraries/")
        res_json = response.json()[0]

        self.assertEqual(response.status_code, 200)
        self.assertIn("id", res_json)
        self.assertIn("author", res_json)
        self.assertIn("name", res_json)
        self.assertIn("address", res_json)
        self.assertIn("latitude", res_json)
        self.assertIn("longitude", res_json)
        self.assertIn("from_hour", res_json)
        self.assertIn("to_hour", res_json)

    def test_retrieve_library_auth(self):
        response = self.user1_client.get(path=f"/api/libraries/{self.library1.id}/")
        expected_json = {
            "id": self.library1.id,
            "author": self.user1.id,
            "name": self.library1.name,
            "address": self.library1.address,
            "latitude": "0.0000000000000000",
            "longitude": "0.0000000000000000",
            "from_hour": str(self.library1.from_hour),
            "to_hour": str(self.library1.to_hour),
        }

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_json)

    def test_retrieve_other_library_auth(self):
        response = self.user1_client.get(path=f"/api/libraries/{self.library2.id}/")
        expected_json = {
            "id": self.library2.id,
            "author": self.user2.id,
            "name": self.library2.name,
            "address": self.library2.address,
            "latitude": "0.0000000000000000",
            "longitude": "0.0000000000000000",
            "from_hour": str(self.library2.from_hour),
            "to_hour": str(self.library2.to_hour),
        }

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_json)

    def test_retrieve_libraries_unauth(self):
        response = self.anon.get(path=f"/api/libraries/")
        expected_json = {"detail": "Authentication credentials were not provided."}

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, expected_json)

    def test_get_library_unauth(self):
        response = self.anon.get(path=f"/api/libraries/{self.library2.id}/")
        expected_json = {"detail": "Authentication credentials were not provided."}

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, expected_json)

    def test_create_library_auth(self):
        expected_json = {
            "id": models.Library.objects.count() + 1,  # first 2 was created in setUp func
            "author": self.user1.id,
            "name": self.library_data["name"],
            "address": self.library_data["address"],
            "latitude": "0.0000000000000000",
            "longitude": "0.0000000000000000",
            "from_hour": str(self.library_data["from_hour"]),
            "to_hour": str(self.library_data["to_hour"]),
        }

        response = self.user1_client.post(path=f"/api/libraries/", data=self.library_data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(response.content, expected_json)

    def test_user_tries_patch_his_library_data(self):
        patch_data = {"name": "Imeni Lenina"}
        response = self.user1_client.patch(path=f"/api/libraries/{self.library1.id}/", data=patch_data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(patch_data["name"], response.json()["name"])

        library = models.Library.objects.get(id=self.library1.id)
        self.assertEqual(patch_data["name"], library.name)

    def test_user_tries_patch_others_data(self):
        expected_json = {"detail": "You do not have permission to perform this action."}
        patch_data = {"name": "Alexander"}

        response = self.user1_client.patch(path=f"/api/libraries/{self.library2.id}/", data=patch_data, format="json")

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, expected_json)

        library2 = models.Library.objects.get(id=self.library2.id)
        self.assertNotEqual(patch_data["name"], library2.name)

    def test_user_tries_delete_his_library(self):
        response = self.user1_client.delete(path=f"/api/libraries/{self.library1.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertNotIn(self.library1, models.Library.objects.filter(id=self.library1.id))

    def test_user_tries_delete_others_library(self):
        expected_json = {"detail": "You do not have permission to perform this action."}
        response = self.user1_client.delete(path=f"/api/libraries/{self.library2.id}/")

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, expected_json)
