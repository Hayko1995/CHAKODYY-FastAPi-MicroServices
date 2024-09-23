import fastapi
from fastapi.testclient import TestClient
import sys
import os.path
from sqlalchemy import StaticPool, create_engine
import sqlalchemy.orm as orm
import json

from sqlalchemy.orm import sessionmaker

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
)


from app import app
import apps.auth.service as services
import db.models as models


client = TestClient(app)


global access_token

def test_chack_api():
    response = client.get("/auth/check_api")
    assert response.status_code == 200
    assert response.json() == {"status": "Connected to API Successfully"}


def test_user_create():
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = client.post("/auth/api/super_users", headers=headers)
    assert response.status_code == 422
    json_str = {
        "name": "string",
        "email": "test@gmail.com",
        "username": "string",
        "password": "string",
    }

    response = client.post(
        "/auth/api/super_users", headers=headers, data=json.dumps(json_str)
    )

    assert response.status_code == 200


def test_get_jwt():

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    json_str = {
        "username": "test@gmail.com",
        "password": "string",
    }

    response = client.post(
        "/auth/api/token", headers=headers, data=json.dumps(json_str)
    )

    assert response.status_code == 200
    access_token = response.json()["access_token"]
    


def buy_coin():

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    json_str = {
        "username": "test@gmail.com",
        "password": "string",
    }

    response = client.post(
        "/coins/api/buy", headers=headers, data=json.dumps(json_str)
    )

    assert response.status_code == 200



# def test_user_delete():
#     headers = {
#         "accept": "application/json",
#         "Content-Type": "application/json",
#     }

#     response = client.post("/coin/api/delete_user", headers=headers)
#     assert response.status_code == 422
#     json_str = {
#         "email": "ab@gmail.com",
#     }

#     response = client.post(
#         "/coin/api/delete_user", headers=headers, data=json.dumps(json_str)
#     )

#     assert response.status_code == 200
