from http import HTTPStatus

from fastapi.testclient import TestClient

from epinga.app import app


def test_root_should_returns_ok_and_hello_epinga():
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello Epinga API!'}
