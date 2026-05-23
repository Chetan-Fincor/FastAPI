from fastapi import status
from TodoApp.routers.todos import get_db, get_current_user
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("/todos")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == [{
        'complete': False,
        'title': 'LastAPI',
        'description': 'Because its not fast enough!',
        'id': 1,
        'priority': 5,
        'owner_id': 1
    }]


def test_read_one_authenticated(test_todo):
    response = client.get("/todos/todo/1")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        'complete': False,
        'title': 'LastAPI',
        'description': 'Because its not fast enough!',
        'id': 1,
        'priority': 5,
        'owner_id': 1
    }


def test_read_one_authenticated_not_found():
    response = client.get("/todos/todo/999")

    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


def test_create_todo():
    request_data = {
        'title': 'New Todo',
        'description': 'New todo description',
        'priority': 5,
        'complete': False
    }

    response = client.post("/todos/todo", json=request_data)

    assert response.status_code == 201

    db = TestingSessionLocal()

    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model.title == request_data['title']


def test_update_todo(test_todo):
    request_data = {
        'title': 'Updated Todo',
        'description': 'Updated description',
        'priority': 5,
        'complete': False
    }

    response = client.put("/todos/todo/1", json=request_data)

    assert response.status_code == 204

    db = TestingSessionLocal()

    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model.title == 'Updated Todo'


def test_update_todo_not_found():
    request_data = {
        'title': 'Updated Todo',
        'description': 'Updated description',
        'priority': 5,
        'complete': False
    }

    response = client.put("/todos/todo/999", json=request_data)

    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


def test_delete_todo(test_todo):
    response = client.delete("/todos/todo/1")

    assert response.status_code == 204

    db = TestingSessionLocal()

    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model is None


def test_delete_todo_not_found():
    response = client.delete("/todos/todo/999")

    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}