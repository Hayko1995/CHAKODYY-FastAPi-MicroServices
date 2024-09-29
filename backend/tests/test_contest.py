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
global id


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
    global access_token
    access_token = response.json()["access_token"]


title = "string"
id = 0


def test_create_contest():
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    json_str = {
        "id": -1,
        "title": title,
        "category": "weekly",
        "start_time": "2024-09-29",
        "end_time": "2024-10-29",
        "reward": "USDT",
        "contest_coins": "USDT",
        "trading_balance": "100",
    }

    response = client.post(
        "/contest/contest", headers=headers, data=json.dumps(json_str)
    )

    assert response.status_code == 200


def test_get_contest():
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    response = client.get("/contest/contest", headers=headers)

    assert response.status_code == 200
    print(response.json())
    assert response.json()[0]["title"] == title
    global id
    id = response.json()[0]["id"]


def test_delete_contest():
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    params = {"id": id}

    response = client.delete("/contest/contest", headers=headers, params=params)

    assert response.status_code == 200


def test_user_delete():
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    response = client.post("/auth/api/delete_user", headers=headers)

    assert response.status_code == 200


def test_delete_history():
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    response = client.post("/api/delete_history", headers=headers)
    assert response.status_code == 200


def test_delete_buys():
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    response = client.post("/api/delete_buys", headers=headers)
    assert response.status_code == 200
