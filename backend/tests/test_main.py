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

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


models.Base.metadata.create_all(models.engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[services.get_db] = override_get_db

client = TestClient(app)


def test_chack_api():
    response = client.get("/coin/check_api")
    assert response.status_code == 200
    assert response.json() == {"status": "Connected to API Successfully"}


def test_user_create():
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = client.post("/coin/api/users", headers=headers)
    assert response.status_code == 422
    json_str = {
        "name": "string",
        "email": "test@gmail.com",
        "username": "string",
        "password": "string",
    }

    response = client.post(
        "/coin/api/users", headers=headers, data=json.dumps(json_str)
    )

    assert response.status_code == 200


def test_get_jwt():

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    json_str = {
        "name": "test",
        "email": "test@gmail.com",
        "username": "test",
        "password": "password",
    }
    db = orm.Session = fastapi.Depends(services.get_db)

    db_user = services.get_user_by_email_hard(email=json_str["email"], db=override_get_db())
    services.verefy_user(db_user, override_get_db())

    if db_user == None:
        raise ValueError("Value cannot be negative")

    if db_user.is_verified:
        services.verefy_user(db_user, db=db)

    response = client.post(
        "/coin/api/users", headers=headers, data=json.dumps(json_str)
    )

    assert response.status_code == 200
    print(response.json())


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
