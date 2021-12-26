from django.http import response
from model_bakery import baker
import factory
import json
import pytest

from rest_framework.test import APIClient, APITestCase
from django.test import TestCase
from book_review_app import models
from model_bakery import baker
from pprint import pp


class TestAuthorView(APITestCase):
    def setUp(self) -> None:
        self.user1 = baker.make(models.AuthorUser)
        self.user2 = baker.make(models.AuthorUser)

        self.user1_client = APIClient()
        self.user2_client = APIClient()
        self.anon = APIClient()

        self.user1_client.force_authenticate(user=self.user1)
        self.user2_client.force_authenticate(user=self.user2)

    def test_get_authors_auth(self):
        response = self.user1_client.get(path="/api/authors/")
        res_json = response.json()[0]

        self.assertEqual(response.status_code, 200)
        self.assertIn("name", res_json)
        self.assertIn("last_name", res_json)
        self.assertIn("middle_name", res_json)
        self.assertIn("birthday", res_json)
        self.assertIn("username", res_json)

    def test_retrieve_self_author_auth(self):
        response = self.user1_client.get(path=f"/api/authors/{self.user1.id}/")
        expected_json = {
            "id": self.user1.id,
            "name": self.user1.name,
            "last_name": self.user1.last_name,
            "middle_name": self.user1.middle_name,
            "birthday": str(self.user1.birthday),
            "username": self.user1.username,
        }
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_json)
        
    def test_retrieve_other_author_auth(self):
        response = self.user1_client.get(path=f"/api/authors/{self.user2.id}/")
        expected_json = {
            "id": self.user2.id,
            "name": self.user2.name,
            "last_name": self.user2.last_name,
            "middle_name": self.user2.middle_name,
            "birthday": str(self.user2.birthday),
            "username": self.user2.username,
        }
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_json)
        
    def test_retrieve_author_unauth(self):
        response = self.anon.get(path=f"/api/authors/{self.user1.id}/")
        expected_json = {"detail": "Authentication credentials were not provided."}
        
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, expected_json)

    def test_get_authors_unauth(self):
        response = self.anon.get(path="/api/authors/")
        expected_json = {"detail": "Authentication credentials were not provided."}
        
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, expected_json)

    def test_user_tries_patch_his_data(self):
        data = {"name": "Alexander"}
        response = self.user1_client.patch(path=f"/api/authors/{self.user1.id}/", data=data, format="json")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["name"], response.json()["name"])
        
        
    def test_user_tries_patch_others_data(self):
        expected_json = {'detail': 'You do not have permission to perform this action.'}
        patch_data = {"name": "Alexander"}
        
        response = self.user1_client.patch(path=f"/api/authors/{self.user2.id}/", data=patch_data, format="json")
        
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, expected_json)
        
    def test_user_tries_delete_profile(self):
        expected_json = {'detail': 'Method "DELETE" not allowed.'}
        response = self.user1_client.delete(path=f"/api/authors/{self.user1.id}/")
        
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, expected_json)
        
        response = self.user1_client.delete(path=f"/api/authors/{self.user2.id}/")
        
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, expected_json)
        
        
