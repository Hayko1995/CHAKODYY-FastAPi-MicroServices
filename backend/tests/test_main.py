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
    global access_token
    access_token = response.json()["access_token"]


def test_buy_coin():
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    json_str = {
        "coin_name": "usdt",
        "coin_count": "100",
    }

    response = client.post("/api/buy", headers=headers, data=json.dumps(json_str))

    json_str = {
        "coin_name": "btc",
        "coin_count": "10",
    }

    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    response = client.post("/api/buy", headers=headers, data=json.dumps(json_str))

    assert response.status_code == 200
    assert response.json() == {"status": "success"}


def test_get_coins():
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    response = client.post("/api/get_coins", headers=headers)
    assert response.status_code == 200

    assert response.json() == {
        "status": "success",
        "coins": [{"USDT": 100.0}, {"BTC": 10.0}],
    }


def test_buy_history():
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    response = client.post("/api/get_buy_history", headers=headers)
    assert response.status_code == 200

    assert response.json() == {
        "status": "success",
        "buys": [{"USDT": 100.0}, {"BTC": 10.0}],
    }


def test_convert_coin_immidiatly():
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    json_str = {"from_coin": "usdt", "to_coin": "btc", "price": 100, "count": 1}

    response = client.post(
        "/api/convert_Immediately", headers=headers, data=json.dumps(json_str)
    )
    assert response.status_code == 200
    assert response.json() == {
        "from_coin": "USDT",
        "to_coin": "BTC",
        "price": 100.0,
        "count": 1.0,
    }


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
