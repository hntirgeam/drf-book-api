import requests
from faker import Faker
import shortuuid


BASE_URL = "http://127.0.0.1:8000/api/"

fake = Faker()

fake_static_username = "TheBigLebowski" + shortuuid.ShortUUID().random(length=8)
fake_static_password = "super_secure_password1337"


def get_static_user_profile():
    dude_json = {
        "username": fake_static_username,
        "password": fake_static_password,
        "name": "The",
        "last_name": "Dude",
        "birthday": "1998-01-18",
    }
    return dude_json


def test_get_author_registration_returns_method_not_allowed():
    response = requests.get(BASE_URL + "v1/register/")
    assert response.json()["detail"] == 'Method "GET" not allowed.'


def test_put_author_registration_returns_method_not_allowed():
    response = requests.put(BASE_URL + "v1/register/")
    assert response.json()["detail"] == 'Method "PUT" not allowed.'


def test_patch_author_registration_returns_method_not_allowed():
    response = requests.patch(BASE_URL + "v1/register/")
    assert response.json()["detail"] == 'Method "PATCH" not allowed.'


def test_register_obtain_auth_token_revoke_check_access():
    dude = get_static_user_profile()

    response = requests.post(BASE_URL + "v1/register/", json=dude)
    assert response.status_code == 201

    response = requests.post(BASE_URL + "v1/api-token-auth/", json={"username": dude["username"] + "wrong_data", "password": dude["password"] + "wrong_data"})
    assert response.status_code == 400

    response = requests.post(BASE_URL + "v1/api-token-auth/", json={"username": dude["username"], "password": dude["password"]})
    assert response.status_code == 200
    assert "token" in response.json()

    token = response.json()["token"]

    response = requests.get(BASE_URL + "authors/", headers={"Authorization": f"Token {token}"})
    assert response.status_code == 200

    response = requests.post(BASE_URL + "v1/api-token-deauth/", headers={"Authorization": f"Token {token}"})
    assert response.status_code == 200

    response = requests.get(BASE_URL + "authors/", headers={"Authorization": f"Token {token}"})
    assert response.status_code == 401
